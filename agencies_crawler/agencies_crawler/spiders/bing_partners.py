# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.spiders.base_spider import BasePartnersSpider
from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
    get_list_by_selector,
)


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
    badge_selector = 'div.partner-badge-large > div.type'
    description_selector = 'section.rule-bottom > div.container > div.row > div:nth-of-type(3) > div'
    budget_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_InfoTiles_MinBudget_Content')
    industries_selector = 'div.row.industries-list' # @TODO Review this selector
    logo_url_selector = (
        '#p_lt_ctl01_pageplaceholder_p_lt_WebPartZone3_zoneContent_pageplaceholder' +
        '_p_lt_ctl01_PartnerProfileQueryRepeater_repItems_ctl00_ctl00_Logo_Image')
    areas_of_expertise_selector = (
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

    def get_agency_badge(self, soup):
        """ Gets agency badge """
        return get_text_by_selector(soup, self.badge_selector)

    def get_agency_description(self, soup):
        """ Gets agency description """
        return get_text_by_selector(soup, self.description_selector)

    def get_areas_of_expertise(self, soup):
        """ Gets agency services """
        return get_list_by_selector(soup, self.areas_of_expertise_selector)

    def get_agency_phone(self, soup):
        """ Gets agency phone """
        return get_text_by_selector(soup, self.phone_selector)

    def get_agency_facebook_url(self, soup):
        """ Gets agency facebook url """
        return get_attribute_by_selector(
            soup, self.facebook_url_selector, 'href')

    def get_agency_twitter_url(self, soup):
        """ Gets agency twitter url """
        return get_attribute_by_selector(
            soup, self.twitter_url_selector, 'href')

    def get_agency_linkedin_url(self, soup):
        """ Gets agency linkedin url """
        return get_attribute_by_selector(
            soup, self.linkedin_url_selector, 'href')

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        for partner in soup.select(self.partner_standard_selector):
            yield {
                'provider': self.name,
                'source': response.url,
                'name': partner.select_one('h3').get_text().strip(),
                'short_address': partner.select_one('.location').get_text().strip(),
                'website_url': partner.select_one('.link').get_text().strip(),
            }
        for link in self.get_profiles_urls(soup):
            request = response.follow(link.get('href'), self.parse_profile)
            request.meta['agency'] = {
                'location': link.parent.find_previous_sibling().get_text().strip()
            }
            yield request

        # Follow pagination links
        next_page = self.get_next_page(soup)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_extra_fields(self, agency, soup):
        agency['badge'] = self.get_agency_badge(soup)
        agency['description'] = self.get_agency_description(soup)
        agency['areas_of_expertise'] = self.get_areas_of_expertise(soup)
        # agency['email'] = self.get_agency_email(soup)
        agency['phone'] = self.get_agency_phone(soup)
        agency['facebook_url'] = self.get_agency_facebook_url(soup)
        agency['twitter_url'] = self.get_agency_twitter_url(soup)
        agency['linkedin_url'] = self.get_agency_linkedin_url(soup)
        # agency['coordinates'] = self.get_agency_coordinates(soup)
        return agency
