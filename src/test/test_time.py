#encoding: utf-8
import dateparser


for time_str in time_strs:
    print time_str
    print dateparser.parse(time_str, 
        languages = ['zh'],
        date_formats = [u'%Y年%m月'],
        settings = {"PREFER_DAY_OF_MONTH":"first"} )

import datetime
