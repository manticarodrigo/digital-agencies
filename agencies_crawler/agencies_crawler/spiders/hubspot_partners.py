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
    partners_text_selector = '.partners-card-ratings > p'

    def get_agency_reviews(self, soup):
        text = self.get_text_by_selector(soup, self.partners_text_selector)
        numbers = [int(s) for s in text.split() if s.isdigit()]
        return numbers[0] if numbers else 0
    