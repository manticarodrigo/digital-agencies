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
    name_selector = 'h1.page-title'
    ranking_selector = 'div.partner-badge-large > div.type'
    brief_selector = 'section.rule-bottom > div.container > div.row > div:nth-of-type(3) > div'