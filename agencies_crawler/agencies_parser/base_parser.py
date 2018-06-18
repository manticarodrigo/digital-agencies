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

class BaseParser(object):
    provider = None
    short_name = None

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

    # Common keys fields, keys that have the same name and don't need
    # to be parsed
    no_transform = []

    # Fields that we need to preserve in all partners
    # Is a nested fields tuple, to map fields
    nested_keys_map = ((),)

    # Keys definition
    languages_key = 'languages'
    budget_key = 'budget'
    full_address_key = 'full_address'
    short_address_key = 'short_address'

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
                'provider': self.provider
            }).sort('$natural')
        else:
            raise ValueError('No provider name set')

    def get_custom_fields(self, result, item):
        pass

    def parse(self):
        raw_data = self.get_raw_data()
        results = [self.parse_item(item) for item in raw_data]
        return results

    def parse_item(self, item):
        result = self.base_result.copy() # Prevent mutation

        # Domain (primary key)
        if item.get('website_url'):
            result['domain'] = get_domain(item.get('website_url'))

        # Common keys fields, keys that have the same name
        for key in self.no_transform:
            if item.get(key):
                result[key] = item[key]

        for merged_key, raw_key  in self.nested_keys_map:
            if item.get(raw_key):
                result[merged_key] = {self.short_name: item[raw_key]}

        # Address
        if self.full_address_key or self.short_address_key:
            result['address'] = get_address_components(
                item.get(self.full_address_key),
                item.get(self.short_address_key)
            )

        # Budget
        if self.budget_key and item.get(self.budget_key):
            result['min_budget'] = parse_budged(item.get(self.budget_key))

        # Language
        if self.languages_key and item.get(self.languages_key):
            result['languages'] = []
            for language in item.get(self.languages_key):
                result['languages'].append(
                    pycountry.languages.lookup(
                        clean_language(language)).alpha_3)

        self.get_custom_fields(result, item)

        pprint(result)
        return result
