#encoding:utf-8
import os
from ..IOUtil import result_dir, Print
import json
from ..mapping.name_mapping import del_space
import HTMLParser

delimeters = [u';', u'；', u'、', u'，']
html_parser = HTMLParser.HTMLParser()
def unfold(text):
    global delimeters, html_parser
    text = html_parser.unescape(text)
    max_sep = delimeters[0]
    for sep in delimeters:
        if len(text.split(sep)) > len(text.split(max_sep)):
            max_sep = sep
    values = text.split(max_sep)
    values = [del_space(x) for x in values]
    values = [x for x in values if x ]
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
            

        

if __name__ == "__main__":
    inpath = os.path.join(result_dir, 'test/entity_info.json')
    outpath = os.path.join(result_dir, 'test/entity_info_processed.json')

    inpath = os.path.join(result_dir, '360/360_entity_info.json')
    outpath = os.path.join(result_dir, '360/360_entity_info_processed.json')
    process(inpath, outpath)