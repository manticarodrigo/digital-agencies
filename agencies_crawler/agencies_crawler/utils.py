# -*- coding: utf-8 -*-
from bs4.element import NavigableString


def get_int_from_string(text):
    try:
        return int(''.join(ch for ch in text if ch.isdigit()))
    except ValueError:
        return None

def get_text_by_selector(soup, selector):
    """ Gets text by selector """
    if selector:
        item = soup.select_one(selector)
        return item.get_text().strip() if item else None


def get_attribute_by_selector(soup, selector, attribute):
    """ Gets attribute by selector """
    if selector:
        url = soup.select_one(selector)
        if url is not None:
            return url.get(attribute)


def get_list_by_selector(soup, selector):
    """ Gets list by selector """
    if selector and soup.select_one(selector):
        item_arr = soup.select_one(selector).children
        result = [
            el.get_text().strip()
            for el in item_arr if not isinstance(el, NavigableString)]
        return result if result else None  # we don't want an empty array
