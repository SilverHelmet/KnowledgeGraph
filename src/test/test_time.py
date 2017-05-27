#encoding: utf-8
import dateparser

time_strs = ['1962']

for time_str in time_strs:
    print time_str
    print dateparser.parse(time_str, 
        languages = ['zh', 'en'],
        settings = {"PREFER_DAY_OF_MONTH":"first"} )

import datetime
