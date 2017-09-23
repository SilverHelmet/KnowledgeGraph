#encoding:utf-8
import os
from ..IOUtil import result_dir, Print, nb_lines_of
import json
from ..mapping.name_mapping import del_space
import HTMLParser
import re
from tqdm import tqdm

delimeters = [u';', u'；', u'、', u'，', u',']
html_parser = HTMLParser.HTMLParser()
bracket_pattern = re.compile(ur'（.*）|\(.*\)')
digits = set([u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9'])
text = u'2,627,000'
def unfold_bracket(value):
    global bracket_pattern
    match = bracket_pattern.search(value)
    if match:
        st, ed  = match.span(0)
        v1 = value[:st] + value[ed:]
        v2 = value[st+1:ed-1]
        return [v1, v2]
    else:
        return [value]

def del_book_bracket(value):
    if value.startswith(u'《') and value.endswith(u'》'):
        return value[1:-1]
    elif value.startswith(u'<<') and value.endswith(u'>>'):
        return value[2:-2]
    else:
        return value

def not_digit(text, pos):
    global digits
    if pos < 0 or pos >= len(text):
        return True
    return not text[pos] in digits

def unfold(text):
    global delimeters, html_parser
    text = html_parser.unescape(text)
    max_sep = delimeters[0]
    pos = text.find(u',')
    if pos != -1 and not_digit(text, pos-1) and not_digit(text, pos+1):
        candidate = delimeters
    else:
        candidate = delimiters[:-1]

    for sep in candidate:
        if len(text.split(sep)) > len(text.split(max_sep)):
            max_sep = sep
    if max_sep == u',':
        print 'unfold', text
    values = text.split(max_sep)
    values = [del_space(x) for x in values]

    values_2 = []
    for value in values:
        values_2.extend(unfold_bracket(value))
    values = values_2

    # values = [del_book_bracket(x) for x in values]
    values = [x.strip() for x in values if x.strip()]
    return values

        
    

def process(inpath, outpath, total = None):
    if total is None:
        total = nb_lines_of(inpath)
    outf = file(outpath, 'w')
    for line in tqdm(file(inpath), total = total):
        baike_key, obj = line.split('\t')
        obj = json.loads(obj)
        if 'ename' in obj:
            obj['ename'] = html_parser.unescape(obj['ename'])
        if 'title' in obj:
            obj['title'] = html_parser.unescape(obj['title'])
        if 'info' in obj:
            info = obj.get('info')
            new_info = {}
            for name in info:
                values = info[name]
                new_name = del_space(name).replace(" ", "")
                new_values = []
                for value in values:
                    new_values.extend(unfold(value))
                new_info[new_name] = new_values
            obj['info'] = new_info
        
        outf.write('%s\t%s\n' %(baike_key, json.dumps(obj, ensure_ascii = False)))
    outf.close()
            
def ignore_baike_name_attr(baike_entity_info, baike_name_attrs, url):
    # global o_name_cnt
    baike_info = baike_entity_info[url]
    names = set()
    if 'ename' in baike_info:
        names.update(baike_info['ename'])
    if 'title' in baike_info:
        names.update(baike_info['title'])

    for name in baike_name_attrs:
        if name in baike_info:
            names.update(baike_info[name])

    o_name_attr = set()
    for name in baike_info:
        for value in baike_info[name]:
            if value in names:
                o_name_attr.add(name)

    for o_name in o_name_attr:
        # if not o_name in o_name_cnt:
        #     o_name_cnt[o_name] = 0
        # o_name_cnt[o_name] += 1
        baike_info.pop(o_name)

    return baike_info
        

if __name__ == "__main__":
    inpath = os.path.join(result_dir, 'test/entity_info.json')
    outpath = os.path.join(result_dir, 'test/entity_info_processed.json')

    inpath = os.path.join(result_dir, '360/360_entity_info.json')
    outpath = os.path.join(result_dir, '360/360_entity_info_processed.json')
    process(inpath, outpath, 21710208)