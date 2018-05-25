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
    short_address_selector = 'p.partners-details__hero-location'
    ranking_selector = 'p.partners-details__hero-icon'
    brief_selector = 'div.partners-details__about-container > p'
    industries_selector = 'div.partners-details__fieldset.industry > ul.partners-details__list'
    stars_selector = 'div.partners-details-card-ratings--stars'
    logo_url_selector = 'div.partners-details__hero-image-wrapper > img'
    regions_selector = 'div.partners-regions > ul.partners-details__list.region'

    def get_agency_industries(self, soup):
        """ Gets agency industries """
        if self.industries_selector:
            item_arr = soup.select_one(self.industries_selector).find_all('li')
            string = '\n'.join([el.get_text().strip() for el in item_arr])
            second_item_arr = soup.select_one('div.directories__toggle-contents').find_all('li')
            string += '\n' + '\n'.join([el.get_text().strip() for el in second_item_arr])
            return string
    
    def get_agency_stars(self, soup):
        """ Gets agency stars """
        if self.stars_selector:
            item_arr = soup.find_all("{0} span.full".format(self.stars_selector))
            return len(item_arr)