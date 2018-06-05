import re

import pymongo
import pandas as pd
import numpy as np
import datetime
import pycountry

from scrapy.conf import settings
from agencies_parser.utils import get_domain, to_excel


class AgenciesParser(object):
    """ Agencies Profiles parser """
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.raw_collection = db[settings['MONGODB_RAW_COLLECTION']]
        self.merged_collection = db[settings['MONGODB_MERGED_COLLECTION']]

    def pick_one(self, df, column, label_bing=None, label_hubspot=None):
        """Picks one value in case is repeated on different sources"""
        if not label_bing and not label_hubspot:
            label_bing = '{0}_bing'.format(column)
            label_hubspot = '{0}_hubspot'.format(column)
        return np.where(
            df[label_hubspot].notna(), df[label_hubspot], df[label_bing])
    
    def merge_columns_lists(self, row, column):
        """Merges lists from different sources"""
        label_bing = '{0}_bing'.format(column)
        label_hubspot = '{0}_hubspot'.format(column)

        if isinstance(row[label_bing], list) and isinstance(row[label_hubspot], list):
            return row[label_bing] + row[label_hubspot]
        elif isinstance(row[label_bing], list):
            return row[label_bing]
        elif isinstance(row[label_hubspot], list):
            return row[label_hubspot]
        else:
            return None

    def get_address_components(self, row):
        """ Parse full and short address """
        raw_address = None
        address_dict = {}
        from_full_address = False

        if row.full_address is not np.nan:
            raw_address = row.full_address
            from_full_address = True

        elif row.short_address is not np.nan:
            raw_address = row.short_address

        if raw_address:
            if ',' not in raw_address:
                address_dict['address1'] = raw_address
            else:
                address_componets = raw_address.split(',')
                if len(address_componets) == 4:
                    address_dict['address1'] = address_componets[0]
                    address_dict['address2'] = address_componets[1].strip()
                    address_dict['city'] = address_componets[2].strip().title()
                elif len(address_componets) == 3 and from_full_address:
                    address_dict['address1'] = address_componets[0]
                    address_dict['city'] = address_componets[1].strip().title()
                elif not from_full_address:
                    address_dict['city'] = address_componets[0].strip().title()
            
            # Try to get zip code
            zip_code = re.search(r'(\d{5})([-])?(\d{4})?', raw_address)
            address_dict['zip_code'] = ''.join(match for match in zip_code.groups() if match) if zip_code else None

            state = re.search(r'([A-Z]{2})', raw_address)
            address_dict['state'] = state.group(0) if state else None

            if 'united states' in raw_address.lower():
                address_dict['country'] = 'US'
            address_dict['full_address'] = raw_address
            return address_dict

    def hasNumbers(self, string):
        return any(char.isdigit() for char in string)

    def value_to_float(self, x):
        """ Convert budget string to float """
        if isinstance(x, (float, int)) or x is None:
            return x
        if isinstance(x, str):
            x = x.split(' ')[0]
            x = x.split('–')[0]
            x = x.split('/')[0]
            x = x.replace('$','').replace('+', '').replace(',', '')
            x = ''.join([s for s in x.split() if self.hasNumbers(s)])
        if 'K' in x:
            if len(x) > 1:
                return float(x.replace('K', '')) * 1000
            return 1000.0
        if 'M' in x:
            if len(x) > 1:
                return float(x.replace('M', '')) * 1000000
            return 1000000.0
        return 0.0
    
    def cleanse_language(self, language):
        if language.lower() == 'chinese traditional':
            return 'Chinese'
        if language.lower() == 'greek':
            return 'Mycenaean Greek'
        if language.lower() == 'mandarin':
            return 'Mandarin Chinese'
        if language.lower() == 'cantonese':
            return 'Yue Chinese'
        if language.lower() == 'malay':
            return 'Malay (macrolanguage)'
        if language.lower() == 'kiswahili':
            return 'Swahili (macrolanguage)'
        return language

    def main(self):
        """ Main method to execute """
        df1 = pd.DataFrame.from_dict(list(
            self.raw_collection.find({'provider': 'bing_partners'})))

        df2 = pd.DataFrame.from_dict(list(
            self.raw_collection.find({'provider': 'hubspot_partners'})))

        for df in [df1, df2]:
            df['domain'] = df['website_url'].map(get_domain)
            df.drop(columns=['_id'], inplace=True)
            df.set_index('domain')
            df['min_budget'] = df['budget'].apply(self.value_to_float)

        df3 = pd.merge(
            df1, df2, on='domain', how='outer',
            suffixes=('_bing', '_hubspot'))

        unique_columns = [
            'domain',
            'location',
            'tier',
            'badge',
            'reviews',
            'stars',
            'regions',
            'awards',
            'areas_of_expertise',
            'email',
            'facebook_url',
            'twitter_url',
            'linkedin_url',
            'phone',
            'coordinates',
        ]
        df4 = df3[unique_columns]
        df4 = df4.rename(columns={
            'location': 'full_address',
            'areas_of_expertise': 'services',
            'stars': 'stars_score',
            'reviews': 'reviews_count',
        })

        # Create hashes
        df4['sources'] = df3.apply(
            lambda row: {
                'bing': row.source_bing if row.source_bing is not np.nan else None,
                'hubspot': row.source_bing if row.source_bing is not np.nan else None
            }, axis=1)
        df4['ranking'] = df4.apply(
            lambda row: {
                'badge': row.badge if row.badge is not np.nan else None,
                'tier': row.tier if row.tier is not np.nan else None
            }, axis=1)
        df4['social_urls'] = df4.apply(
            lambda row: {
                'facebook': row.facebook_url if row.facebook_url is not np.nan else None,
                'twitter': row.twitter_url if row.twitter_url is not np.nan else None,
                'linkedin': row.linkedin_url if row.linkedin_url is not np.nan else None
            }, axis=1)
        df4['description'] = df3.apply(
            lambda row: {
                'bing': row.description if row.description is not np.nan else None,
                'hubspot': row.about if row.about is not np.nan else None
            }, axis=1)
        df4['coordinates'] = df3[df3.coordinates.notnull()].apply(
            lambda row: {'lat': float(row.coordinates[0]), 'long': float(row.coordinates[1])}, axis=1)

        common_columns = [
            'name',
            'short_address',
            'website_url',
            'industries',
            'min_budget',
            'logo_url',
        ]

        merge_columns = [
            'languages',
        ]

        for column in common_columns:
            df4[column] = self.pick_one(df3, column)

        for column in merge_columns:
            df4[column] = df3.apply(self.merge_columns_lists, axis=1, column=column)

        # Languages to ISO
        df4['languages'] = df4[df4.languages.notnull()].apply(
            lambda row: [pycountry.languages.lookup(
                self.cleanse_language(language)).alpha_3 for language in row.languages], axis=1)

        # Split address into components
        df4['address'] = df4.apply(self.get_address_components, axis=1)

        # Insert in db
        df4 = df4.where((pd.notnull(df4)), None)
        
        # Drop junk columns
        df4.drop(columns=[
            'badge',
            'tier',
            'facebook_url',
            'twitter_url',
            'linkedin_url',
            'full_address',
            'short_address',
        ], inplace=True)
        
        print(df4.info())
        self.to_database(df4)
        # self.to_csv(df4)

    def to_database(self, df):
        to_write = []
        for item in df.to_dict('records'):
            to_write.append(
                pymongo.UpdateOne(
                    {'domain': item.get('domain')}, {'$set': item},
                    upsert=True))
        self.merged_collection.bulk_write(to_write)

    def to_csv(self, df):
        # Export
        now = datetime.datetime.now()
        to_excel(
            df, file_name='test_{0}.xlsx'.format(now.strftime('%Y%m%d_%H%M')))

if __name__ == '__main__':
    instance = AgenciesParser()
    instance.main()
