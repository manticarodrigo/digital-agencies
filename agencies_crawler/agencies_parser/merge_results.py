import pymongo

from scrapy.conf import settings


class AgenciesParser(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def main(self):
        print(self.collection.find())

if __name__ == '__main__':
    instance = AgenciesParser()
    instance.main()
