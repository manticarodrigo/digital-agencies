# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
)


class ClutchSpider(scrapy.Spider):
    name = 'clutch_partners'
    start_urls = ['https://clutch.co/profile/blue-fountain-media']

    # def parse(self, response):
    #     soup = BeautifulSoup(response.text, 'lxml')
    #     for city in soup.select('.dropdown-list.city-list li'):
    #         yield response.follow(
    #             self.start_urls[0] + city['data-url'] + '/',
    #             self.parse_profile)

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        item = {}
        item['source'] = response.url
        item['provider'] = self.name

        item['name'] = get_text_by_selector(soup, 'h1.page-title')
        item['logo'] = get_attribute_by_selector(
            soup, '.page-heading-brand-info .logo-wrapper img', 'src')
        item['description'] = get_text_by_selector(
            soup, '.field-item p')
        item['website_url'] = get_attribute_by_selector(
            soup, '.quick-menu-element.website-link-a a', 'href')

        item['address'] = {
            'street': get_text_by_selector(soup, '.street-address'),
            'locality': get_text_by_selector(soup, '.locality'),
            'region': get_text_by_selector(soup, '.region'),
            'postal_code': get_text_by_selector(soup, '.postal-code'),
            'country': get_text_by_selector(soup, '.country-name'),
        }
        item['phone'] = get_text_by_selector(soup, '.tel')
        # item['email'] = get_text_by_selector(
        #     obj, '.contact-info .email + p')
        yield item
