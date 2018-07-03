# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
)


class DanSpider(scrapy.Spider):
    name = 'dan_partners'
    start_urls = ['https://digitalagencynetwork.com/agencies/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for city in soup.select('.dropdown-list.city-list li'):
            yield response.follow(
                self.start_urls[0] + city['data-url'] + '/',
                self.parse_profile)

    def parse_profile(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        # Featured agencies
        featured_agencies = []
        for obj in soup.select('#FeaturedCityAgencies div.agency-item.featured'):
            featured_agencies.append(get_text_by_selector(obj, '.agency-text .wpb_wrapper a'))
        # List of agencies
        for obj in soup.select('#AgenciesListing div.agency-item-container'):
            item = {}
            item['source'] = response.url
            item['provider'] = 'dan_partners'
            item['name'] = get_text_by_selector(obj, '.agency-content > .wpb_wrapper a')
            item['is_featured'] = item['name'] in featured_agencies
            item['description'] = get_text_by_selector(
                obj, '.agency-content > .wpb_wrapper > h6, .agency-content .wpb_wrapper > p')
            item['logo'] = get_attribute_by_selector(
                obj, '.vc_single_image-img', 'src')
            item['website_url'] = get_attribute_by_selector(
                obj, '.agency-content > .wpb_wrapper a', 'href')
            item['address'] = get_text_by_selector(
                obj, '.contact-info .address + p')
            item['phone'] = get_text_by_selector(
                obj, '.contact-info .phone + p')
            item['email'] = get_text_by_selector(
                obj, '.contact-info .email + p')
            yield item
