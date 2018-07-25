# -*- coding: utf-8 -*-
import re
import json

import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
    get_int_from_string,
    get_list_by_selector,
)

class UpCitySpider(scrapy.Spider):
    name = 'upcity_partners'
    start_urls = [
        'https://upcity.com/local-marketing-agencies/lists',
    ]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for link in soup.select('.list-grouping-panel ul > li > a'):
            request = response.follow(link.get('href'), self.parse_list)
            yield request

    def parse_list(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        print('Parsing: %s' % soup.title)
        for profile in soup.select('.profiles > .row'):
            item = {}
            item['name'] = get_text_by_selector(profile, 'h4')
            item['badge'] = get_text_by_selector(profile, '.partner-badge')
            item['yext_certified'] = bool(profile.find('span', class_='yext-certified'))
            item['full_address'] = get_text_by_selector(profile, 'h5')
            url = get_attribute_by_selector(profile, 'h4 > a', 'href')

            request = response.follow(url, self.parse_profile)
            request.meta['item'] = item

            yield request

        next_page = soup.select_one('.pagination a.next_page')
        if next_page is not None:
            yield response.follow(next_page.get('href'), callback=self.parse_list)

    def parse_profile(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        item = response.meta['item']
        item['provider'] = self.name
        item['source_url'] = response.url
        # item['name'] = get_text_by_selector(soup, '.review-box h1')
        item['short_address'] = get_text_by_selector(soup, '.review-box h6')
        item['logo_url'] = get_attribute_by_selector(
            soup, '.review-box .website > img', 'src')
        item['claimed'] = bool(soup.find('p', class_='claimed'))

        reviews = soup.find_all('a', class_='review-score')
        try:
            item['review_stars'] = float(reviews[0].text)
            item['total_reviews'] = get_int_from_string(reviews[1].text)
        except ValueError:
            item['review_stars'] = 0
            item['total_reviews'] = 0

        item['telephone'] = get_text_by_selector(
            soup, '.contact-box .telephone')
        item['website_url'] = get_attribute_by_selector(
            soup, '.contact-box .website', 'href')
        item['certified'] = get_text_by_selector(
            soup, '.certified_badge small')

        item['description'] = get_text_by_selector(
            soup, '.description .excerpt').replace('read more', '')

        item['included_list'] = get_list_by_selector(
            soup, '.profile-box div.lists-indent ul')
        item['social_urls'] = {
            'facebook': get_attribute_by_selector(
                soup, '.profile-social .icon_facebook', 'href'),
            'linkedin': get_attribute_by_selector(
                soup, '.profile-social .icon_linked_in', 'href'),
            'twitter': get_attribute_by_selector(
                soup, '.profile-social .icon_twitter', 'href'),
            'instagram': get_attribute_by_selector(
                soup, '.profile-social .icon_instagram', 'href')
        }

        try:
            item['locality'] = soup.find(
                'h6', string='Locality').find_next_sibling('ul').find(
                    'div', class_='checkmark-closed').next
        except AttributeError:
            item['locality'] = None

        try:
            item['budget'] = soup.find(
                'h6', string='Minimum Monthly Budget').find_next_sibling(
                    'ul').find('div', class_='checkmark-closed').next
        except AttributeError:
            item['budget'] = None

        try:
            item['business_type'] = soup.find(
                'h6', string='Types of Small Businesses We Work With').find_next_sibling(
                    'ul').find('div', class_='checkmark-closed').next
        except AttributeError:
            item['business_type'] = None

        try:
            services = soup.find('h6', string='Services').find_next_sibling(
                'ul').find_all('div', class_='checkmark-closed')
            item['services'] = [
                service.next for service in services] if services else None
        except AttributeError:
            item['services'] = None

        try:
            clients = soup.find('h6', string='Clients We Serve').find_next_sibling(
                'ul').find_all('div', class_='checkmark-closed')
            item['clients'] = [
                client.next for client in clients] if clients else None
        except AttributeError:
            item['clients'] = None

        try:
            platforms = soup.find(
                'h6', string='Web Platforms We Support').find_next_sibling(
                    'ul').find_all('div', class_='checkmark-closed')
            item['web_platforms'] = [
                platform.next for platform in platforms] if platforms else None
        except AttributeError:
            item['web_platforms'] = None
            
        try:
            item['coordinates'] = {
                'latitude': float(get_attribute_by_selector(
                    soup, '.profile-box-locations .location-map', 'data-lat')),
                'longitude': float(get_attribute_by_selector(
                    soup, '.profile-box-locations .location-map', 'data-lng'))
            }
        except TypeError:
            item['coordinates'] = None

        street_address = soup.find('span', itemprop='streetAddress')
        address_locality = soup.find('span', itemprop='addressLocality')
        address_region = soup.find('span', itemprop='addressRegion')
        postal_code = soup.find('span', itemprop='postalCode')

        item['address'] = {
            'street_address': street_address.text if street_address else None,
            'address_locality': address_locality.text if address_locality else None,
            'address_region': address_region.text if address_region else None,
            'postal_code': postal_code.text if postal_code else None,
        }

        yield item
