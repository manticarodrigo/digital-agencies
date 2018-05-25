# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

class BasePartnersSpider(scrapy.Spider):
    name = 'partners_spider'
    links_selector = None
    pagination_selector = None
    name_selector = None
    short_address_selector = None
    website_url_selector = None
    ranking_selector = None
    brief_selector = None
    industries_selector = None
    partners_text_selector = None
    budget_selector = None
    languages_selector = None

    def get_text_by_selector(self, soup, selector):
        """ Gets text by selector """
        if selector:
            item = soup.select_one(selector)
            return item.get_text().strip() if item else None

    def get_link_from_selector(self, soup, selector):
        """ Gets agency website url """
        if selector:
            url = soup.select_one(selector)
            if url is not None:
                return url.get('href')

    def get_profiles_urls(self, soup):
        """ Links to follow up to get content """
        if self.links_selector:
            return soup.select(self.links_selector)
        else:
            return None

    def get_agency_name(self, soup):
        """ Gets agency name """
        return self.get_text_by_selector(soup, self.name_selector)
    
    def get_agency_short_address(self, soup):
        """ Gets agency short address """
        return self.get_text_by_selector(soup, self.short_address_selector)
    
    def get_agency_ranking(self, soup):
        """ Gets agency ranking """
        return self.get_text_by_selector(soup, self.ranking_selector)
    
    def get_agency_brief(self, soup):
        """ Gets agency brief """
        return self.get_text_by_selector(soup, self.brief_selector)

    def get_agency_industries(self, soup):
        """ Gets agency brief """
        if self.industries_selector:
            ul = soup.select_one(self.industries_selector)
            liArray = ul.find_all('li')
            concatString = " -".join([el.get_text().strip() for el in liArray])
            return concatString

    def get_agency_website_url(self, soup):
        """ Gets agency website url """
        return self.get_link_from_selector(soup, self.website_url_selector)

    def get_agency_reviews(self, soup):
        pass

    def get_agency_budget(self, soup):
        return self.get_text_by_selector(soup, self.budget_selector)

    def get_agency_languages(self, soup):
        elements = soup.select(self.languages_selector)
        return "\n".join([el.get_text().strip() for el in elements])

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
        agency['short_address'] = self.get_agency_short_address(soup)
        agency['website_url'] = self.get_agency_website_url(soup)
        agency['ranking'] = self.get_agency_ranking(soup)
        agency['brief'] = self.get_agency_brief(soup)
        agency['industries'] = self.get_agency_industries(soup)
        agency['reviews'] = self.get_agency_reviews(soup)
        agency['budget'] = self.get_agency_budget(soup)
        agency['languages'] = self.get_agency_languages(soup)
        yield agency
