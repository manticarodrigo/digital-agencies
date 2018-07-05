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
        web_tag = soup.find_all("strong", string="Web:")
        web_url = str(web_tag.previousSibling).strip()
        import pdb; pdb.set_trace()

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
        yield agency
