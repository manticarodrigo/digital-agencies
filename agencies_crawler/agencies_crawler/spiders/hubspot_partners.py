# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.spiders.base_spider import BasePartnersSpider
from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
    get_list_by_selector,
)


class HubspotPartnersSpider(BasePartnersSpider):
    name = 'hubspot_partners'
    start_urls = ['https://www.hubspot.com/agencies']
    pagination_selector = '.directories__pagination ul li > a'
    links_selector = 'a.directories__link'
    title_selector = '.partners-details__hero-text > h2'
    short_address_selector = 'p.partners-details__hero-location'
    website_url_selector = '.partners-details__hero-website.partners-listing-website'
    name_selector = 'div.partners-details__hero-text > h2'
    tier_selector = 'p.partners-details__hero-icon'
    about_selector = 'div.partners-details__about-container > p'
    industries_selector = 'div.partners-details__fieldset.industry > ul.partners-details__list'
    partners_text_selector = '.partners-card-ratings > p'
    budget_selector = '.partners-details__fieldset.budget .circle.upper'
    languages_selector = '.partners-details__list.language'
    stars_selector = 'div.partners-details-card-ratings--stars'
    logo_url_selector = 'div.partners-details__hero-image-wrapper > img'
    regions_selector = 'div.partners-regions > ul.partners-details__list.region'
    awards_selector = 'div.certification ul.partners-details__list'

    def get_agency_short_address(self, soup):
        """ Gets agency short address """
        return get_text_by_selector(soup, self.short_address_selector)

    def get_agency_tier(self, soup):
        """ Gets agency badge """
        return get_text_by_selector(soup, self.tier_selector)

    def get_agency_about(self, soup):
        """ Gets agency description """
        return get_text_by_selector(soup, self.about_selector)

    def get_agency_reviews(self, soup):
        """ Gets agency reviews """
        text = get_text_by_selector(soup, self.partners_text_selector)
        numbers = [int(s) for s in text.split() if s.isdigit()]
        return numbers[0] if numbers else 0

    def get_agency_industries(self, soup):
        """ Gets agency industries """
        more_selector = 'div.directories__toggle-contents'
        if self.industries_selector and soup.select_one(self.industries_selector):
            item_arr = soup.select_one(self.industries_selector).find_all('li')
            result = [el.get_text().strip() for el in item_arr]
            if soup.select_one(more_selector):
                item_arr = soup.select_one(more_selector).find_all('li')
                result += [el.get_text().strip() for el in item_arr]
            return result

    def get_agency_stars(self, soup):
        """ Gets agency stars """
        if self.stars_selector:
            item_arr = soup.select("{0} span.full".format(self.stars_selector))
            return len(item_arr)

    def get_agency_regions(self, soup):
        """ Gets agency regions """
        return get_list_by_selector(soup, self.regions_selector)

    def get_agency_awards(self, soup):
        """ Gets agency awards """
        return get_list_by_selector(soup, self.awards_selector)

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        profiles_urls = self.get_profiles_urls(soup)
        for link in profiles_urls:
            request = response.follow(link.get('href'), self.parse_profile)
            yield request

        # Follow pagination links
        next_page = self.get_next_page(soup)
        if next_page and len(profiles_urls) > 0:  # hubspot has a bug on pagination
            yield response.follow(next_page, callback=self.parse)

    def get_next_page(self, soup):
        if self.pagination_selector:
            next_page = soup.select(self.pagination_selector)[-1]
            if next_page is not None:
                return next_page.get('href')

    def parse_extra_fields(self, agency, soup):
        agency['short_address'] = self.get_agency_short_address(soup)
        agency['tier'] = self.get_agency_tier(soup)
        agency['about'] = self.get_agency_about(soup)
        agency['reviews'] = self.get_agency_reviews(soup)
        agency['stars'] = self.get_agency_stars(soup)
        agency['regions'] = self.get_agency_regions(soup)
        agency['awards'] = self.get_agency_awards(soup)
        return agency
