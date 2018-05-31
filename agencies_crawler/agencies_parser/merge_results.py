import pymongo
import pandas as pd
import numpy as np
import datetime

from scrapy.conf import settings
from agencies_parser.utils import get_domain, to_excel


class AgenciesParser(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.raw_collection = db[settings['MONGODB_RAW_COLLECTION']]
        self.merged_collection = db[settings['MONGODB_MERGED_COLLECTION']]

    def pick_one(self, df, label, label_bing=None, label_hubspot=None):
        if not label_bing and not label_hubspot:
            label_bing = '{0}_bing'.format(label)
            label_hubspot = '{0}_hubspot'.format(label)
        return np.where(
            df[label_bing].notna(), df[label_bing], df[label_hubspot])

    def main(self):
        df1 = pd.DataFrame.from_dict(list(
            self.raw_collection.find({'provider': 'bing_partners'})))

        df2 = pd.DataFrame.from_dict(list(
            self.raw_collection.find({'provider': 'hubspot_partners'})))

        for df in [df1, df2]:
            df['domain'] = df['website_url'].map(get_domain)
            df.drop(columns=['_id'], inplace=True)
            df.set_index('domain')

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
            'source_bing',
            'source_hubspot'
        ]
        df4 = df3[unique_columns]

        df4 = df4.rename(columns={
            'location': 'full_address',
            'areas_of_expertise': 'services',
        })

        df4['sources'] = df4.apply(
            lambda row: {'bing': row.source_bing, 'hubspot': row.source_hubspot}, axis=1)

        common_columns = [
            'name',
            'short_address',
            'website_url',
            'industries',
            'budget',  # we may transform this to float
            'logo_url',
            'languages',
        ]

        for column in common_columns:
            df4[column] = self.pick_one(df3, column)

        # Export
        # now = datetime.datetime.now()
        # to_excel(
            # df4, file_name='test_{0}.xlsx'.format(now.strftime('%Y%m%d_%H%M')))

        # Insert in db
        print(df4.info())
        self.merged_collection.insert_many(df4.to_dict('records'))

if __name__ == '__main__':
    instance = AgenciesParser()
    instance.main()
