import pycountry

from .utils import (
    get_address_components,
    parse_budged,
    clean_language,
    get_domain,
)
from .base_parser import BaseParser


class AwwwardsParser(BaseParser):
    provider = 'awwwards_agencies'
    short_name = 'awwwards'

    no_transform = [
        'name', 'source', 'websiteUrl', 'countrycity',
    ]

    website_url_key = 'websiteUrl'
  
if __name__ == '__main__':
    instance = AwwwardsParser()
    instance.parse()
