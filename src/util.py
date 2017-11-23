#encoding: utf-8
import re 

def add_to_dict_list(d, key, value):
    if not key in d:
        d[key] = []
    d[key].append(value)

re_chinese = re.compile(ur'[\u4e00-\u9fa5]+$')
def is_chinese(text):
    if type(text) == str:
        text = text.decode('utf-8')
    return re_chinese.match(text) is not None

if __name__ == "__main__":
    import json
    s = u'塞維利亞足球俱樂部'
    print is_chinese(s)