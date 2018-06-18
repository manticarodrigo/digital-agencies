import pycountry

from .utils import (
    get_address_components,
    parse_budged,
    clean_language,
    get_domain,
)
from .base_parser import BaseParser

class HubspotParser(BaseParser):
    provider = 'hubspot_partners'
    short_name = 'hubspot'

    no_transform = [
        'name', 'website_url', 'phone', 'email',
        'industries', 'logo_url',
    ]

    # Nested dict fields
    nested_keys_map = (
        ('source', 'source'),
        ('ranking', 'tier'),
        ('description', 'about'),
    )

    full_address_key = None

    def get_custom_fields(self, result, item):
        result['reviews_count'] = item.get('reviews')
        result['stars_count'] = item.get('stars')
        result['awards'] = item.get('awards')


if __name__ == '__main__':
    instance = HubspotParser()
    instance.parse()

