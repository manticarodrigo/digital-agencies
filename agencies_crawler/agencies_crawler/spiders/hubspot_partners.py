# -*- coding: utf-8 -*-
import scrapy

from agencies_crawler.spiders.base_spider import BasePartnersSpider 


class HubspotPartnersSpider(BasePartnersSpider):
    name = 'hubspot_partners'
    start_urls = ['https://www.hubspot.com/agencies']
    pagination_selector = None
    links_selector = 'a.directories__link'
    title_selector = '.partners-details__hero-text > h2'
    short_address_selector = 'p.partners-details__hero-location'
    website_url_selector = '.partners-details__hero-website.partners-listing-website'
    name_selector = 'div.partners-details__hero-text > h2'
    ranking_selector = 'p.partners-details__hero-icon'
    brief_selector = 'div.partners-details__about-container > p'
    industries_selector = 'div.partners-details__fieldset.industry > ul.partners-details__list'
    partners_text_selector = '.partners-card-ratings > p'
    budget_selector = '.partners-details__fieldset.budget .circle upper'
    languages_selector = '.partners-details__list.language'
    stars_selector = 'div.partners-details-card-ratings--stars'
    logo_url_selector = 'div.partners-details__hero-image-wrapper > img'
    regions_selector = 'div.partners-regions > ul.partners-details__list.region'
    awards_selector = 'div.certification ul.partners-details__list'

    def get_agency_reviews(self, soup):
        """ Gets agency reviews """
        text = self.get_text_by_selector(soup, self.partners_text_selector)
        numbers = [int(s) for s in text.split() if s.isdigit()]
        return numbers[0] if numbers else 0

    def get_agency_awards(self, soup):
        return self.get_list_by_selector(soup, self.awards_selector)

    def get_agency_industries(self, soup):
        """ Gets agency industries """
        if self.industries_selector:
            item_arr = soup.select_one(self.industries_selector).find_all('li')
            second_item_arr = soup.select_one('div.directories__toggle-contents').find_all('li')
            string = ('\n'.join([el.get_text().strip() for el in item_arr]) 
            + '\n' + '\n'.join([el.get_text().strip() for el in second_item_arr]))  # NOQA
            return string

    def get_agency_stars(self, soup):
        """ Gets agency stars """
        if self.stars_selector:
            item_arr = soup.select("{0} span.full".format(self.stars_selector))
            return len(item_arr)
