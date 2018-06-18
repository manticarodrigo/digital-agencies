from functools import reduce

import pymongo
import pandas as pd
import numpy as np

from scrapy.utils.project import get_project_settings
from agencies_parser.utils import to_excel

SETTINGS = get_project_settings()

from .bing_parser import BingParser
from .hubspot_parser import HubspotParser
from .google_parser import GoogleParser

class MergeParser(object):
    """ Agencies Profiles parser """

    # Top elements have more priority
    priority_order = {
        'google',
        'hubspot',
        'bing',
    }

    unique_key = 'domain'

    def __init__(self):
        self.connection = pymongo.MongoClient(
            SETTINGS['MONGODB_SERVER'],
            SETTINGS['MONGODB_PORT']
        )
        db = self.connection[SETTINGS['MONGODB_DB']]
        self.raw_collection = db[SETTINGS['MONGODB_RAW_COLLECTION']]
        self.merged_collection = db[SETTINGS['MONGODB_MERGED_COLLECTION']]

    def merge(self):
        bing_df = pd.DataFrame.from_dict(BingParser().parse())
        hubspot_df = pd.DataFrame.from_dict(HubspotParser().parse())
        google_df = pd.DataFrame.from_dict(GoogleParser().parse())

        print(bing_df.info())
        print(hubspot_df.info())
        print(google_df.info())

        df = bing_df.merge(
            hubspot_df, on=self.unique_key, how='outer').merge(
            google_df, on=self.unique_key, how='outer')

        print(df.info())

    def to_database(self, df):
        to_write = []
        for item in df.to_dict('records'):
            to_write.append(
                pymongo.UpdateOne(
                    {'domain': item.get('domain')}, {'$set': item},
                    upsert=True))
        self.merged_collection.bulk_write(to_write)
        self.connection.close()

if __name__ == '__main__':
    instance = MergeParser()
    instance.merge()
