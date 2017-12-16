#encoding: utf-8
import re 

def add_to_dict_cnt(d, key):
    if not key in d:
        d[key] = 1
    else:
        d[key] += 1
        
def add_to_dict_list(d, key, value):
    if not key in d:
        d[key] = []
    d[key].append(value)

def add_values_to_dict_list(d, key, values):
    if not key in d:
        d[key] = []
    d[key].extend(values)
    
re_chinese = re.compile(ur'[\u4e00-\u9fa5]+$')
def is_chinese(text):
    if type(text) == str:
        text = text.decode('utf-8')
    return re_chinese.match(text) is not None

def is_chinese_char(uchar):
	if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
		return True
	else:
		return False

def is_no_chinese(text):
    if type(text) == str:
        text = text.decode('utf-8')
    for uchar in text:
        if is_chinese_char(uchar):
            return False
    return True



if __name__ == "__main__":
    import json
    s = u'Real Madrid Club de Fútbol '
    s = '中文'
    print is_chinese(s)
    print is_no_chinese(s)