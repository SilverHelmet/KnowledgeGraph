import base64
import glob
import HTMLParser
import json
import os
import re
import sys
from bs4 import BeautifulSoup
from ..IOUtil import result_dir

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
    
def parse_summary(obj):
    global html_parser
    summary = None
    if 'intro_info' in obj:
        intro_info = obj['intro_info']
        if 'summary' in intro_info:
            summary = intro_info['summary']
    if summary:
        return html_unescape(summary)
    else:
        return None

def parse_line(line):
    try:
        tokens = line.strip().split('\t')
        url = tokens[0]
        content = json.loads(base64.b64decode(tokens[1]))
        return url, content
    except Exception, e:
        return None, None
    

def strip_url(url):
    if url.startswith("http://"):
        url = url[len('http://'):]
    return url

def check_valid(attr):
    # if 'ename' in attr and 'title' in attr:
    #     if attr['ename'] != attr['title']:
    #         print "error: different name", attr['url'], attr['ename'], attr['title']
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
        if url is None:
            print "fatal error: parse_line error, ", line
            continue
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

def parse_text_from_html(html):
    ps = []
    try:
         t = BeautifulSoup(html, 'lxml')
    except Exception, e:
        print 'error at parse_text_from_html'
        print html
        return []

   
    p_list = t.find_all('p')
    for p_obj in p_list:
        text = html_unescape(p_obj.get_text()).strip()
        if text:
            ps.append(text)
    return ps

def parse_text(url, b64_content):
    ret = []
    try:
        obj = json.loads(base64.b64decode(b64_content))
    except Exception, e:
        print "error url", url
        return ret

    content = obj.get('content', {}).get("content", {})
    if type(content) is unicode:
        content = {'1': {'section_content': content}}
    for key in content:
        chapter = content[key]
        chapter_content = chapter.get('section_content', [])
        if type(chapter_content) == list:
            # print "section",  url
            for section in chapter_content:
                section_content = section.get('sub_section_content', '')
                ret.extend(parse_text_from_html(section_content))
        else:
            ret.extend(parse_text_from_html(chapter_content))
    return ret

def test():

    # url = 'http://baike.so.com/doc/3946206-4141203.html'
    content = 'eyJpbmZvX21vZGVsIjpbeyJtb2R1bGVfbmFtZSI6IiIsIm1vZHVsZV9zb3J0IjowLCJuYW1lIjoiXHU0ZTJkXHU2NTg3XHU1NDBkXHU3OWYwIiwibmlja19uYW1lIjoibmFtZUMiLCJ2YWx1ZSI6WyJcdTZiNGNcdTgyMWVcdTRmMGVcdTVlYTciXX0seyJtb2R1bGVfbmFtZSI6IiIsIm1vZHVsZV9zb3J0IjowLCJuYW1lIjoiXHU1OTE2XHU2NTg3XHU1NDBkXHU3OWYwIiwibmlja19uYW1lIjoibmFtZUUiLCJ2YWx1ZSI6WyJLYWJ1a2l6YSJdfSx7Im5hbWUiOiJcdTUyMWJcdTdhY2JcdTY1ZjZcdTk1ZjQiLCJuaWNrX25hbWUiOiJtb2RlbEN1c3RvbSIsInZhbHVlIjpbIjE5MTRcdTVlNzQiXX0seyJuYW1lIjoiXHU1NzMwXHUwMGEwXHUwMGEwXHUwMGEwXHUwMGEwXHU1NzQwIiwibmlja19uYW1lIjoibW9kZWxDdXN0b20iLCJ2YWx1ZSI6WyJcdTRlMWNcdTRlYWNcdTkwZmRcdTRlMmRcdTU5MmVcdTUzM2FcdTk0ZjZcdTVlYTc0LTEyLTE1Il19XSwiaW50cm9faW5mbyI6eyJ0aXRsZSI6Ilx1NmI0Y1x1ODIxZVx1NGYwZVx1NWVhNyIsImVudHJ5VHlwZSI6IjEiLCJzdW1tYXJ5IjoiXHU2YjRjXHU4MjFlXHU0ZjBlXHU1ZWE3XHU2NjJmXHU0ZjRkXHU0ZThlXHU0ZTFjXHU0ZWFjXHU5NGY2XHU1ZWE3XHU3Njg0XHU2YjRjXHU4MjFlXHU0ZjBlXHU0ZTEzXHU3NTI4XHU1MjY3XHU1NzNhXHVmZjBjMTkxNFx1NWU3NFx1OGQ3N1x1Njc3ZVx1N2FmOVx1NTcyOFx1NmI2NFx1NTIxYlx1NGUxYVx1MzAwMjE4ODlcdTVlNzQxMVx1NjcwODIxXHU2NWU1XHU1ZjAwXHU0ZTFhXHU0ZWU1XHU2NzY1XHVmZjBjXHU2NmZlXHU5MDZkXHU1M2Q3XHU3MDZiXHU3MDdlXHUzMDAxXHU2MjE4XHU3MDZiXHVmZjBjXHU1Mzg2XHU3ZWNmXHU2NTcwXHU2YjIxXHU3MGU3XHU2YmMxXHUzMDAxXHU1OTBkXHU1MTc0XHUzMDAxXHU2NTM5XHU1ZWZhXHVmZjBjXHU3M2IwXHU1NzI4XHU3Njg0XHU1ZWZhXHU3YjUxXHU1ZWZhXHU2MjEwXHU0ZThlMTk1MVx1NWU3NFx1MzAwMlx1Njg0M1x1NWM3MVx1NjVmNlx1NGVlM1x1OThjZVx1NjgzY1x1NzY4NFx1NzNiMFx1NmI0Y1x1ODIxZVx1NGYwZVx1NWVhN1x1ZmYwY1x1NWVmYVx1NjIxMFx1NTQwZVx1N2VjZlx1NTM4Nlx1NGU4NjUwXHU1ZTc0XHU1Mzg2XHU1M2YyXHVmZjBjXHU1ZGYyXHU4OGFiXHU1MjE3XHU0ZTNhXHU1NmZkXHU1YmI2XHU2NzA5XHU1ZjYyXHU2NTg3XHU1MzE2XHU5MDU3XHU0ZWE3XHVmZjBjXHU2NjJmXHU5ODg3XHU0ZTNhXHU3M2NkXHU4ZDM1XHU3Njg0XHU1ZWZhXHU3YjUxXHUzMDAyXHU1NzI4XHU4ZmM0XHU0ZWNhXHU0ZTNhXHU2YjYyMTAwXHU1ZTc0XHU1OTFhXHU1ZTc0XHU3Njg0XHU1YzgxXHU2NzA4XHVmZjBjXHU2YjY0XHU1NzMwXHU0ZTBkXHU2NWFkXHU0ZTBhXHU2ZjE0XHU2YjRjXHU4MjFlXHU0ZjBlXHVmZjBjXHU1NDBkXHU1MjZmXHU1MTc2XHU1YjllXHU1NzMwXHU0ZmRkXHU2MzAxXHU0ZTg2XHU2NzAwXHU1MTc3XHU0ZWUzXHU4ODY4XHU2MDI3XHU2YjRjXHU4MjFlXHU0ZjBlXHU1MjY3XHU1NzNhXHU3Njg0XHU1YjlkXHU1ZWE3XHUzMDAyIiwidXJsIjoiaHR0cDpcL1wvYmFpa2Uuc28uY29tXC9kb2NcLzQ3ODYxMzYtNTAwMjEyOC5odG1sIn0sImNvbnRlbnQiOnsiY29udGVudCI6IjxwPlx1NTQwZFx1NzlmMFx1NmI0Y1x1ODIxZVx1NGYwZVx1NWVhNzxcL3A+PHA+XHU2NWU1XHU4YmVkS2FidWtpemE8XC9wPjxwPlx1NTczMFx1NTc0MFx1NGUxY1x1NGVhY1x1OTBmZFx1NGUyZFx1NTkyZVx1NTMzYVx1OTRmNlx1NWVhNzQtMTItMTU8XC9wPjxwPlx1NGVhNFx1OTAxYVx1NjI0Ylx1NmJiNVx1NGUxY1x1NGVhY1x1NTczMFx1OTRjMVx1NjVlNVx1NmJkNFx1OGMzN1x1N2ViZlx1MzAwMVx1OTBmZFx1ODQyNVx1NmQ0NVx1ODM0OVx1N2ViZlx1NGUxY1x1OTRmNlx1NWVhN1x1N2FkOVx1NGUwYlx1OGY2Nlx1NTM3M1x1NTIzMFx1MzAwMlx1NGVjZVx1NGUxY1x1NGVhY1x1NTczMFx1OTRjMVx1NjVlNVx1NmJkNFx1OGMzN1x1N2ViZlx1MzAwMVx1OTRmNlx1NWVhN1x1N2ViZlx1OTRmNlx1NWVhN1x1N2FkOVx1NmI2NVx1ODg0YzVcdTUyMDZcdTk0OWZcdTMwMDI8XC9wPjxwPlx1OTVlOFx1Nzk2OFx1NTZlMFx1NTE2Y1x1NmYxNFx1ODI4Mlx1NzZlZVx1ODAwY1x1NWYwMjxcL3A+PHA+XHU2YjRjXHU4MjFlXHU0ZjBlXHU1ZWE3XHU2NjJmXHU0ZjRkXHU0ZThlXHU0ZTFjXHU0ZWFjXHU5NGY2XHU1ZWE3XHU3Njg0XHU2YjRjXHU4MjFlXHU0ZjBlXHU0ZTEzXHU3NTI4XHU1MjY3XHU1NzNhXHVmZjBjMTkxNFx1NWU3NFx1OGQ3N1x1Njc3ZVx1N2FmOVx1NTcyOFx1NmI2NFx1NTIxYlx1NGUxYVx1MzAwMjE4ODlcdTVlNzQxMVx1NjcwODIxXHU2NWU1XHU1ZjAwXHU0ZTFhXHU0ZWU1XHU2NzY1XHVmZjBjXHU2NmZlXHU5MDZkXHU1M2Q3XHU3MDZiXHU3MDdlXHUzMDAxXHU2MjE4XHU3MDZiXHVmZjBjXHU1Mzg2XHU3ZWNmXHU2NTcwXHU2YjIxXHU3MGU3XHU2YmMxXHUzMDAxXHU1OTBkXHU1MTc0XHUzMDAxXHU2NTM5XHU1ZWZhXHVmZjBjXHU3M2IwXHU1NzI4XHU3Njg0XHU1ZWZhXHU3YjUxXHU1ZWZhXHU2MjEwXHU0ZThlMTk1MVx1NWU3NFx1MzAwMlx1Njg0M1x1NWM3MVx1NjVmNlx1NGVlM1x1OThjZVx1NjgzY1x1NzY4NFx1NzNiMFx1NmI0Y1x1ODIxZVx1NGYwZVx1NWVhN1x1ZmYwY1x1NWVmYVx1NjIxMFx1NTQwZVx1N2VjZlx1NTM4Nlx1NGU4NjUwXHU1ZTc0XHU1Mzg2XHU1M2YyXHVmZjBjXHU1ZGYyXHU4OGFiXHU1MjE3XHU0ZTNhXHU1NmZkXHU1YmI2XHU2NzA5XHU1ZjYyXHU2NTg3XHU1MzE2XHU5MDU3XHU0ZWE3XHVmZjBjXHU2NjJmXHU5ODg3XHU0ZTNhXHU3M2NkXHU4ZDM1XHU3Njg0XHU1ZWZhXHU3YjUxXHUzMDAyXHU1NzI4XHU4ZmM0XHU0ZWNhXHU0ZTNhXHU2YjYyMTAwXHU1ZTc0XHU1OTFhXHU1ZTc0XHU3Njg0XHU1YzgxXHU2NzA4XHVmZjBjXHU2YjY0XHU1NzMwXHU0ZTBkXHU2NWFkXHU0ZTBhXHU2ZjE0XHU2YjRjXHU4MjFlXHU0ZjBlXHVmZjBjXHU1NDBkXHU1MjZmXHU1MTc2XHU1YjllXHU1NzMwXHU0ZmRkXHU2MzAxXHU0ZTg2XHU2NzAwXHU1MTc3XHU0ZWUzXHU4ODY4XHU2MDI3XHU2YjRjXHU4MjFlXHU0ZjBlXHU1MjY3XHU1NzNhXHU3Njg0XHU1YjlkXHU1ZWE3XHUzMDAyPFwvcD4ifSwiZW50cnlfZmVhdHVyZSI6eyJpZCI6IjM4OTM4ODUiLCJlaWQiOiI0Nzg2MTM2Iiwic2lkIjoiNTAwMjEyOCIsImVuYW1lIjoiXHU2YjRjXHU4MjFlXHU0ZjBlXHU1ZWE3Iiwic25hbWUiOiIiLCJ0eXBlX2lkIjoiMSIsImludHJvX2xlbiI6IjE3OSIsImludHJvX3BpYyI6IjAiLCJpbnRyb19waWNfdyI6IjAiLCJpbnRyb19waWNfaCI6IjAiLCJpbnRyb19saW5rIjoiMCIsIm1vZHVsZSI6IjQiLCJjb250ZW50X2xlbiI6IjI3MCIsImNvbnRlbnRfbGluayI6IjAiLCJjb250ZW50X2ltZyI6IjAiLCJjb250ZW50X2ltZ19pbnRybyI6IjAiLCJoMl9udW0iOiIwIiwiaDNfbnVtIjoiMCIsInJlZl9udW0iOiIwIiwiZnVyX251bSI6IjAiLCJ0YWdfbnVtIjoiMCIsInB2IjoiMCIsInVwZGF0ZXRpbWUiOiIyMDE1LTA3LTI3IDE5OjM1OjM5IiwiaXNfZXNzZW5jZSI6IjAiLCJpc19wZXJzb25hbF93aWRnZXRzIjoiMCIsImlzX3BhcnRuZXIiOiIwIiwiaXNfYmFpZHVfaW1wb3J0IjoiMCIsImlzX2JhaWtlX2VkaXQiOiIwIn0sImVudHJ5X2luZm8iOnsiZW5hbWUiOiJcdTZiNGNcdTgyMWVcdTRmMGVcdTVlYTciLCJ0eXBlX2lkIjoiMSIsIm5ld190eXBlcyI6IjEiLCJ1cmwiOiJodHRwOlwvXC9iYWlrZS5zby5jb21cL2RvY1wvNDc4NjEzNi01MDAyMTI4Lmh0bWwifX0='
    obj = json.loads(base64.b64decode(content))
    # print obj['content']
    content = obj.get('content', {}).get("content", {})
    if type(content) is unicode:
        content = {'1': {'section_content': content}}
    ret = []
    for key in content:
        chapter = content[key]
        chapter_content = chapter.get('section_content', [])
        if type(chapter_content) == list:
            print "section", 
            for section in chapter_content:
                section_content = section.get('sub_section_content', '')
                ret.extend(parse_text_from_html(section_content))
        else:
            ret.extend(parse_text_from_html(chapter_content))
    print "\n".join(ret)
            
        
    

    # key = '4'
    # print content[key]['section_content']
    # t = BeautifulSoup(content[key]['section_content'], 'lxml')
    # print '-' * 50
    # p_list = t.find_all('p')
    # for p_obj in p_list:
    #     print p_obj.get_text()

    # print html_unescape(content['1']['section_content'])

if __name__ == "__main__":
    test()
    # out_path = os.path.join(result_dir, '360/360_entity_info.json')
    # if not os.path.exists(os.path.dirname(out_path)):
    #     os.mkdir(os.path.dirname(out_path))
    # outf = file(out_path, 'w')
    # for filepath in glob.glob('data/360/*finish'):
    #     parse(filepath, outf)
    # outf.close()

    