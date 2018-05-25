# -*- coding: utf-8 -*-
import scrapy

from agencies_crawler.spiders.base_spider import BasePartnersSpider 


class HubspotPartnersSpider(BasePartnersSpider):
    name = 'hubspot_partners'
    start_urls = ['https://www.hubspot.com/agencies']
    pagination_selector = None
    links_selector = 'a.directories__link'
    name_selector = 'div.partners-details__hero-text > h2'
    short_address_selector = 'p.partners-details__hero-location'
    ranking_selector = 'p.partners-details__hero-icon'
    brief_selector = 'div.partners-details__about-container > p'
    industries_selector = 'div.partners-details__fieldset.industry > ul.partners-details__list'
