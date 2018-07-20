# -*- coding: utf-8 -*-
import re
import json

import scrapy
from bs4 import BeautifulSoup

from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
    get_int_from_string,
)


class UpCitySpider(scrapy.Spider):
    name = 'upcity_partners'
    start_urls = [
        'https://upcity.com/local-marketing-agencies/profiles/edkent-media',
    ]

    # def parse(self, response):
    #     soup = BeautifulSoup(response.text, 'lxml')
    #     for link in soup.select('h3 > span > a'):
    #         request = response.follow(link.get('href'), self.parse_profile)
    #         yield request

    #     next_page = soup.select_one('ul.pager li.pager-next > a')
    #     if next_page is not None:
    #         yield response.follow(next_page.get('href'), callback=self.parse)

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        item = {}
        item['provider'] = self.name
        item['source_url'] = response.url
        item['name'] = get_text_by_selector(soup, '.review-box h1')
        item['short_address'] = get_text_by_selector(soup, '.review-box h6')
        item['logo_url'] = get_attribute_by_selector(soup, '.review-box .website > img', 'src')
        item['claimed'] = bool(soup.find('p', class_='claimed'))

        reviews = soup.find_all('a', class_='review-score')
        try:
            item['review_stars'] = reviews[0].text
            item['total_reviews'] = get_int_from_string(reviews[1].text)
        except ValueError:
            item['review_stars'] = 0
            item['total_reviews'] = 0

        item['telephone'] = get_text_by_selector(soup, '.contact-box .telephone')
        item['website_url'] = get_attribute_by_selector(soup, '.contact-box .website', 'href')
        item['badge'] = get_text_by_selector(soup, '.certified_badge small')

        item['description'] = get_text_by_selector(soup, '.description .excerpt')

        yield item
