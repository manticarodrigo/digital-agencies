# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.spiders.base_spider import BasePartnersSpider
from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
    get_list_by_selector,
)


class TiaPartnersSpider(BasePartnersSpider):
    name = 'tia_partners'
    start_urls = [
        'http://www.topinteractiveagencies.com/digital-directory/north-america/united-states/new-york/'
    ]
    links_selector = 'div.maincontent div.fullarticle a.thumblink'
    pagination_selector = 'div.maincontent a.next.page-numbers'
    name_selector = 'div.maincontent h1.blogtitle.entry-title > span'

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        profiles_urls = self.get_profiles_urls(soup)
        for link in profiles_urls:
            request = response.follow(link.get('href'), self.parse_profile)
            yield request
        
        # Follow pagination links
        next_page = self.get_next_page(soup)
        if next_page and len(profiles_urls) > 0:
            yield response.follow(next_page, callback=self.parse)
    
    def get_agency_website_url(self, soup):
        tag = soup.find('strong', string=lambda string: string and 'Web' in string)
        if tag is not None:
            return tag.parent.find('a').get_text().strip()
    
    def get_agency_headquarters(self, soup):
        tag = soup.find('strong', string=lambda string: string and 'Headquarters' in string)
        if tag is not None:
            return tag.parent.get_text().strip() 

    def get_agency_phone(self, soup):
        tag = soup.find('strong', string=lambda string: string and 'Phone' in string)
        if tag is not None:
            return tag.parent.get_text().strip() 

    def get_agency_staff(self, soup):
        tag = soup.find('strong', string=lambda string: string and 'Staff' in string)
        if tag is not None:
            return tag.parent.get_text().strip() 
    
    def get_agency_clients(self, soup):
        tag = soup.find('strong', string=lambda string: string and 'Clients' in string)
        if tag is not None:
            return tag.parent.get_text().strip() 
    
    def get_agency_services(self, soup):
        tag = soup.find('strong', string=lambda string: string and 'Services' in string)
        if tag is not None:
            return tag.parent.get_text().strip() 

    def get_agency_social_media(self, soup):
        tag = soup.find('strong', string=lambda string: string and 'Social Media' in string)
        if tag is not None:
            return [link.get_text().strip() for link in tag.parent.find_all('a')]

    def get_next_page(self, soup):
        if self.pagination_selector:
            next_page = soup.select(self.pagination_selector)[-1]
            if next_page is not None:
                return next_page.get('href')

    def parse_profile(self, response):
        agency = response.meta.get('agency', {})
        soup = BeautifulSoup(response.text, 'lxml')
        agency['name'] = self.get_agency_name(soup)
        agency['provider'] = self.name
        agency['source'] = response.url
        agency['website_url'] = self.get_agency_website_url(soup)
        agency['headquarters'] = self.get_agency_headquarters(soup)
        agency['phone'] = self.get_agency_phone(soup)
        agency['staff'] = self.get_agency_staff(soup)
        agency['clients'] = self.get_agency_clients(soup)
        agency['services'] = self.get_agency_services(soup)
        agency['social_media'] = self.get_agency_social_media(soup)
        import pdb; pdb.set_trace()
        yield agency
