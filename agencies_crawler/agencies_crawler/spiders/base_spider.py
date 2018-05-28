# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from bs4.element import NavigableString

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
    stars_selector = None
    logo_url_selector = None
    regions_selector = None
    services_selector = None
    phone_selector = None

    def get_text_by_selector(self, soup, selector):
        """ Gets text by selector """
        if selector:
            item = soup.select_one(selector)
            return item.get_text().strip() if item else None

    def get_attribute_by_selector(self, soup, selector, attribute):
        """ Gets attribute by selector """
        if selector:
            url = soup.select_one(selector)
            if url is not None:
                return url.get(attribute)
    
    def get_list_by_selector(self, soup, selector):
        """ Gets list by selector """
        # @TODO its failing in some cases
        if selector:
            item_arr = soup.select_one(selector).children
            string = '\n'.join([el.get_text().strip() for el in item_arr if not isinstance(el, NavigableString)])
            return string

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
        """ Gets agency industries """
        return self.get_list_by_selector(soup, self.industries_selector)

    def get_agency_stars(self, soup):
        pass

    def get_agency_website_url(self, soup):
        """ Gets agency website url """
        return self.get_attribute_by_selector(soup, self.website_url_selector, 'href')

    def get_agency_logo_url(self, soup):
        """ Gets agency logo url """
        return self.get_attribute_by_selector(soup, self.logo_url_selector, 'src')
    
    def get_agency_regions(self, soup):
        """ Gets agency regions """
        return self.get_list_by_selector(soup, self.regions_selector)
    
    def get_agency_services(self, soup):
        """ Gets agency services """
        return self.get_list_by_selector(soup, self.services_selector)
    
    def get_agency_phone(self, soup):
        """ Gets agency phone """
        return self.get_text_by_selector(soup, self.phone_selector)

    def get_agency_reviews(self, soup):
        pass

    def get_agency_budget(self, soup):
        return self.get_text_by_selector(soup, self.budget_selector)

    def get_agency_languages(self, soup):
        return self.get_list_by_selector(soup, self.languages_selector)

    def get_agency_awards(self, soup):
        pass

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
        agency['stars'] = self.get_agency_stars(soup)
        agency['logo_url'] = self.get_agency_logo_url(soup)
        agency['regions'] = self.get_agency_regions(soup)
        agency['services'] = self.get_agency_services(soup)
        agency['awards'] = self.get_agency_awards(soup)
        agency['phone'] = self.get_agency_phone(soup)
        yield agency
