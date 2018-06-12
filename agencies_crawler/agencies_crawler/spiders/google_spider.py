# -*- coding: utf-8 -*-
import json
from urllib import parse
import scrapy

BASE_URL = 'https://partners.clients6.google.com/v2/companies?'
PARAMS = {
    'view': 'CV_GOOGLE_PARTNER_SEARCH',
    'key': 'AIzaSyCi4oosxbZoHR65JXdMVy7eVRVsIO6tPlQ'
}


class GooglePartnersSpider(scrapy.Spider):
    name = 'google_partners'
    start_urls = [
        BASE_URL + parse.urlencode(PARAMS)
    ]

    def parse(self, response):
        json_data = json.loads(response.text)
        print(json_data)
        
        next_page_token = json_data.get('nextPageToken')
        if next_page_token:
            print(next_page_token)
            PARAMS['pageToken'] = next_page_token
            yield response.follow(BASE_URL + parse.urlencode(PARAMS), callback=self.parse)
