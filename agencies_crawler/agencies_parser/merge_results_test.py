import re

import pymongo
import pandas as pd
import numpy as np
import datetime
import pycountry

from scrapy.conf import settings
from agencies_parser.utils import get_domain, to_excel

OFFICIAL_COUNTRY_CODES = ["AD","AE","AF","AG","AI","AL","AM","AO","AQ","AR","AS","AT","AU","AW","AX","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BL","BM","BN","BO","BQ","BR","BS","BT","BV","BW","BY","BZ","CA","CC","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CU","CV","CW","CX","CY","CZ","DE","DJ","DK","DM","DO","DZ","EC","EE","EG","EH","ER","ES","ET","FI","FJ","FK","FM","FO","FR","GA","GB","GD","GE","GF","GG","GH","GI","GL","GM","GN","GP","GQ","GR","GS","GT","GU","GW","GY","HK","HM","HN","HR","HT","HU","ID","IE","IL","IM","IN","IO","IQ","IR","IS","IT","JE","JM","JO","JP","KE","KG","KH","KI","KM","KN","KP","KR","KW","KY","KZ","LA","LB","LC","LI","LK","LR","LS","LT","LU","LV","LY","MA","MC","MD","ME","MF","MG","MH","MK","ML","MM","MN","MO","MP","MQ","MR","MS","MT","MU","MV","MW","MX","MY","MZ","NA","NC","NE","NF","NG","NI","NL","NO","NP","NR","NU","NZ","OM","PA","PE","PF","PG","PH","PK","PL","PM","PN","PR","PS","PT","PW","PY","QA","RE","RO","RS","RU","RW","SA","SB","SC","SD","SE","SG","SH","SI","SJ","SK","SL","SM","SN","SO","SR","SS","ST","SV","SX","SY","SZ","TC","TD","TF","TG","TH","TJ","TK","TL","TM","TN","TO","TR","TT","TV","TW","TZ","UA","UG","UM","US","UY","UZ","VA","VC","VE","VG","VI","VN","VU","WF","WS","YE","YT","ZA","ZM","ZW"]
EXCEPTIONAL_RESERVATION_COUNTRY_CODES = ["AC","CP","DG","EA","EU","EZ","FX","IC","SU","TA","UK","UN"]
TRANSITIONAL_RESERVATION_COUNTRY_CODES = ["AN","BU","CS","NT","SF","TP","YU","ZR"]
INDETERMINATE_RESERVATION_COUNTRY_CODES = ["DY","EW","FL","JA","LF","PI","RA","RB","RB","RC","RH","RI","RL","RM","RN","RP","SF","WG","WL","WV","YV"]
NOT_USED_COUNTRY_CODES = ["AP","BX","EF","EM","EP","EV","GC","IB","OA","WO"]
DELETED_COUNTRY_CODES = ["AI","BQ","CT","DD","DY","FQ","GE","HV","JT","MI","NH","NQ","PC","PU","PZ","RH","SK","VD","WK","YD"]

class AgenciesParser(object):
    """ Agencies Profiles parser """
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.raw_collection = db[settings['MONGODB_RAW_COLLECTION']]

    def main(self):
        """ Main method to execute """
        # df1 = pd.DataFrame.from_dict(list(
        #     self.raw_collection.find({'provider': 'bing_partners'})))

        # df2 = pd.DataFrame.from_dict(list(
        #     self.raw_collection.find({'provider': 'hubspot_partners'})))
        
        # df3 = pd.DataFrame.from_dict(list(
        #     self.raw_collection.find({'provider': 'google_partners'})))

        # df3 = df3.rename(columns={
        #     'websiteUrl': 'website_url'
        # })    

        # for df in [df1, df2, df3]:
        #     df['domain'] = df['website_url'].map(get_domain)
        #     df.drop(columns=['_id'], inplace=True)
        #     df.set_index('domain')

        # df4 = pd.merge(
        #     df1, df2, on='domain', how='outer',
        #     suffixes=('_bing', '_hubspot'))
        
        # df5 = pd.merge(
        #     df3, df4, on='domain', how='outer',
        #     suffixes=('_google', ''))
        
        # print(df5.info())

        distinct_country_codes = self.raw_collection.find({'provider': 'google_partners'}).distinct('localizedInfos.countryCodes')
        print('Official country code count is ' + str(len(OFFICIAL_COUNTRY_CODES)))
        print('Agencies country code count is ' + str(len(distinct_country_codes)))
        matching_official = []
        for code in distinct_country_codes:
            if code in OFFICIAL_COUNTRY_CODES:
                matching_official.append(code)
            else:
                print(code + " is not an official country code.")
        print('Matching country codes count is ' + str(len(matching_official)))
        
        
if __name__ == '__main__':
    instance = AgenciesParser()
    instance.main()
