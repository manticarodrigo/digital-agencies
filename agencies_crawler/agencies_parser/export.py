from functools import reduce

import pymongo
import pandas as pd
import numpy as np

from scrapy.utils.project import get_project_settings
from .utils import to_excel

SETTINGS = get_project_settings()

from .bing_parser import BingParser
from .hubspot_parser import HubspotParser
from .google_parser import GoogleParser
from .awwwards_parser import AwwwardsParser

class ExportParsers(object):
    """ Agencies Profiles exporter """

    # Top elements have more priority
    priority_order = {
        'google',
        'hubspot',
        'bing',
    }

    unique_key = 'domain'

    def export(self):
        # bing_df = pd.DataFrame.from_dict(BingParser().parse())
        # hubspot_df = pd.DataFrame.from_dict(HubspotParser().parse())
        # google_df = pd.DataFrame.from_dict(GoogleParser().parse())
        awwwards_df = pd.DataFrame.from_dict(AwwwardsParser().parse())

        # to_excel(df=bing_df, file_name='bing_cleaned.xlsx')
        # to_excel(df=hubspot_df, file_name='hubspot_cleaned.xlsx')
        # to_excel(df=google_df, file_name='google_cleaned.xlsx')
        to_excel(df=awwwards_df, file_name='awwwards_cleaned.xlsx')        

if __name__ == '__main__':
    instance = ExportParsers()
    instance.export()
