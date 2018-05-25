# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

class BasePartnersSpider(scrapy.Spider):
    name = 'partners_spider'
    links_selector = None
    pagination_selector = None
    title_selector = None

    def get_profiles_urls(self, soup):
        """ Links to follow up to get content """
        if self.links_selector:
            return soup.select(self.links_selector)
        else:
            return None

    def get_agency_name(self, soup):
        """ Gets agency name from the title """
        title = soup.select_one(self.title_selector)
        return title.get_text().strip() if title else 'No title found'

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        for link in self.get_profiles_urls(soup):
            request = response.follow(link.get('href'), self.parse_profile)
            yield request

        # Follow pagination links
        if self.pagination_selector:
            next_page = soup.select_one(self.pagination_selector)
            if next_page is not None:
                yield response.follow(
                    next_page.get('href'), callback=self.parse)


    def parse_profile(self, response):
        agency = {}
        soup = BeautifulSoup(response.text, 'lxml')
        agency['provider'] = self.name
        agency['source'] = response.url
        agency['name'] = self.get_agency_name(soup)
        yield agency
