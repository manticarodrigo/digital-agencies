# -*- coding: utf-8 -*-
import csv
import json
from urllib import parse

import scrapy

from .google_spider import GooglePartnersSpider


class GooglePartnersSpiderCSV(GooglePartnersSpider):
    name = 'google_partners_csv'

    def get_urls_from_csv(self):
        with open('data/gpartners.csv', 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            urls = []
            for row in reader:
                urls.append("{0}{1}?{2}".format(
                    self.base_url,
                    row['google.id'],
                    parse.urlencode(self.queries)
                ))
            return urls

    def start_requests(self):
        return [scrapy.Request(url) for url in self.get_urls_from_csv()]

    def parse(self, response):
        json_data = json.loads(response.text)
        company = json_data.get('company',)
        self.parse_company(company, response.url)
        yield company

