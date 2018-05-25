# -*- coding: utf-8 -*-
import scrapy

from agencies_crawler.spiders.base_spider import BasePartnersSpider 


class HubspotPartnersSpider(BasePartnersSpider):
    name = 'hubspot_partners'
    start_urls = ['https://www.hubspot.com/agencies']
    pagination_selector = None
    links_selector = 'a.directories__link'
    title_selector = '.partners-details__hero-text > h2'
        
