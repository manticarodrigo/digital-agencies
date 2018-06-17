from pprint import pprint

import pymongo
import pycountry

from scrapy.utils.project import get_project_settings

from .utils import (
    get_address_components,
    parse_budged,
    clean_language,
    get_domain,
)

SETTINGS = get_project_settings()

class BingParser(object):
    provider = 'bing_partners'
    short_name = 'bing'

    base_result = {
        'name': None,
        'source': None,
        'domain': None,
        'ranking': None,
        'address': None,
        'coordinates': None,
        'website_url': None,
        'description': None,
        'industries': None,
        'reviews': None,
        'stars': None,
        'budget': None,
        'logo_url': None,
        'languages': None,
        'regions': None,
        'awards': None,
        'services': None,
        'email': None,
        'social_urls': None,
        'phone': None,
    }

    def __init__(self):
        connection = pymongo.MongoClient(
            SETTINGS['MONGODB_SERVER'],
            SETTINGS['MONGODB_PORT']
        )
        db = connection[SETTINGS['MONGODB_DB']]
        self.raw_collection = db[SETTINGS['MONGODB_RAW_COLLECTION']]

    def get_raw_data(self):
        if self.provider:
            return self.raw_collection.find({
                'provider': self.provider,
            })
        else:
            return []

    def parse(self):
        raw_data = self.get_raw_data()
        results = [self.parse_item(item) for item in raw_data]
        pprint(results)

    def parse_item(self, item):
        result = self.base_result.copy() # Prevent mutation

        # Domain (primary key)
        if item.get('website_url'):
            result['domain'] = get_domain(item.get('website_url'))
        
        # Common keys fields, keys that have the same name
        common_keys = [
            'name', 'website_url', 'phone', 'email',
            'industries', 'logo_url',
        ]

        for key in common_keys:
            if item.get(key):
                result[key] = item[key]

        # Nested dict fields
        nested_keys_map = (
            ('source', 'source'),
            ('description', 'description'),
            ('ranking', 'badge'),
        )

        for merged_key, raw_key  in nested_keys_map:
            if item.get(raw_key):
                result[merged_key] = {self.short_name: item[raw_key]}

        # Address
        if item.get('location') or item.get('short_address'):
            result['address'] = get_address_components(
                item.get('location'),
                item.get('short_address')
            )

        # Coordinates
        cords = item.get('coordinates')
        if cords and len(cords) == 2:
            result['coordinates'] = {
                'lat': float(cords[0]),
                'long': float(cords[1])
            }

        # Budget
        if item.get('budget'):
            result['min_budget'] = parse_budged(item.get('budget'))

        # Language
        if item.get('languages'):
            result['languages'] = []
            for language in item.get('languages'):
                result['languages'].append(
                    pycountry.languages.lookup(
                        clean_language(language)).alpha_3)

        # Services
        if item.get('areas_of_expertise'):
            result['services'] = item.get('areas_of_expertise')

        # Social networks
        result['social_networks'] = {
            'facebook': item.get('facebook_url'),
            'twitter_url': item.get('twitter_url'),
            'linkedin_url': item.get('linkedin_url'),
        }

        return result
            

if __name__ == '__main__':
    instance = BingParser()
    instance.parse()

