import pymongo
import pandas as pd
import numpy as np
import datetime
import usaddress

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

    def pick_one(self, df, label, label_bing=None, label_hubspot=None):
        """Picks one value in case is repeated on different sources"""
        if not label_bing and not label_hubspot:
            label_bing = '{0}_bing'.format(label)
            label_hubspot = '{0}_hubspot'.format(label)
        return np.where(
            df[label_bing].notna(), df[label_bing], df[label_hubspot])

    def get_address_components(self, row):
        """ Parse full and short address """
        raw_address = None
        address_dict = {}

        if row.full_address is not np.nan:
            raw_address = row.full_address
        elif row.short_address is not np.nan:
            raw_address = row.short_address
        
        tag_mapping = {
            'AddressNumber': 'address1',
            'StreetName': 'address1',
            'StreetNamePreDirectional': 'address1',
            'StreetNamePreModifier': 'address1',
            'StreetNamePreType': 'address1',
            'StreetNamePostDirectional': 'address1',
            'StreetNamePostModifier': 'address1',
            'StreetNamePostType': 'address1',
            'CornerOf': 'address1',
            'IntersectionSeparator': 'address1',
            'LandmarkName': 'address1',
            'USPSBoxGroupID': 'address1',
            'USPSBoxGroupType': 'address1',
            'USPSBoxID': 'address1',
            'USPSBoxType': 'address1',
            'BuildingName': 'address2',
            'OccupancyType': 'address2',
            'OccupancyIdentifier': 'address2',
            'SubaddressIdentifier': 'address2',
            'SubaddressType': 'address2',
            'PlaceName': 'city',
            'StateName': 'state',
            'ZipCode': 'zip_code',
            'CountryName': 'country',
        }

        try:
            if raw_address:
                address, address_type = usaddress.tag(
                    raw_address, tag_mapping)
                address_dict = dict(address)
        except:
            pass
        
        return (
            address_dict.get('address1'),
            address_dict.get('city'),
            address_dict.get('state'),
            address_dict.get('zip_code'),
            address_dict.get('country')
        )

    def hasNumbers(self, string):
        return any(char.isdigit() for char in string)

    def value_to_float(self, x):
        """ Convert budget string to float """
        if type(x) == float or type(x) == int or x is None:
            return x
        if type(x) == str:
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
        })

        # Create hashes
        df4['sources'] = df3.apply(
            lambda row: {'bing': row.source_bing, 'hubspot': row.source_hubspot}, axis=1)
        df4['ranking'] = df4.apply(
            lambda row: {'badge': row.badge, 'tier': row.tier}, axis=1)
        df4['social_urls'] = df4.apply(
            lambda row: {'facebook': row.facebook_url, 'twitter': row.twitter_url, 'linkedin': row.linkedin_url}, axis=1)

        # Drop columns
        df4.drop(columns=['badge', 'tier', 'facebook_url', 'twitter_url', 'linkedin_url'], inplace=True)

        common_columns = [
            'name',
            'short_address',
            'website_url',
            'industries',
            'budget',
            'min_budget',
            'logo_url',
            'languages',
        ]

        for column in common_columns:
            df4[column] = self.pick_one(df3, column)

        # Split address
        df4['address'], df4['city'], df4['state'], \
            df4['zip_code'], df4['country'] = zip(
                *df4.apply(self.get_address_components, axis=1))

        # Insert in db
        df4 = df4.where((pd.notnull(df4)), None)
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
