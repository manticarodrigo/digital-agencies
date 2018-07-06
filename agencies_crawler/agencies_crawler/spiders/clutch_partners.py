# -*- coding: utf-8 -*-
import re
import json

import scrapy
import js2xml
from bs4 import BeautifulSoup

from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
)


class ClutchSpider(scrapy.Spider):
    name = 'clutch_partners'
    start_urls = ['https://clutch.co/profile/blue-fountain-media', 'https://clutch.co/profile/deksia']

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
        item['slogan'] = get_text_by_selector(soup, '.field-name-field-pp-slogan .field-item')
        item['rating'] = get_text_by_selector(
            soup, '.field-name-field-pp-total-reviews .rating')
        item['reviews_count'] = get_text_by_selector(
            soup, '.reviews-count')
        item['logo'] = get_attribute_by_selector(
            soup, '.page-heading-brand-info .logo-wrapper img', 'src')
        item['description'] = get_text_by_selector(
            soup, '#summary .summary-description > div.row > div.col-xs-6-custom')
        item['website_url'] = get_attribute_by_selector(
            soup, '.quick-menu-element.website-link-a a', 'href')

        item['address'] = {
            'street': get_text_by_selector(soup, '.street-address'),
            'locality': get_text_by_selector(soup, '.locality'),
            'region': get_text_by_selector(soup, 'span.region'),
            'postal_code': get_text_by_selector(soup, '.postal-code'),
            'country': get_text_by_selector(soup, '.country-name'),
        }
        item['phone'] = get_text_by_selector(soup, '.tel')
        item['min_project_size'] = get_text_by_selector(
            soup, '.field-name-field-pp-min-project-size .field-item')
        item['hourly_rate'] = get_text_by_selector(
            soup, '.field-name-field-pp-hrly-rate-range .field-item')
        item['employees'] = get_text_by_selector(
            soup, '.field-name-field-pp-size-people .field-item')
        item['year_founded'] = get_text_by_selector(
            soup, '.field-name-field-pp-year-founded .field-item')

        try:
            email_script = js2xml.parse(soup.select_one('.field-name-field-pp-email script').text)
            email_raw = email_script.xpath('/program//var[1]/string/text()')[0].split('#')
            order = email_script.xpath('/program//assign[2]//bracketaccessor/property/number/@value')
            item['email'] = "".join([email_raw[int(x)] for x in order])
        except IndexError:
            item['email'] = None

        # Getting data from script
        # @TODO graphs are not matching
        data_script = soup.find_all('script')[-1].text
        regex = r"jQuery\.extend\(Drupal\.settings, (.*)\);"
        match = re.match(regex, data_script)
        if match and len(match.groups()) == 1:
            data = json.loads(match.group(1))
            item['locations'] = [{
                'lat': loc[0] if len(loc) >= 1 else None,
                'long': loc[1] if len(loc) >= 2 else None,
                'city': loc[2] if len(loc) >= 3 else None,
            } for loc in data.get('locations')]

            for graph in data.get('clutchGraph'):
                element_id = graph['element_id']
                title = soup.find('div', {'id': element_id}).previous_sibling.text
                s_title = title.replace(' ', '_').lower()
                item[s_title] = graph.get('dataset')
        yield item
