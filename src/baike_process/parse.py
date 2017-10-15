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
        while True:
            new_html_str = html_parser.unescape(html_str)
            if new_html_str == html_str:
                return html_str
            else:
                html_str = new_html_str
    else:
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
        if type(intro_info) is not dict:
            return None
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
    elif url.startswith("https://"):
        url = url[len('https://'):]
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

def parse_text_from_html(html, url):
    ps = []
    try:
         t = BeautifulSoup(html, 'lxml')
    except Exception, e:
        print 
        print 'error at parse_text_from_html, url is', url
        return []

    if t.find('table'):
        return []
        
    p_list = t.find_all('p')
    for p_obj in p_list:
        text = html_unescape(p_obj.get_text()).strip()
        if text:
            ps.append(text)
    return ps

def del_space(text):
    return text.replace(u'\xa0', '').replace(u'\u200b', '').strip()

def parse_text(url, b64_content):
    try:
        obj = json.loads(base64.b64decode(b64_content))
    except Exception, e:
        print "error url", url
        return {}

    ret = {}
    summary = parse_summary(obj)
    if summary:
        ret['intro_summary'] = [summary.split('\n')]
    content = obj.get('content', {}).get("content", {})
    if type(content) is unicode:
        content = {'1': {'section_content': content, 'section_title': "faked title"}}
    for key in content:
        chapter = content[key]
        chapter_content = chapter.get('section_content', [])
        chapter_title = chapter['section_title']
        if type(chapter_content) == list:
            # print "section",  url
            for section in chapter_content:
                section_content = section.get('sub_section_content', '')
                if section_content == "":
                    continue
                title = chapter_title + "_" + section['sub_section_title']
                title = del_space(title)
                texts = parse_text_from_html(section_content, url)
                if len(texts) > 0:
                    ret[title] = texts
        else:
            texts = parse_text_from_html(chapter_content, url)
            
            if len(texts) > 0:
                ret[del_space(chapter_title)] = texts
    return ret

# def test():

#     url = 'http://baike.so.com/doc/3946206-4141203.html'
#     content = ''
#     obj = json.loads(base64.b64decode(content))
#     # print obj['content']
#     content = obj.get('content', {}).get("content", {})
#     if type(content) is unicode:
#         content = {'1': {'section_content': content}}
#     ret = []
#     for key in content:
#         chapter = content[key]
#         chapter_content = chapter.get('section_content', [])
#         if type(chapter_content) == list:
#             for section in chapter_content:
#                 section_content = section.get('sub_section_content', '')
#                 ret.extend(parse_text_from_html(section_content))
#         else:
#             print chapter_content
#             ret.extend(parse_text_from_html(chapter_content))
#     print len(ret)
            
        
    

    # key = '4'
    # print content[key]['section_content']
    # t = BeautifulSoup(content[key]['section_content'], 'lxml')
    # print '-' * 50
    # p_list = t.find_all('p')
    # for p_obj in p_list:
    #     print p_obj.get_text()

    # print html_unescape(content['1']['section_content'])

if __name__ == "__main__":
    s = "eyJpbnRyb19pbmZvIjp7InRpdGxlIjoiXHU1MjE4XHU1ZmI3XHU1MzRlIiwiZW50cnlUeXBlIjoiMSIsInN1bW1hcnkiOiJcdTMwMGFcdTUyMThcdTVmYjdcdTUzNGVcdTMwMGJcdTY2MmYyMDAwXHU1ZTc0XHU2NWIwXHU3NTg2XHU5NzUyXHU1YzExXHU1ZTc0XHU1MWZhXHU3MjQ4XHU3OTNlXHU1MWZhXHU3MjQ4XHU3Njg0XHU1NmZlXHU0ZTY2XHUzMDAyXHU3YjgwXHU0ZWNiXHU1MjE4XHU1ZmI3XHU1MzRlIFx1ZmYwY1x1NjU4N1x1NzMyZVx1N2M3Ylx1NTc4YjpcdTRlMTNcdTg0NTcgXHVmZjBjXHU1MWZhXHU3MjQ4XHUzMDAxXHU1M2QxXHU4ODRjXHU4MDA1OiBcdTY1YjBcdTc1ODZcdTk3NTJcdTVjMTFcdTVlNzRcdTUxZmFcdTcyNDhcdTc5M2UgXHVmZjBjXHU1MWZhXHU3MjQ4XHU1M2QxXHU4ODRjXHU2NWY2XHU5NWY0OjIwMDBcdTY3NjVcdTZlOTBcdTY1NzBcdTYzNmVcdTVlOTM6XHU5OTg2XHU4NWNmXHU0ZTJkXHU2NTg3XHU4ZDQ0XHU2ZTkwIFx1ZmYwY1x1NjI0MFx1NjcwOVx1OTg5OFx1NTQwZDogXHU1MTc2XHU0ZWQ2XHU5ODk4XHU1NDBkXHU0ZmUxXHU2MDZmIDogXHU5OGNlXHU5NzYxXHU0ZTI0XHU1Y2I4XHU0ZTA5XHU1NzMwXHU1OTI5XHU3MzhiXHU1ZGU4XHU2NjFmIFx1ZmYwY1x1NjgwN1x1OGJjNlx1NTNmNzogSVNCTiA6IDctNTM3MS0zNjg4LTIgXHVmZjBjXHU1MWZhXHU3MjQ4XHUzMDAxXHU1M2QxXHU4ODRjXHU1NzMwOiBcdTRlNGNcdTljODFcdTY3MjhcdTlmNTAgXHVmZjBjXHU1MTczXHU5NTJlXHU4YmNkOiBcdTUyMThcdTVmYjdcdTUzNGUtLS0oMTk2MS0gKS0tLVx1NzUxZlx1NWU3M1x1NGU4Ylx1OGZmOS0tLVx1NjQ0NFx1NWY3MVx1OTZjNiBcdTUyMThcdTVmYjdcdTUzNGUtLS0oMTk2MS0gKSBcdWZmMGNcdThiZWRcdTc5Y2Q6IENoaW5lc2UgXHU2YzQ5XHU4YmVkIFx1ZmYwY1x1NTIwNlx1N2M3YjogXHU0ZTJkXHU1NmZlXHU1MjA2XHU3YzdiIDogSzgyNS43PTc2IFx1ZmYwY1x1NGUxYlx1N2YxNlx1OTg5OFx1NTQwZDogMjAwMFx1NWY3MVx1ODljNlx1NmI0Y1x1NjcwMFx1N2VhMlx1NGUxYlx1NGU2NiBcdWZmMGNcdThmN2RcdTRmNTNcdTVmNjJcdTYwMDE6IDFcdTUxOGMgXHUzMDAyIFx1NTE4NVx1NWJiOVx1NjcyY1x1NGU2Nlx1NGVlNVx1NTZmZVx1NzI0N1x1NzY4NFx1NWY2Mlx1NWYwZlx1NGVjYlx1N2VjZFx1NGU4Nlx1OTk5OVx1NmUyZlx1NWY3MVx1ODljNlx1NmI0Y1x1NjYxZlx1NTIxOFx1NWZiN1x1NTM0ZVx1NzY4NFx1NGUyYVx1NGViYVx1NWMwZlx1Njg2M1x1Njg0OFx1MzAwMiIsInVybCI6Imh0dHA6XC9cL2JhaWtlLnNvLmNvbVwvZG9jXC8xMjg3OTE4LTI0OTU2NTc3Lmh0bWwiLCJzZWN0aW9uIjpbeyJzZWN0aW9uVGl0bGUiOiJcdTdiODBcdTRlY2IiLCJzZWN0aW9uTGlua19tIjoiaHR0cDpcL1wvbS5iYWlrZS5zby5jb21cL2RvY1wvMTI4NzkxOC5odG1sP3NpZD0yNDk1NjU3NyZhbmNob3I9MSMxMjg3OTE4LTI0OTU2NTc3LTEiLCJzZWN0aW9uTGluayI6Imh0dHA6XC9cL2JhaWtlLnNvLmNvbVwvZG9jXC8xMjg3OTE4LTI0OTU2NTc3Lmh0bWwjMTI4NzkxOC0yNDk1NjU3Ny0xIn0seyJzZWN0aW9uVGl0bGUiOiJcdTUxODVcdTViYjkiLCJzZWN0aW9uTGlua19tIjoiaHR0cDpcL1wvbS5iYWlrZS5zby5jb21cL2RvY1wvMTI4NzkxOC5odG1sP3NpZD0yNDk1NjU3NyZhbmNob3I9MiMxMjg3OTE4LTI0OTU2NTc3LTIiLCJzZWN0aW9uTGluayI6Imh0dHA6XC9cL2JhaWtlLnNvLmNvbVwvZG9jXC8xMjg3OTE4LTI0OTU2NTc3Lmh0bWwjMTI4NzkxOC0yNDk1NjU3Ny0yIn1dfSwiY29udGVudCI6eyJjb250ZW50Ijp7IjEiOnsic2VjdGlvbl90aXRsZSI6Ilx1N2I4MFx1NGVjYiIsInNlY3Rpb25fY29udGVudCI6IjxwPlx1NTIxOFx1NWZiN1x1NTM0ZSBcdWZmMGNcdTY1ODdcdTczMmVcdTdjN2JcdTU3OGI6XHU0ZTEzXHU4NDU3IFx1ZmYwY1x1NTFmYVx1NzI0OFx1MzAwMVx1NTNkMVx1ODg0Y1x1ODAwNTogXHU2NWIwXHU3NTg2XHU5NzUyXHU1YzExXHU1ZTc0XHU1MWZhXHU3MjQ4XHU3OTNlIFx1ZmYwY1x1NTFmYVx1NzI0OFx1NTNkMVx1ODg0Y1x1NjVmNlx1OTVmNDoyMDAwPFwvcD48cD5cdTY3NjVcdTZlOTBcdTY1NzBcdTYzNmVcdTVlOTM6XHU5OTg2XHU4NWNmXHU0ZTJkXHU2NTg3XHU4ZDQ0XHU2ZTkwIFx1ZmYwY1x1NjI0MFx1NjcwOVx1OTg5OFx1NTQwZDogXHU1MTc2XHU0ZWQ2XHU5ODk4XHU1NDBkXHU0ZmUxXHU2MDZmIDogXHU5OGNlXHU5NzYxXHU0ZTI0XHU1Y2I4XHU0ZTA5XHU1NzMwXHU1OTI5XHU3MzhiXHU1ZGU4XHU2NjFmIFx1ZmYwY1x1NjgwN1x1OGJjNlx1NTNmNzogSVNCTiA6IDctNTM3MS0zNjg4LTIgXHVmZjBjXHU1MWZhXHU3MjQ4XHUzMDAxXHU1M2QxXHU4ODRjXHU1NzMwOiBcdTRlNGNcdTljODFcdTY3MjhcdTlmNTAgXHVmZjBjXHU1MTczXHU5NTJlXHU4YmNkOiBcdTUyMThcdTVmYjdcdTUzNGUtLS0oMTk2MS0gKS0tLVx1NzUxZlx1NWU3M1x1NGU4Ylx1OGZmOS0tLVx1NjQ0NFx1NWY3MVx1OTZjNiBcdTUyMThcdTVmYjdcdTUzNGUtLS0oMTk2MS0gKSBcdWZmMGNcdThiZWRcdTc5Y2Q6IENoaW5lc2UgXHU2YzQ5XHU4YmVkIFx1ZmYwY1x1NTIwNlx1N2M3YjogXHU0ZTJkXHU1NmZlXHU1MjA2XHU3YzdiIDogSzgyNS43PTc2IFx1ZmYwY1x1NGUxYlx1N2YxNlx1OTg5OFx1NTQwZDogMjAwMFx1NWY3MVx1ODljNlx1NmI0Y1x1NjcwMFx1N2VhMlx1NGUxYlx1NGU2NiBcdWZmMGNcdThmN2RcdTRmNTNcdTVmNjJcdTYwMDE6IDFcdTUxOGMgXHUzMDAyIDxcL3A+In0sIjIiOnsic2VjdGlvbl90aXRsZSI6Ilx1NTE4NVx1NWJiOSIsInNlY3Rpb25fY29udGVudCI6IjxwPlx1NjcyY1x1NGU2Nlx1NGVlNVx1NTZmZVx1NzI0N1x1NzY4NFx1NWY2Mlx1NWYwZlx1NGVjYlx1N2VjZFx1NGU4Nlx1OTk5OVx1NmUyZlx1NWY3MVx1ODljNlx1NmI0Y1x1NjYxZlx1NTIxOFx1NWZiN1x1NTM0ZVx1NzY4NFx1NGUyYVx1NGViYVx1NWMwZlx1Njg2M1x1Njg0OFx1MzAwMiA8XC9wPiJ9fX0sImVudHJ5X2ZlYXR1cmUiOnsiaWQiOiI1ODg0NDYyOSIsImVpZCI6IjEyODc5MTgiLCJzaWQiOiIyNDk1NjU3NyIsImVuYW1lIjoiXHU1MjE4XHU1ZmI3XHU1MzRlIiwic25hbWUiOiJcdTY1YjBcdTc1ODZcdTk3NTJcdTVjMTFcdTVlNzRcdTUxZmFcdTcyNDhcdTc5M2VcdTUxZmFcdTcyNDhcdTc2ODRcdTg0NTdcdTRmNWMiLCJ0eXBlX2lkIjoiMSIsImludHJvX2xlbiI6IjI1IiwiaW50cm9fcGljIjoiMCIsImludHJvX3BpY193IjoiMCIsImludHJvX3BpY19oIjoiMCIsImludHJvX2xpbmsiOiIwIiwibW9kdWxlIjoiMCIsImNvbnRlbnRfbGVuIjoiNDA2IiwiY29udGVudF9saW5rIjoiMCIsImNvbnRlbnRfaW1nIjoiMCIsImNvbnRlbnRfaW1nX2ludHJvIjoiMCIsImgyX251bSI6IjIiLCJoM19udW0iOiIwIiwicmVmX251bSI6IjEiLCJmdXJfbnVtIjoiMCIsInRhZ19udW0iOiIxIiwicHYiOiIwIiwidXBkYXRldGltZSI6IjIwMTctMDEtMjggMTY6MTQ6NTkiLCJpc19lc3NlbmNlIjoiMCIsImlzX3BlcnNvbmFsX3dpZGdldHMiOiIwIiwiaXNfcGFydG5lciI6IjAiLCJpc19iYWlkdV9pbXBvcnQiOiIwIiwiaXNfYmFpa2VfZWRpdCI6IjAifSwiZW50cnlfaW5mbyI6eyJlbmFtZSI6Ilx1NTIxOFx1NWZiN1x1NTM0ZSIsInR5cGVfaWQiOiIxIiwibmV3X3R5cGVzIjoiIiwidXJsIjoiaHR0cDpcL1wvYmFpa2Uuc28uY29tXC9kb2NcLzEyODc5MTgtMjQ5NTY1NzcuaHRtbCJ9fQ=="
    content = json.loads(base64.b64decode(s))
    print content['intro_info']['summary']
    # out_path = os.path.join(result_dir, '360/360_entity_info.json')
    # if not os.path.exists(os.path.dirname(out_path)):
    #     os.mkdir(os.path.dirname(out_path))
    # outf = file(out_path, 'w')
    # for filepath in glob.glob('data/360/*finish'):
    #     parse(filepath, outf)
    # outf.close()

    