# -*- coding: utf-8 -*-
import scrapy


class BingPartnersSpider(scrapy.Spider):
    name = 'bing_partners'
    start_urls = [
        'https://advertise.bingads.microsoft.com/en-us/resources/bing-partner-program/partner-directory'
    ]

    def parse(self, response):
        pass
