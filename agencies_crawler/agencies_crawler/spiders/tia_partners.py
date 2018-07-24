# -*- coding: utf-8 -*-
import re
import json
import scrapy
from bs4 import BeautifulSoup
from bs4.element import NavigableString


def get_by_text(soup, text, selector='strong', hyperlink=False, multiple=False):
    if isinstance(text, list):
        text = '|'.join(text)
    tag = soup.find(selector, string=re.compile(text, re.IGNORECASE))
    result = None
    if tag is not None:
        if hyperlink:
            if multiple:
                result = [link.get('href') for link in tag.parent.find_all('a')]
            else:
                link = tag.parent.find_next('a')
                if link:
                    result = link.get('href')
        else:
            result = ''
            for el in tag.next_siblings:
                if isinstance(el, NavigableString):
                    result += el
                else:
                    result += el.get_text().strip()
            if multiple and ',' in result:
                result = [result.strip() for result in result.split(',')]
    return result if result else None # we don't want an empty string or list

class TiaPartnersSpider(scrapy.Spider):
    name = 'tia_partners'
    base_url = 'http://www.topinteractiveagencies.com'
    categories_url = base_url + '/wp-json/wp/v2/posts?categories='

    def start_requests(self):
        categories = [
            97, # Africa
            244, # Asia
            99, # Europa
            246, # Latam
            243, # North America
            241, # Oceania
        ]

        return [scrapy.Request(
            self.categories_url + str(cat), self.parse) for cat in categories]

    def parse(self, response):
        data = json.loads(response.body_as_unicode())

        for item in data:
            agency = {}
            agency['provider'] = self.name
            agency['source'] = item['link']
            agency['name'] = item['title']['rendered']

            soup = BeautifulSoup(item['content']['rendered'], 'lxml')
            agency['website_url'] = get_by_text(
                soup, 'Web', hyperlink=True)
            agency['headquarters'] = get_by_text(soup, 'Headquarters')
            agency['mail'] = get_by_text(soup, 'Mail')
            agency['phone'] = get_by_text(soup, ['Phone', 'Tel'])
            agency['staff'] = get_by_text(soup, 'Staff')
            agency['clients'] = get_by_text(soup, 'Clients', multiple=True)
            agency['services'] = get_by_text(
                soup, 'Services', multiple=True)
            agency['social_media'] = get_by_text(
                soup, 'Social Media', hyperlink=True, multiple=True)

            try:
                tags_url = item.get('_links').get('wp:term')[1].get('href')
            except AttributeError:
                tags_url = None

            if tags_url:
                request = response.follow(
                    tags_url, callback=self.parse_tags)
                request.meta['agency'] = agency
                yield request
            else:
                yield agency

            # Follow pagination links
            try:
                groups = re.findall('<(.+?)>', str(response.headers.get('link')))
                if len(groups) == 1:
                    next_page = groups[0]
                elif len(groups) == 2:
                    next_page = groups[1]
            except AttributeError:
                next_page = None

            if next_page is not None:
                self.logger.info('Parsing page: %s' % next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_tags(self, response):
        agency = response.meta.get('agency')
        data = json.loads(response.body_as_unicode())
        agency['tags'] = [tag.get('name') for tag in data]
        yield agency
