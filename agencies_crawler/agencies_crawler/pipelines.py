import logging

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        self.collection.update(
            {'name': item.get('name'), 'provider': item.get('provider')}, item, upsert=True)
        logging.debug('Agency added to MongoDB')
        return item
