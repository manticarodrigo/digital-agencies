# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.spiders.base_spider import BasePartnersSpider


class BingPartnersSpider(BasePartnersSpider):
    name = 'bing_partners'
    start_urls = [
        'https://advertise.bingads.microsoft.com/en-us/resources/bing-partner-program/partner-directory'
    ]
    pagination_selector = '#search-result-statistics + li > a'
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
    partner_standard_selector = '.partner-item.standard'

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        for partner in soup.select(self.partner_standard_selector):
            agency = {
                'provider': self.name,
                'source': response.url,
                'name': partner.select_one('h3').get_text().strip(),
                'location': partner.select_one('.location').get_text().strip(),
                'website_url': partner.select_one('.link').get_text().strip(),
            }
            yield agency
        for link in self.get_profiles_urls(soup):
            request = response.follow(link.get('href'), self.parse_profile)
            try:
                request.meta['agency'] = {
                    'full_address': link.parent.find_previous_sibling().get_text().strip()
                }
            except:
                pass
            yield request

        # Follow pagination links
        if self.pagination_selector:
            next_page = soup.select_one(self.pagination_selector)
            if next_page is not None:
                yield response.follow(
                    next_page.get('href'), callback=self.parse)
