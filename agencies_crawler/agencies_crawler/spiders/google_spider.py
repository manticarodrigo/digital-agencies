# -*- coding: utf-8 -*-
import json
from urllib import parse

import scrapy


class GooglePartnersSpider(scrapy.Spider):
    name = 'google_partners'
    queries = {
        'view': 'CV_GOOGLE_PARTNER_SEARCH',
        'key': 'AIzaSyCi4oosxbZoHR65JXdMVy7eVRVsIO6tPlQ',
        'orderBy': 'id'
    }
    base_url = 'https://partners.clients6.google.com/v2/companies/'
    start_urls = [base_url + '?' + parse.urlencode(queries)]

    def parse_company(self, data, url):
        data['provider'] = 'google_partners'
        data['source'] = url
        data['profile_page'] = ('https://www.google.com/partners/' +
            '#a_profile;bdgt=;idtf={0};lang=us-en'.format(
                data.get('id')
            ))
        data['name'] = data.get(
            'localizedInfos', [{}])[0].get('displayName')

    def parse(self, response):
        json_data = json.loads(response.text)
        companies = json_data.get('companies')
        for company in companies:
            self.parse_company(company, response.url)
            yield company

        next_page_token = json_data.get('nextPageToken')
        if next_page_token:
            self.queries['pageToken'] = next_page_token
            yield response.follow(
                self.base_url + '?' + parse.urlencode(self.queries),
                callback=self.parse)
