#encoding: utf-8
import dateparser

time_strs = ['1962-10','1966年5月31']

for time_str in time_strs:
    print time_str
    result =  dateparser.parse(time_str, 
        languages = ['zh', 'en'],
        settings = {"PREFER_DAY_OF_MONTH":"first"} )
    print result

import datetime
