import pymongo
import pandas as pd
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
        self.collection = db[settings['MONGODB_COLLECTION']]

    def pick_one(self, df, label):
        bing = '{0}_bing'.format(label)
        hubspot = '{0}_hubspot'.format(label)
        return df[bing] if not df[bing].empty else df[hubspot]

    def main(self):
        df1 = pd.DataFrame.from_dict(list(
            self.collection.find({'provider': 'bing_partners'})))
        df2 = pd.DataFrame.from_dict(list(
            self.collection.find({'provider': 'hubspot_partners'})))

        df1['domain'] = df1['website_url'].map(get_domain)
        df1['is_bing_partner'] = True
        df1.set_index('domain')

        df2['domain'] = df2['website_url'].map(get_domain)
        df2['is_hubspot_partner'] = True
        df2.set_index('domain')

        df3 = pd.merge(
            df1, df2, on='domain', how='outer',
            suffixes=('_bing', '_hubspot'))

        unique_columns = [
            'domain',
            'is_bing_partner',
            'is_hubspot_partner',
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
        # df4.set_index('domain')

        common_columns = [
            column.replace('_bing', '') for column in df3.columns if column.endswith('_bing')]

        for column in common_columns:
            df4[column] = self.pick_one(df3, column)

        now = datetime.datetime.now()
        to_excel(
            df4, file_name='test_{0}.xlsx'.format(now.strftime('%Y%m%d_%H%M')))

if __name__ == '__main__':
    instance = AgenciesParser()
    instance.main()
