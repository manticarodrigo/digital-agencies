# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
    get_list_by_selector,
)


class BasePartnersSpider(scrapy.Spider):
    name = 'partners_spider'
    links_selector = None
    pagination_selector = None
    name_selector = None
    website_url_selector = None
    industries_selector = None
    budget_selector = None
    languages_selector = None
    logo_url_selector = None

    def get_profiles_urls(self, soup):
        """ Links to follow up to get content """
        if self.links_selector:
            return soup.select(self.links_selector)

    def get_agency_name(self, soup):
        """ Gets agency name """
        return get_text_by_selector(soup, self.name_selector)

    def get_agency_industries(self, soup):
        """ Gets agency industries """
        return get_list_by_selector(soup, self.industries_selector)

    def get_agency_website_url(self, soup):
        """ Gets agency website url """
        return get_attribute_by_selector(
            soup, self.website_url_selector, 'href')

    def get_agency_logo_url(self, soup):
        """ Gets agency logo url """
        return get_attribute_by_selector(
            soup, self.logo_url_selector, 'src')

    def get_agency_budget(self, soup):
        """ Gets agency budget """
        return get_text_by_selector(soup, self.budget_selector)

    def get_agency_languages(self, soup):
        """ Gets agency languages """
        return get_list_by_selector(soup, self.languages_selector)

    def get_next_page(self, soup):
        if self.pagination_selector:
            next_page = soup.select_one(self.pagination_selector)
            if next_page is not None:
                return next_page.get('href')

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        for link in self.get_profiles_urls(soup):
            request = response.follow(link.get('href'), self.parse_profile)
            yield request

        # Follow pagination links
        next_page = self.get_next_page(soup)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_extra_fields(self, agency, soup):
        return agency

    def parse_profile(self, response):
        agency = response.meta.get('agency', {})
        soup = BeautifulSoup(response.text, 'lxml')
        agency['name'] = self.get_agency_name(soup)
        agency['provider'] = self.name
        agency['source'] = response.url
        agency['website_url'] = self.get_agency_website_url(soup)
        agency['industries'] = self.get_agency_industries(soup)
        agency['budget'] = self.get_agency_budget(soup)
        agency['logo_url'] = self.get_agency_logo_url(soup)
        agency['languages'] = self.get_agency_languages(soup)
        agency = self.parse_extra_fields(agency, soup)
        yield agency
