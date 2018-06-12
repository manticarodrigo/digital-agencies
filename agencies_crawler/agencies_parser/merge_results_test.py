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

    def main(self):
        """ Main method to execute """
        df1 = pd.DataFrame.from_dict(list(
            self.raw_collection.find({'provider': 'bing_partners'})))

        df2 = pd.DataFrame.from_dict(list(
            self.raw_collection.find({'provider': 'hubspot_partners'})))
        
        df3 = pd.DataFrame.from_dict(list(
            self.raw_collection.find({'provider': 'google_partners'})))

        for df in [df1, df2]:
            df['domain'] = df['website_url'].map(get_domain)
            df.drop(columns=['_id'], inplace=True)
            df.set_index('domain')

        df4 = pd.merge(
            df1, df2, df3, on='domain', how='outer',
            suffixes=('_bing', '_hubspot', '_google'))
        
        print(df4.info())

        
if __name__ == '__main__':
    instance = AgenciesParser()
    instance.main()
