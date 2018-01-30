#encoding: utf-8
# import dateparser
import re

class FBDatetime:
    date_p = re.compile(r'(?P<year>-?\d{1,4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$')
    year_p = re.compile(r'(?P<year>-?\d{1,4})$')
    yearmonth_p = re.compile(r'(?P<year>-?\d{1,4})-(?P<month>\d{1,2})$')
    datetime_p = re.compile(r'(?P<year>-?\d{1,4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})T(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})\.(?P<msec>\d+)Z$')
    def __init__(self, year, month = 0, day = 0, hour = -1, minute = -1, second = -1, msec = -1):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.msec = msec
    
    
    @staticmethod
    def parse_fb_datetime(time_str):
        if type(time_str) is unicode:
            time_str = time_str.encode('utf-8')
        p = time_str.split('^^')
        if len(p) != 2:
            return None
        date_type = p[1]
        
        value = p[0]
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        args = {}
        if date_type == "<http://www.w3.org/2001/XMLSchema#date>":
            match = FBDatetime.date_p.match(value)
            if match is None:
                # print "\nerror", time_str
                return None
            args['year'] = int(match.group('year'))
            args['month'] = int(match.group('month'))
            args['day'] = int(match.group('day'))
        elif date_type == "<http://www.w3.org/2001/XMLSchema#gYear>":
            match = FBDatetime.year_p.match(value)
            if match is None:
                # print "\nerror", time_str
                return None
            args['year'] = int(match.group('year'))
        elif date_type == '<http://www.w3.org/2001/XMLSchema#gYearMonth>':
            match = FBDatetime.yearmonth_p.match(value)
            if match is None:
                # print "\nerror", time_str
                return None
            args['year'] = int(match.group('year'))
            args['month'] = int(match.group('month'))
        elif date_type == "<http://www.w3.org/2001/XMLSchema#dateTime>":
            match = FBDatetime.datetime_p.match(value)
            if match is None:
                # print "\nerror", time_str
                return None
            args['year'] = int(match.group('year'))
            args['month'] = int(match.group('month'))
            args['day'] = int(match.group('day'))
            args['hour'] = int(match.group('hour'))
            args['second'] = int(match.group('second'))
            args['msec'] = int(match.group('msec'))
        else:
            # print "error date type", time_str
            return None
        return FBDatetime(**args)

    def __str__(self):
        return "%d-%d-%d %d:%d:%d.%d" %(self.year, self.month, self.day, self.hour, self.minute, self.second, self.msec)

    def date_str(self):
        return "%d-%d-%d" %(self.year, self.month, self.day)

def year_month_checker(args):
    return args['year'] > 12

class BaikeDatetime:
    date_p = re.compile(ur'(?P<year>-?\d{1,4})(-|年|/|\.)(?P<month>\d{1,2})(-|月|/|\.)(?P<day>\d{1,2})(日)?')
    year_p = re.compile(ur'(?P<year>-?\d{1,4})年')
    year_p_2 = re.compile(ur'(?P<year>\d{4,4})')
    yearmonth_p = re.compile(ur'(?P<year>-?\d{1,4})(-|年|\.)(?P<month>\d{1,2})(月)?')
    yearmonth_p_2 = re.compile(ur'(?P<year>-?\d{2,4})(-|年|\.)(?P<month>\d{1,2})(月)?')
    month_day_p = re.compile(ur'(?P<month>\d{1,2})月(?P<day>\d{1,2})(日)?')
    def __init__(self, year, month = 0, day = 0):
        self.year = year
        self.month = month
        self.day = day
    
    def __str__(self):
        return "%d-%d-%d" %(self.year, self.month, self.day)

    @staticmethod
    def parse(time_str, strict = False, search_mod = False):
        if type(time_str) is str:
            time_str = time_str.decode('utf-8')
        args = {}
        if not strict:
            patterns = [BaikeDatetime.date_p, BaikeDatetime.yearmonth_p, BaikeDatetime.year_p, BaikeDatetime.year_p_2, BaikeDatetime.month_day_p]
            pattern_names = [['year', 'month', 'day'],
                            ['year', 'month'],
                            ['year'],
                            ['year'],
                            ['month', 'day']]
            checkers = [None, None, None, None, None]
        else:
            patterns = [BaikeDatetime.date_p, BaikeDatetime.yearmonth_p_2, BaikeDatetime.year_p, BaikeDatetime.month_day_p]
            pattern_names = [['year', 'month', 'day'],
                            ['year', 'month'],
                            ['year'],
                            ['month', 'day']]
                            
            checkers =[None,
                None,
                None,
               year_month_checker] 

        match_flag = False
        for pattern, names, checker in zip(patterns, pattern_names, checkers):
            match = pattern.match(time_str)
            if match and not search_mod and match.group() != time_str:
                match = None
            if match:
                match_flag = True
                for name in names:
                    args[name] = int(match.group(name))
                if checker is None or checker(args):
                    break
                else:
                    return None
        # if not match_flag:
        #     try:
        #         result =  dateparser.parse(time_str, 
        #         languages = ['zh', 'en'],
        #         settings = {"PREFER_DAY_OF_MONTH":"first"} )
        #         if result is not None:
        #             args['year'], args['month'], args['day'] = result.year, result.month, result.day
        #             match_flag = True
        #             print "dateparser", args, time_str
        #     except Exception, e:
        #         pass
        #         # print "\nException", e
        #         # print "\n dataparser error ", time_str
        if match_flag:
            if not 'year' in args:
                args['year'] = 0
            return BaikeDatetime(**args)
        else:
            return None
    



if __name__ == "__main__":
    # values = ['"2009-09-24"^^<http://www.w3.org/2001/XMLSchema#date>',
    #      '"-2001"^^<http://www.w3.org/2001/XMLSchema#gYear>', 
    #      '"-2006-02"^^<http://www.w3.org/2001/XMLSchema#gYearMonth>', 
    #      '"1975-05-15T22:00:00.000Z"^^<http://www.w3.org/2001/XMLSchema#dateTime>', 
    #      '"-0269-07"^^<http://www.w3.org/2001/XMLSchema#gYear>']
    # for value in values:
    #     d = FBDatetime.parse_fb_datetime(value)
    #     print d

    #values = [u'2003年8月26日', u'2003年8', '2003', u'2003年8月', u'2003年', '203-8', u'1916年', u'公元前485年10月',u'1972.6.23', u'12.9', u'1971/02/05']
    values = [u'1961年9月27']
    for value in values:
        print "str", value
        d = BaikeDatetime.parse(value, strict = True, search_mod = True)
        print "time", d

    values = [u'\"1961-09-27\"^^<http://www.w3.org/2001/XMLSchema#date>']
    for value in values:
        d = FBDatetime.parse_fb_datetime(value)
        print d.date_str()

    
        
    


