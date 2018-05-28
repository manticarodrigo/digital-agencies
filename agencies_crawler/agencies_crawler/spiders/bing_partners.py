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
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_SocialTiles_WebAddress_Container > .tile-link')
    name_selector = 'h1.page-title'
    ranking_selector = 'div.partner-badge-large > div.type'
    brief_selector = 'section.rule-bottom > div.container > div.row > div:nth-of-type(3) > div'
    budget_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_InfoTiles_MinBudget_Content')
    industries_selector = 'div.row.industries-list' # @TODO Review this selector
    logo_url_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_Logo_Image')
    services_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_InfoTiles_AreasOfExpertise_Content')
    languages_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_LanguagesServed_Title' +
        ' + .industries-list')
    facebook_url_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_SocialTiles_Facebook_Link')
    twitter_url_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_SocialTiles_Twitter_Link')
    linkedin_url_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_SocialTiles_LinkedIn_Link')
    phone_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_SocialTiles_Phone_Content')