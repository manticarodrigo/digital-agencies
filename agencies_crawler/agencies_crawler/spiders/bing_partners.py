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
    website_url_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_SocialTiles_WebAddress_Container > .tile-link'
    )
