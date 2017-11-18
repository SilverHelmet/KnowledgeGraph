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
    s = r'{"fb:type.object.type": ["fb:dataworld.information_source"], "fb:type.object.name": ["\"Fertility rate, Demographic Indicators, Vietnam, General Statistics Office of Vietnam\"@en", "\"Fertility rate, Demographic Indicators, Vietnam, General Statistics Office of Vietnam\"@en", "\"Fertility rate, Demographic Indicators, Vietnam, General Statistics Office of Vietnam\"@en"]}'
    o = json.loads(s)
    names = o['fb:type.object.name']
    print len(names), names
    names = set(names)
    print len(names), sorted(names)