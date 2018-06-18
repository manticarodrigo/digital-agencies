import pycountry

from .utils import (
    get_address_components,
    parse_budged,
    clean_language,
    get_domain,
)
from .base_parser import BaseParser

class BingParser(BaseParser):
    provider = 'bing_partners'
    short_name = 'bing'

    no_transform = [
        'name', 'website_url', 'phone', 'email',
        'industries', 'logo_url',
    ]

    nested_keys_map = (
        ('source', 'source'),
        ('description', 'description'),
        ('ranking', 'badge'),
    )

    budget_key = 'budget'
    full_address_key = 'location'

    def get_custom_fields(self, result, item):
        # Coordinates
        cords = item.get('coordinates')
        if cords and len(cords) == 2:
            result['coordinates'] = {
                'lat': float(cords[0]),
                'long': float(cords[1])
            }

        # Services
        if item.get('areas_of_expertise'):
            result['services'] = item.get('areas_of_expertise')

        # Social networks
        result['social_networks'] = {
            'facebook': item.get('facebook_url'),
            'twitter_url': item.get('twitter_url'),
            'linkedin_url': item.get('linkedin_url'),
        }
            

if __name__ == '__main__':
    instance = BingParser()
    instance.parse()

