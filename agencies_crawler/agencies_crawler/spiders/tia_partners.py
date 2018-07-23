# -*- coding: utf-8 -*-
import json
import scrapy
from bs4 import BeautifulSoup
from bs4.element import NavigableString

from agencies_crawler.spiders.base_spider import BasePartnersSpider
from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
    get_list_by_selector,
)


class TiaPartnersSpider(scrapy.Spider):
    name = 'tia_partners'
    start_urls = [
        'http://www.topinteractiveagencies.com/wp-json/wp/v2/posts?categories=246'
    ]

    def get_by_text(self, soup, text, selector='strong', is_link=False):
        tag = soup.find(selector, string=lambda s: s and text in s)
        if tag is not None:
            if is_link:
                return tag.parent.find('a').get('href')
            else:
                result = ''
                for el in tag.next_siblings:
                    if isinstance(el, NavigableString):
                        result += el
                    else:
                        result += el.get_text().strip()
                # if ',' in result:
                #     result = result.split(',')
                return result

    # def get_agency_headquarters(self, soup):
    #     tag = soup.find('strong', string=lambda string: string and 'Headquarters' in string)
    #     if tag is not None:
    #         return tag.parent.get_text().strip()

    # def get_agency_phone(self, soup):
    #     tag = soup.find('strong', string=lambda string: string and 'Phone' in string)
    #     if tag is not None:
    #         return tag.parent.get_text().strip()

    # def get_agency_staff(self, soup):
    #     tag = soup.find('strong', string=lambda string: string and 'Staff' in string)
    #     if tag is not None:
    #         return tag.parent.get_text().strip()

    # def get_agency_clients(self, soup):
    #     tag = soup.find('strong', string=lambda string: string and 'Clients' in string)
    #     if tag is not None:
    #         return tag.parent.get_text().strip()

    # def get_agency_services(self, soup):
    #     tag = soup.find('strong', string=lambda string: string and 'Services' in string)
    #     if tag is not None:
    #         return tag.parent.get_text().strip() 

    # def get_agency_social_media(self, soup):
    #     tag = soup.find('strong', string=lambda string: string and 'Social Media' in string)
    #     if tag is not None:
    #         return [link.get_text().strip() for link in tag.parent.find_all('a')]

    def parse(self, response):
        data = json.loads(response.body_as_unicode())

        for item in data:
            agency = {}
            agency['provider'] = self.name
            agency['source'] = item['link']
            agency['name'] = item['title']['rendered']

            soup = BeautifulSoup(item['content']['rendered'], 'lxml')
            agency['website_url'] = self.get_by_text(soup, 'Web', is_link=True)
            agency['headquarters'] = self.get_by_text(soup, 'Headquarters')
            # agency['headquarters'] = self.get_agency_headquarters(soup)
            # agency['phone'] = self.get_agency_phone(soup)
            # agency['staff'] = self.get_agency_staff(soup)
            # agency['clients'] = self.get_agency_clients(soup)
            # agency['services'] = self.get_agency_services(soup)
            # agency['social_media'] = self.get_agency_social_media(soup)
            yield agency
