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
    t = BeautifulSoup(html, 'lxml')
    p_list = t.find_all('p')
    for p_obj in p_list:
        text = html_unescape(p_obj.get_text()).strip()
        if text:
            ps.append(text)
    return ps

def parse_text(url, b64_content):
    ret = []
    try:
        obj = json.loads(base64.b64decode(content))
    except Exception, e:
        print "error url", url
        return ret

    content = obj.get('content', {}).get("content", {})
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
    return ret

def test():

    url = 'http://baike.so.com/doc/3946206-4141203.html'
    content = 'eyJpbmZvX21vZGVsIjpbeyJtb2R1bGVfbmFtZSI6IiIsIm1vZHVsZV9zb3J0IjowLCJuYW1lIjoiXHU0ZTJkXHU2NTg3XHU1NDBkXHU3OWYwIiwibmlja19uYW1lIjoibmFtZUMiLCJ2YWx1ZSI6WyJcdTY2MWZcdTRlNGJcdTUzNjFcdTZiZDRcdTgwMDFcdTlmMjBcdThmZGJcdTY1M2IiXX0seyJtb2R1bGVfbmFtZSI6IiIsIm1vZHVsZV9zb3J0IjowLCJuYW1lIjoiXHU1OTE2XHU2NTg3XHU1NDBkXHU3OWYwIiwibmlja19uYW1lIjoibmFtZUUiLCJ2YWx1ZSI6WyJLaXJieTogTW91c2UgQXR0YWNrIl19LHsibmFtZSI6Ilx1NmUzOFx1NjIwZlx1NGVhN1x1NTczMCIsIm5pY2tfbmFtZSI6Im1vZGVsQ3VzdG9tIiwidmFsdWUiOlsiXHU2YjI3XHU2ZDMyIl19LHsibmFtZSI6Ilx1NmUzOFx1NjIwZlx1N2M3Ylx1NTc4YiIsIm5pY2tfbmFtZSI6Im1vZGVsQ3VzdG9tIiwidmFsdWUiOlsiQUNUIl19XSwiaW50cm9faW5mbyI6eyJ0aXRsZSI6Ilx1NjYxZlx1NGU0Ylx1NTM2MVx1NmJkNFx1ODAwMVx1OWYyMFx1OGZkYlx1NjUzYiIsImVudHJ5VHlwZSI6IjEiLCJzdW1tYXJ5IjoiXHU2ZTM4XHU2MjBmXHU0ZmUxXHU2MDZmXHU2ZTM4XHU2MjBmXHU1NDBkXHU3OWYwOlx1NjYxZlx1NGU0Ylx1NTM2MVx1NmJkNFx1ODAwMVx1OWYyMFx1OGZkYlx1NjUzYlx1NmUzOFx1NjIwZlx1NTM5Zlx1NTQwZDpLaXJieTogTW91c2UgQXR0YWNrXHU2ZTM4XHU2MjBmXHU3YzdiXHU1NzhiOkFDVFx1NmUzOFx1NjIwZlx1NGVhN1x1NTczMDpcdTZiMjdcdTZkMzJcdTUzZDFcdTg4NGNcdTUzODJcdTU1NDY6TmludGVuZG9cdTZlMzhcdTYyMGZcdTViYjlcdTkxY2Y6NTEyXHU1YjU4XHU2ODYzXHU3YzdiXHU1NzhiOkVlcHJvbSAtIDY0IGtiaXRcdTZlMzhcdTYyMGZcdThiZWRcdThhMDA6XHU2Y2Q1XHU4YmVkIC0gXHU4MmYxXHU4YmVkIC0gXHU1ZmI3XHU4YmVkIC0gXHU2MTBmXHU1OTI3XHU1MjI5XHU4YmVkIC0gXHU4OTdmXHU3M2VkXHU3MjU5XHU4YmVkXHU2ZTM4XHU2MjBmXHU3NTNiXHU5NzYyOjJEXHU2ZTM4XHU2MjBmXHU1ZTczXHU1M2YwOk5EU1x1NmUzOFx1NjIwZlx1NTE4NVx1NWJiOVx1MzAwYVx1NjYxZlx1NGU0Ylx1NTM2MVx1NmJkNFx1ODAwMVx1OWYyMFx1OGZkYlx1NjUzYlx1MzAwYlx1NjYyZlx1NmIyN1x1NmQzMlx1NmUzOFx1NjIwZlx1NTIzNlx1OTAyMFx1NTU0Nk5pbnRlbmRvXHU1MTZjXHU1M2Y4XHU1MjM2XHU0ZjVjXHU3Njg0XHU0ZTAwXHU2YjNlXHU1MmE4XHU0ZjVjXHU2ZTM4XHU2MjBmXHUzMDAyXHU2ZTM4XHU2MjBmXHU2NTQ1XHU0ZThiXHU4YmIyXHU4ZmYwXHU3Njg0XHU2NjJmXHVmZjBjXHU3M2E5XHU1YmI2XHU2M2E3XHU1MjM2XHU3Njg0XHU1MzYxXHU2YmQ0XHU1NDhjM1x1NTNlYVx1NWMwZlx1ODAwMVx1OWYyMFx1ZmYwY1x1NWY1M1x1NzEzNlx1OGZkOFx1NjcwOVx1NGVkNlx1NGVlY1x1NzY4NFx1NTZlMlx1OTU3Zlx1NGU0Ylx1OTVmNFx1NzY4NFx1NjU0NVx1NGU4Ylx1ZmYwY1x1NzNhOVx1NWJiNlx1NzY4NFx1NzZlZVx1NjgwN1x1NjYyZlx1NTQ4Y1x1NTQ1MFx1NTU4YVx1NTZlMlx1NGU4OVx1NTkzYVx1NGUwMFx1NGUyYVx1Nzk1ZVx1NzlkOFx1NWI5ZFx1NzZkMlx1MzAwMlx1NTcyOE5EU1x1NGUwYVx1NzY3Ylx1NWY1NVx1NzY4NFx1NmUzOFx1NjIwZlx1NjViMFx1NTg5ZVx1NGU4Nlx1NGUwZFx1NWMxMVx1NzY4NFx1OTA1M1x1NTE3N1x1NGVlNVx1NTNjYVx1NjViMFx1NzY4NFx1NzI3OVx1NjI4MFx1ZmYwY1x1NTE3Nlx1NGY1OVx1NjViOVx1OTc2Mlx1NTQ4Y0dCQVx1NGUwYVx1NzY4NFx1NGU1Zlx1NmNhMVx1NTkxYVx1NTkyN1x1NTMzYVx1NTIyYlx1NGU4Nlx1ZmYwY1x1NTM3M1x1NGY3Zlx1NjYyZlx1NjViMFx1NzNhOVx1NWJiNlx1NGU1Zlx1NWY4OFx1NWJiOVx1NjYxM1x1NGUwYVx1NjI0Ylx1MzAwMiIsInVybCI6Imh0dHA6XC9cL2JhaWtlLnNvLmNvbVwvZG9jXC80Nzg1NzM0LTUwMDE3MjYuaHRtbCIsInNlY3Rpb24iOlt7InNlY3Rpb25UaXRsZSI6Ilx1NmUzOFx1NjIwZlx1NGZlMVx1NjA2ZiIsInNlY3Rpb25MaW5rX20iOiJodHRwOlwvXC9tLmJhaWtlLnNvLmNvbVwvZG9jXC80Nzg1NzM0Lmh0bWw/c2lkPTUwMDE3MjYmYW5jaG9yPTEjNDc4NTczNC01MDAxNzI2LTEiLCJzZWN0aW9uTGluayI6Imh0dHA6XC9cL2JhaWtlLnNvLmNvbVwvZG9jXC80Nzg1NzM0LTUwMDE3MjYuaHRtbCM0Nzg1NzM0LTUwMDE3MjYtMSJ9LHsic2VjdGlvblRpdGxlIjoiXHU2ZTM4XHU2MjBmXHU1MTg1XHU1YmI5Iiwic2VjdGlvbkxpbmtfbSI6Imh0dHA6XC9cL20uYmFpa2Uuc28uY29tXC9kb2NcLzQ3ODU3MzQuaHRtbD9zaWQ9NTAwMTcyNiZhbmNob3I9MiM0Nzg1NzM0LTUwMDE3MjYtMiIsInNlY3Rpb25MaW5rIjoiaHR0cDpcL1wvYmFpa2Uuc28uY29tXC9kb2NcLzQ3ODU3MzQtNTAwMTcyNi5odG1sIzQ3ODU3MzQtNTAwMTcyNi0yIn1dfSwiY29udGVudCI6eyJjb250ZW50Ijp7IjEiOnsic2VjdGlvbl90aXRsZSI6Ilx1NmUzOFx1NjIwZlx1NGZlMVx1NjA2ZiIsInNlY3Rpb25fY29udGVudCI6IjxwPlx1NmUzOFx1NjIwZlx1NTQwZFx1NzlmMDpcdTY2MWZcdTRlNGJcdTUzNjFcdTZiZDRcdTgwMDFcdTlmMjBcdThmZGJcdTY1M2I8XC9wPjxwPlx1NmUzOFx1NjIwZlx1NTM5Zlx1NTQwZDpLaXJieTogTW91c2UgQXR0YWNrPFwvcD48cD5cdTZlMzhcdTYyMGZcdTdjN2JcdTU3OGI6QUNUPGEgaHJlZj1cImh0dHA6XC9cL3A2LnFobXNnLmNvbVwvdDAxYmM0ZGQ4YzkzYWNhYjA5Ny5qcGdcIiAgY2xhc3M9XCJzaG93LWltZyBsYXlvdXRyaWdodFwiIGRhdGEtdHlwZT1cImdhbGxlcnlcIj48c3BhbiBjbGFzcz1cInNob3ctaW1nLWhkXCIgIHN0eWxlPVwid2lkdGg6MjIwcHg7aGVpZ2h0OjMzMXB4O1wiPjxpbWcgaWQ9XCJpbWdfODgzNjc0MFwiICB0aXRsZT1cIlx1NjYxZlx1NGU0Ylx1NTM2MVx1NmJkNFx1ODAwMVx1OWYyMFx1OGZkYlx1NjUzYlwiIGFsdD1cIlx1NjYxZlx1NGU0Ylx1NTM2MVx1NmJkNFx1ODAwMVx1OWYyMFx1OGZkYlx1NjUzYlwiIGRhdGEtaW1nPVwibW9kX2ltZ1wiIGRhdGEtc3JjPVwiaHR0cDpcL1wvcDYucWhtc2cuY29tXC9kclwvMjIwX19cL3QwMWJjNGRkOGM5M2FjYWIwOTcuanBnXCIgIHN0eWxlPVwid2lkdGg6MjIwcHg7aGVpZ2h0OjMzMXB4O1wiIFwvPjxcL3NwYW4+PHNwYW4gY2xhc3M9XCJzaG93LWltZy1iZFwiPlx1NjYxZlx1NGU0Ylx1NTM2MVx1NmJkNFx1ODAwMVx1OWYyMFx1OGZkYlx1NjUzYjxcL3NwYW4+PFwvYT48XC9wPjxwPlx1NmUzOFx1NjIwZlx1NGVhN1x1NTczMDpcdTZiMjdcdTZkMzI8XC9wPjxwPlx1NTNkMVx1ODg0Y1x1NTM4Mlx1NTU0NjpOaW50ZW5kbzxcL3A+PHA+XHU2ZTM4XHU2MjBmXHU1YmI5XHU5MWNmOjUxMjxcL3A+PHA+XHU1YjU4XHU2ODYzXHU3YzdiXHU1NzhiOkVlcHJvbSAtIDY0IGtiaXQ8XC9wPjxwPlx1NmUzOFx1NjIwZlx1OGJlZFx1OGEwMDpcdTZjZDVcdThiZWQgLSBcdTgyZjFcdThiZWQgLSBcdTVmYjdcdThiZWQgLSBcdTYxMGZcdTU5MjdcdTUyMjlcdThiZWQgLSBcdTg5N2ZcdTczZWRcdTcyNTlcdThiZWQ8XC9wPjxwPlx1NmUzOFx1NjIwZlx1NzUzYlx1OTc2MjoyRDxcL3A+PHA+XHU2ZTM4XHU2MjBmXHU1ZTczXHU1M2YwOk5EUzxcL3A+In0sIjIiOnsic2VjdGlvbl90aXRsZSI6Ilx1NmUzOFx1NjIwZlx1NTE4NVx1NWJiOSIsInNlY3Rpb25fY29udGVudCI6IjxwPlx1MzAwYVx1NjYxZlx1NGU0Ylx1NTM2MVx1NmJkNFx1ODAwMVx1OWYyMFx1OGZkYlx1NjUzYlx1MzAwYlx1NjYyZlx1NmIyN1x1NmQzMlx1NmUzOFx1NjIwZlx1NTIzNlx1OTAyMFx1NTU0Nk5pbnRlbmRvXHU1MTZjXHU1M2Y4XHU1MjM2XHU0ZjVjXHU3Njg0XHU0ZTAwXHU2YjNlXHU1MmE4XHU0ZjVjXHU2ZTM4XHU2MjBmXHUzMDAyXHU2ZTM4XHU2MjBmXHU2NTQ1XHU0ZThiXHU4YmIyXHU4ZmYwXHU3Njg0XHU2NjJmXHVmZjBjXHU3M2E5XHU1YmI2XHU2M2E3XHU1MjM2XHU3Njg0XHU1MzYxXHU2YmQ0XHU1NDhjM1x1NTNlYVx1NWMwZlx1ODAwMVx1OWYyMFx1ZmYwY1x1NWY1M1x1NzEzNlx1OGZkOFx1NjcwOVx1NGVkNlx1NGVlY1x1NzY4NFx1NTZlMlx1OTU3Zlx1NGU0Ylx1OTVmNFx1NzY4NFx1NjU0NVx1NGU4Ylx1ZmYwY1x1NzNhOVx1NWJiNlx1NzY4NFx1NzZlZVx1NjgwN1x1NjYyZlx1NTQ4Y1x1NTQ1MFx1NTU4YVx1NTZlMlx1NGU4OVx1NTkzYVx1NGUwMFx1NGUyYVx1Nzk1ZVx1NzlkOFx1NWI5ZFx1NzZkMlx1MzAwMjxcL3A+PHA+XHU1NzI4TkRTXHU0ZTBhXHU3NjdiXHU1ZjU1XHU3Njg0XHU2ZTM4XHU2MjBmXHU2NWIwXHU1ODllXHU0ZTg2XHU0ZTBkXHU1YzExXHU3Njg0XHU5MDUzXHU1MTc3XHU0ZWU1XHU1M2NhXHU2NWIwXHU3Njg0XHU3Mjc5XHU2MjgwXHVmZjBjXHU1MTc2XHU0ZjU5XHU2NWI5XHU5NzYyXHU1NDhjR0JBXHU0ZTBhXHU3Njg0XHU0ZTVmXHU2Y2ExXHU1OTFhXHU1OTI3XHU1MzNhXHU1MjJiXHU0ZTg2XHVmZjBjXHU1MzczXHU0ZjdmXHU2NjJmXHU2NWIwXHU3M2E5XHU1YmI2XHU0ZTVmXHU1Zjg4XHU1YmI5XHU2NjEzXHU0ZTBhXHU2MjRiXHUzMDAyPFwvcD4ifX19LCJlbnRyeV9mZWF0dXJlIjp7ImlkIjoiMzg5MjAyNCIsImVpZCI6IjQ3ODU3MzQiLCJzaWQiOiI1MDAxNzI2IiwiZW5hbWUiOiJcdTY2MWZcdTRlNGJcdTUzNjFcdTZiZDRcdTgwMDFcdTlmMjBcdThmZGJcdTY1M2IiLCJzbmFtZSI6IiIsInR5cGVfaWQiOiI0MiIsImludHJvX2xlbiI6IjAiLCJpbnRyb19waWMiOiIwIiwiaW50cm9fcGljX3ciOiIwIiwiaW50cm9fcGljX2giOiIwIiwiaW50cm9fbGluayI6IjAiLCJtb2R1bGUiOiI0IiwiY29udGVudF9sZW4iOiIzMjAiLCJjb250ZW50X2xpbmsiOiIwIiwiY29udGVudF9pbWciOiIxIiwiY29udGVudF9pbWdfaW50cm8iOiI0IiwiaDJfbnVtIjoiMiIsImgzX251bSI6IjAiLCJyZWZfbnVtIjoiMCIsImZ1cl9udW0iOiIwIiwidGFnX251bSI6IjAiLCJwdiI6IjAiLCJ1cGRhdGV0aW1lIjoiMjAxNS0wNy0yNyAxOTozNTozOCIsImlzX2Vzc2VuY2UiOiIwIiwiaXNfcGVyc29uYWxfd2lkZ2V0cyI6IjAiLCJpc19wYXJ0bmVyIjoiMCIsImlzX2JhaWR1X2ltcG9ydCI6IjAiLCJpc19iYWlrZV9lZGl0IjoiMCJ9LCJlbnRyeV9pbmZvIjp7ImVuYW1lIjoiXHU2NjFmXHU0ZTRiXHU1MzYxXHU2YmQ0XHU4MDAxXHU5ZjIwXHU4ZmRiXHU2NTNiIiwidHlwZV9pZCI6IjQyIiwibmV3X3R5cGVzIjoiNzgyIiwidXJsIjoiaHR0cDpcL1wvYmFpa2Uuc28uY29tXC9kb2NcLzQ3ODU3MzQtNTAwMTcyNi5odG1sIn19'
    obj = json.loads(base64.b64decode(content))
    # print obj['content']
    content = obj.get('content', {}).get("content", {})
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

    