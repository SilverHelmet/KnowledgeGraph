from ..IOUtil import result_dir
import sys
import os
import base64
import json
import glob
import re
import HTMLParser
html_parser = HTMLParser.HTMLParser()
reload(sys)
sys.setdefaultencoding('utf-8')

def parse_info_value(info_values):
    global html_parser
    # to do
    # parse multi value in one slot
    info_values = [html_unescape(x) for x in info_values]
    return info_values        

def parse_entity_info(info_list):
    infos = {}
    for info in info_list:
        name = info['name']
        value = parse_info_value(info['value'])
        infos[name] = value
    return infos

url_pattern = re.compile(r'http://baike\.so\.com/doc/(?P<eid>\d+)-(?P<sid>\d+)\.html')
def parse_id_from_url(url):
    global url_pattern
    match = url_pattern.match(url)
    if match:
        return int(match.group('eid')), int(match.group('sid'))
    else:
        return -1, -1

def html_unescape(html_str):
    global html_parser
    if html_str:
        html_str = html_parser.unescape(html_str)
    return html_str

def parse_ename(obj):
    global html_parser
    ename = None
    if 'entry_feature' in obj:
        ename = obj['entry_feature'].get('ename')
    if not ename and 'entry_info' in obj:
        ename = obj['entry_info'].get('ename')
    return html_unescape(ename)

def parse_title(obj):
    global html_parser
    title = None
    if 'intro_info' in obj and type(obj['intro_info']) == dict:
        title = obj['intro_info']['title']
    return html_unescape(title)
    
    

def parse_line(line):
    tokens = line.strip().split('\t')
    url = tokens[0]
    content = json.loads(base64.b64decode(tokens[1]))
    return url, content

def strip_url(url):
    if url.startswith("http://"):
        url = url[len('http://'):]
    return url

def check_valid(attr):
    if 'ename' in attr and 'title' in attr:
        if attr['ename'] != attr['title']:
            print "error: different name", attr['url'], attr['ename'], attr['title']
    if not 'title' in attr or not 'ename' in attr:
        print 'fatal error: no name', attr['url']
        return False
    return True
    
        
def parse(filepath, outf):
    print "parse file [%s]" %os.path.basename(filepath)
    cnt = 0
    for line in file(filepath):
        cnt += 1
        url, obj = parse_line(line)
        attr = {'url': url}

        ename = parse_ename(obj)
        if ename:
            attr['ename'] = ename

        title = parse_title(obj)
        if 'intro_info' in obj and type(obj['intro_info']) == dict:
            attr['title'] = obj['intro_info']['title']
        attr['info'] = parse_entity_info(obj.get('info_model', []))

        if check_valid(attr):
            outf.write(strip_url(url) + "\t" + json.dumps(attr, ensure_ascii = False) + '\n')

if __name__ == "__main__":
    out_path = os.path.join(result_dir, '360/360_entity_info.json')
    if not os.path.exists(os.path.dirname(out_path)):
        os.mkdir(os.path.dirname(out_path))
    outf = file(out_path, 'w')
    for filepath in glob.glob('data/360/*finish'):
        parse(filepath, outf)
    outf.close()
