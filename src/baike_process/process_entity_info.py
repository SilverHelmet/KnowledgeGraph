#encoding:utf-8
import os
from ..IOUtil import result_dir, Print
import json
from ..mapping.name_mapping import del_space
import HTMLParser
import re

delimeters = [u';', u'；', u'、', u'，']
html_parser = HTMLParser.HTMLParser()
bracket_pattern = re.compile(ur'（.*）|\(.*\)')


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
    


def unfold(text):
    global delimeters, html_parser
    text = html_parser.unescape(text)
    max_sep = delimeters[0]
    for sep in delimeters:
        if len(text.split(sep)) > len(text.split(max_sep)):
            max_sep = sep
    values = text.split(max_sep)
    values = [del_space(x) for x in values]

    values_2 = []
    for value in values:
        values_2.extend(unfold_bracket(value))
    values = values_2

    values = [del_book_bracket(x) for x in values]
    values = [x.strip() for x in values if x.strip()]
    return values

        
    

def process(inpath, outpath):
    outf = file(outpath, 'w')
    for cnt, line in enumerate(file(inpath), start =1):
        if cnt % 100000 == 0:
            Print("process cnt = %d" %cnt)
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
            

        

if __name__ == "__main__":
    inpath = os.path.join(result_dir, 'test/entity_info.json')
    outpath = os.path.join(result_dir, 'test/entity_info_processed.json')

    inpath = os.path.join(result_dir, '360/360_entity_info.json')
    outpath = os.path.join(result_dir, '360/360_entity_info_processed.json')
    process(inpath, outpath)