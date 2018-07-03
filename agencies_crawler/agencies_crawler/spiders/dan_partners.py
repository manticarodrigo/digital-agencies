# -*- coding: utf-8 -*-
import scrapy
from pprint import pprint
from bs4 import BeautifulSoup

from agencies_crawler.utils import (
    get_text_by_selector,
    get_attribute_by_selector,
    get_list_by_selector,
)

raw_cities = [
    "New York", "San Francisco", "Los Angeles", "Chicago", "Atlanta", "Miami",
    "Seattle", "Boston", "San Diego", "Philadelphia", "Washington DC",
    "Portland", "Dallas", "Austin", "Houston", "Denver", "Charlotte",
    "Detroit", "Orlando", "Columbus", "Cincinnati", "Minneapolis", "Cleveland",
    "Tampa", "New York", "San Francisco", "Los Angeles", "Chicago", "Atlanta",
    "Miami", "Seattle", "Boston", "San Diego", "Philadelphia", "Washington DC",
    "Portland", "Dallas", "Austin", "Houston", "Denver", "Charlotte",
    "Detroit", "Orlando", "Columbus", "Cleveland", "Tampa", "London",
    "Birmingham", "Leeds", "Manchester", "Bristol", "Liverpool", "Nottingham",
    "Newcastle", "Sheffield", "Bath", "Oxford", "Cardiff", "Bournemouth",
    "Brighton", "Southampton", "Glasgow", "Edinburgh", "Toronto", "Vancouver",
    "Montreal", "Calgary", "Ottawa", "Sydney", "Melbourne", "Brisbane",
    "Perth", "Adelaide", "Canberra", "Amsterdam", "Rotterdam", "Berlin",
    "Paris", "Barcelona", "Madrid", "Milan", "Brussels", "Dublin", "Stockholm",
    "Oslo", "Helsinki", "Copenhagen", "Warsaw", "İstanbul", "Dubai",
    "Abu Dhabi", "Islamabad", "Hong Kong", "Shanghai", "Beijing", "Singapore",
    "Mumbai", "Manila",
]


class DanSpider(scrapy.Spider):
    name = 'dan_partners'
    base_url = 'https://digitalagencynetwork.com/agencies/'

    def start_requests(self):
        urls = [self.base_url + city.replace(
            ' ', '-').lower() for city in list(set(raw_cities))]
        return [scrapy.Request(url) for url in urls]

    def parse(self, response):
        # Follow links to post pages
        soup = BeautifulSoup(response.text, 'lxml')
        for obj in soup.select('#AgenciesListing div.agency-info'):
            item = {}
            item['source'] = response.url
            item['provider'] = 'dan_partners'
            item['name'] = get_text_by_selector(obj, 'div.wpb_wrapper > h3')
            item['description'] = get_text_by_selector(
                obj, 'div.wpb_wrapper > h6')
            item['logo'] = get_attribute_by_selector(
                obj, '.vc_single_image-img', 'src')
            item['website_url'] = get_attribute_by_selector(
                obj, 'div.wpb_wrapper > h3 > a', 'href')
            item['address'] = get_text_by_selector(
                obj, '.contact-info .address + p')
            item['phone'] = get_text_by_selector(
                obj, '.contact-info .phone + p')
            item['email'] = get_text_by_selector(
                obj, '.contact-info .email + p')
            yield item
