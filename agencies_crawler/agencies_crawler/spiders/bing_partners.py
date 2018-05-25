# -*- coding: utf-8 -*-
import scrapy

from agencies_crawler.spiders.base_spider import BasePartnersSpider 


class BingPartnersSpider(BasePartnersSpider):
    name = 'bing_partners'
    start_urls = [
        'https://advertise.bingads.microsoft.com/en-us/resources/bing-partner-program/partner-directory'
    ]
    pagination_selector = None
    links_selector = 'a.profile-link'
    title_selector = 'h1.page-title'
