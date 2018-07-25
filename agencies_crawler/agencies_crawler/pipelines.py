import logging

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(settings['MONGODB_URI'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_RAW_COLLECTION']]

    def process_item(self, item, spider):
        unique_key = 'id' if item.get('id') else 'name'
        self.collection.update(
            {unique_key: item.get(unique_key), 'provider': item.get('provider')}, item, upsert=True)
        logging.debug('Agency added to MongoDB')
        return item
