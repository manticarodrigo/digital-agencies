import pycountry

from .utils import (
    get_address_components,
    parse_budged,
    clean_language,
    get_domain,
)
from .base_parser import BaseParser

NIO_VALUE = 31.67 # 17/06/18

class HubspotParser(BaseParser):
    provider = 'google_partners'
    short_name = 'google'

    no_transform = [
        'name', 'email', 'industries', 'logo_url', 'services'
    ]

    # Nested dict fields
    nested_keys_map = (
        ('source', 'source'),
        ('ranking', 'badgeTier'),
    )

    website_url_key = 'websiteUrl'

    def get_address(self, item):
        return {
            'full_address': item.get('locations', [{}])[0].get('address')
        }

    def get_budget(self, item):
        # Getting NIO value
        if item.get('originalMinMonthlyBudget', {}).get('currencyCode') == 'USD':
            return item.get('originalMinMonthlyBudget', {}).get('units', 0)
        else:
            # try to make a conversion
            units = float(item.get('convertedMinMonthlyBudget', {}).get('units', 0))
            if not units == 0:
                val = (units / NIO_VALUE)
                return round(val,(len(str(int(val)))-1) * -1)
        return 0

    def get_iso_languages(self, item):
        languages = []
        for info in item.get('localizedInfos'):
            code = info.get('languageCode')
            alpha_3 = pycountry.languages.lookup(code.split('-')[0]).alpha_3
            if alpha_3 not in languages:
                languages.append(alpha_3)
        return languages


    def get_custom_fields(self, result, item):
        # Website
        result['website_url'] = item.get(self.website_url_key)

        # Coordinates
        cords = item.get('locations', [{}])[0].get('latLng')
        result['coordinates'] = {
            'lat': float(cords.get('latitude')),
            'long': float(cords.get('longitude'))
        }

        # Description
        result['description'] = {
            self.short_name: item.get('localizedInfos', [{}])[0].get('overview')
        }

        # logo
        result['logo_url'] = item.get('publicProfile', {}).get('displayImageUrl')


if __name__ == '__main__':
    instance = HubspotParser()
    instance.parse()

