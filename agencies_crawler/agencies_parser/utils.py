import re

import tldextract
import pandas as pd


def get_domain(url):
    if url:
        xtract = tldextract.extract(url)
        return xtract.domain


def to_excel(
        df, file_name='simple-report.xlsx', columns=None, use_index=False):
    writer = pd.ExcelWriter('%s' % file_name, engine='xlsxwriter')
    extra_params = {}
    if columns:
        extra_params['columns'] = columns

    extra_params['index'] = use_index
    df.to_excel(writer, **extra_params)
    writer.save()


def get_address_components(full_address=None, short_address=None):
    """ Parse full and short address """
    raw_address = None
    address_dict = {}
    from_full_address = False

    if full_address:
        raw_address = full_address
        from_full_address = True

    elif short_address:
        raw_address = short_address

    if raw_address:
        if ',' not in raw_address:
            address_dict['address1'] = raw_address
        else:
            address_componets = raw_address.split(',')
            if len(address_componets) == 4:
                address_dict['address1'] = address_componets[0]
                address_dict['address2'] = address_componets[1].strip()
                address_dict['city'] = address_componets[2].strip().title()
            elif len(address_componets) == 3 and from_full_address:
                address_dict['address1'] = address_componets[0]
                address_dict['city'] = address_componets[1].strip().title()
            elif not from_full_address:
                address_dict['city'] = address_componets[0].strip().title()
        
        # Try to get zip code
        zip_code = re.search(r'(\d{5})([-])?(\d{4})?', raw_address)
        address_dict['zip_code'] = ''.join(match for match in zip_code.groups() if match) if zip_code else None

        state = re.search(r'([A-Z]{2})', raw_address)
        address_dict['state'] = state.group(0) if state else None

        if 'United States'.lower() in raw_address.lower() or state or zip_code:
            address_dict['country'] = 'US'
        address_dict['full_address'] = raw_address
        return address_dict

def hasNumbers(string):
    return any(char.isdigit() for char in string)

def parse_budged(x):
    """ Convert budget string to float """
    if isinstance(x, (float, int)) or x is None:
        return x
    if isinstance(x, str):
        match = re.search(r'(\d+[,\.]?\d*)', x)
        value = match.group(0).strip().replace(',', '') if match else None
        if value and 'K' in x:
            return float(value) * 1000
        elif value:
            return float(value)
    return 0

def clean_language(language):
    if language.lower() == 'chinese traditional':
        return 'Chinese'
    if language.lower() == 'greek':
        return 'Mycenaean Greek'
    if language.lower() == 'mandarin':
        return 'Mandarin Chinese'
    if language.lower() == 'cantonese':
        return 'Yue Chinese'
    if language.lower() == 'malay':
        return 'Malay (macrolanguage)'
    if language.lower() == 'kiswahili':
        return 'Swahili (macrolanguage)'
    return language
