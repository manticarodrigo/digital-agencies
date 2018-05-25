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

    def get_agency_industries(self, soup):
        if self.industries_selector:
            item_arr = soup.select_one(self.industries_selector).find_all('li')
            string = "\n".join([el.get_text().strip() for el in item_arr])
            second_item_arr = soup.select_one('div.directories__toggle-contents').find_all('li')
            string += "\n" + "\n".join([el.get_text().strip() for el in second_item_arr])
            return string