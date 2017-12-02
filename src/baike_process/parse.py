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

def parse_text_from_html(html, url, ignore_table):
    ps = []
    html = html.strip()
    try:
         t = BeautifulSoup(html, 'lxml')
    except Exception, e:
        print 
        print 'error at parse_text_from_html, url is', url
        return []

    if t.find('table'):
        if not ignore_table and html.startswith('<table') and html.endswith('</table>'):
            return html
        else:
            return html
        
    p_list = t.find_all('p')
    for p_obj in p_list:
        text = html_unescape(p_obj.get_text()).strip()
        if text:
            ps.append(text)
    return ps

def del_space(text):
    return text.replace(u'\xa0', '').replace(u'\u200b', '').strip()

def parse_text(url, b64_content, ignore_table):
    try:
        obj = json.loads(base64.b64decode(b64_content))
    except Exception, e:
        print "error url", url
        return {}

    ret = []
    summary = parse_summary(obj)
    if summary:
        ret.append(('intro_summary', summary.split('\n') ))
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
                texts = parse_text_from_html(section_content, url, ignore_table)
                if len(texts) > 0:
                    ret.append((title, texts))
        else:
            texts = parse_text_from_html(chapter_content, url, ignore_table)
            
            if len(texts) > 0:
                ret.append( (del_space(chapter_title), texts) )
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
    # s = "eyJpbmZvX21vZGVsIjpbeyJtb2R1bGVfbmFtZSI6IiIsIm1vZHVsZV9zb3J0IjowLCJuYW1lIjoiXHU0ZTJkXHU2NTg3XHU1NDBkXHU3OWYwIiwibmlja19uYW1lIjoibmFtZUMiLCJ2YWx1ZSI6WyJcdTlhNmNcdTZiNDdcdTVjMTRcdTUzYmYiXX0seyJtb2R1bGVfbmFtZSI6IiIsIm1vZHVsZV9zb3J0IjowLCJuYW1lIjoiXHU1OTE2XHU2NTg3XHU1NDBkXHU3OWYwIiwibmlja19uYW1lIjoibmFtZUUiLCJ2YWx1ZSI6WyJNYXJzaGFsbCBDb3VudHkiXX0seyJuYW1lIjoiXHU1NzMwXHU3NDA2XHU0ZjRkXHU3ZjZlIiwibmlja19uYW1lIjoibW9kZWxDdXN0b20iLCJ2YWx1ZSI6WyIgXHU3ZjhlXHU1NmZkXHU1YmM2XHU4OTdmXHU4OTdmXHU2YmQ0XHU1ZGRlXHU1MzE3XHU5MGU4ICJdfSx7Im5hbWUiOiJcdTk3NjJcdTc5ZWYiLCJuaWNrX25hbWUiOiJtb2RlbEN1c3RvbSIsInZhbHVlIjpbIiAxLDgzOFx1NWU3M1x1NjViOVx1NTE2Y1x1OTFjYyAiXX1dLCJpbnRyb19pbmZvIjp7InRpdGxlIjoiXHU5YTZjXHU2YjQ3XHU1YzE0XHU1M2JmIiwiZW50cnlUeXBlIjoiMSIsInN1bW1hcnkiOiJcdTlhNmNcdTZiNDdcdTVjMTRcdTUzYmYoTWFyc2hhbGwgQ291bnR5LCBNaXNzaXNzaXBwaSlcdTY2MmZcdTdmOGVcdTU2ZmRcdTViYzZcdTg5N2ZcdTg5N2ZcdTZiZDRcdTVkZGVcdTUzMTdcdTkwZThcdTc2ODRcdTRlMDBcdTRlMmFcd"
    # line = file('data/360_sample.data').readlines()[0]
    # baike_url, s = line.strip().split('\t')
    # print baike_url
    # content = json.loads(base64.b64decode(s))
    baike_url = 'http://baike.so.com/doc/10236800-10762138.html'
    s = 'eyJpbmZvX21vZGVsIjpbeyJtb2R1bGVfbmFtZSI6Ilx1NGUyYVx1NGViYVx1Njk4Mlx1NTFiNSIsIm1vZHVsZV9zb3J0Ijo4LCJuYW1lIjoiXHU1OTE2XHU2NTg3XHU1NDBkIiwibmlja19uYW1lIjoibmFtZUUiLCJ2YWx1ZSI6WyJMaXNhIERlbGllbiJdfSx7Im1vZHVsZV9uYW1lIjoiXHU0ZTJhXHU0ZWJhXHU4MGNjXHU2NjZmIiwibW9kdWxlX3NvcnQiOjIsIm5hbWUiOiJcdTgwNGNcdTRlMWEiLCJuaWNrX25hbWUiOiJjYXJlZXIiLCJ2YWx1ZSI6WyJcdTZmMTRcdTU0NTgiXX1dLCJpbnRyb19pbmZvIjp7InRpdGxlIjoiTGlzYSBEZWxpZW4iLCJlbnRyeVR5cGUiOiIwIiwic3VtbWFyeSI6Ikxpc2EgRGVsaWVuXHVmZjBjXHU2ZjE0XHU1NDU4XHVmZjBjXHU0ZTNiXHU4OTgxXHU0ZjVjXHU1NGMxXHUzMDBhU2FudGEgQ2xhd3NcdTMwMGJcdTMwMDFcdTMwMGFTY3JlYW0gUXVlZW5zJyBOYWtlZCBDaHJpc3RtYXNcdTMwMGJcdTMwMDJcdTRlM2JcdTg5ODFcdTRmNWNcdTU0YzFcdTc1MzVcdTVmNzFcdTRmNWNcdTU0YzFcdTRlMGFcdTY2MjBcdTY1ZjZcdTk1ZjRcdTUyNjdcdTU0MGRcdTYyNmVcdTZmMTRcdTg5ZDJcdTgyNzJcdTViZmNcdTZmMTRcdTRlM2JcdTZmMTRcdTYyYzVcdTRlZmJcdTgwNGNcdTUyYTExOTk2U2FudGEgQ2xhd3NNYXJ5IEphbmUgQXVzdGluXHU3ZWE2XHU3ZmYwXHUwMGI3QVx1MDBiN1x1OWM4MVx1N2QyMkRlYmJpZSBSb2Nob25cdWZmMGNHcmFudCBDcmFtZXJcdTZmMTRcdTU0NTgxOTk2U2NyZWFtIFF1ZWVucycgTmFrZWQgQ2hyaXN0bWFzSGVyc2VsZiAoYXMgTGlzYSBEdXZhdWwpXHU3ZWE2XHU3ZmYwXHUwMGI3QVx1MDBiN1x1OWM4MVx1N2QyMkdyYW50IENyYW1lclx1ZmYwY0RlYmJpZSBSb2Nob25cdTZmMTRcdTU0NThcdTRlYmFcdTcyNjlcdTUxNzNcdTdjZmJcdTU0MDhcdTRmNWNcdTUxNzNcdTdjZmJcdTRlYmFcdTcyNjlcdTU0MGRcdTc5ZjBcdTU0MDhcdTRmNWNcdTRmNWNcdTU0YzFcdTU0MDhcdTRmNWNcdTRlMjRcdTZiMjFcdTRlZTVcdTRlMGFcdTc2ODRcdTVmNzFcdTRlYmFEZWJiaWUgUm9jaG9uXHU1NDA4XHU0ZjVjXHU0ZjVjXHU1NGMxKDIpXHVmZjFhXHUzMDBhU2NyZWFtIFF1ZWVucyYjMzk7IE5ha2VkIENocmlzdG1hc1x1MzAwYlx1ZmYwY1x1MzAwYVNhbnRhIENsYXdzXHUzMDBiUy4gV2lsbGlhbSBIaW56bWFuXHU1NDA4XHU0ZjVjXHU0ZjVjXHU1NGMxKDIpXHVmZjFhXHUzMDBhU2NyZWFtIFF1ZWVucyYjMzk7IE5ha2VkIEMiLCJ1cmwiOiJodHRwOlwvXC9iYWlrZS5zby5jb21cL2RvY1wvMTAyMzY4MDAtMTA3NjIxMzguaHRtbCIsInNlY3Rpb24iOlt7InNlY3Rpb25UaXRsZSI6Ilx1NGUzYlx1ODk4MVx1NGY1Y1x1NTRjMSIsInNlY3Rpb25MaW5rX20iOiJodHRwOlwvXC9tLmJhaWtlLnNvLmNvbVwvZG9jXC8xMDIzNjgwMC5odG1sP3NpZD0xMDc2MjEzOCZhbmNob3I9MSMxMDIzNjgwMC0xMDc2MjEzOC0xIiwic2VjdGlvbkxpbmsiOiJodHRwOlwvXC9iYWlrZS5zby5jb21cL2RvY1wvMTAyMzY4MDAtMTA3NjIxMzguaHRtbCMxMDIzNjgwMC0xMDc2MjEzOC0xIn0seyJzZWN0aW9uVGl0bGUiOiJcdTRlYmFcdTcyNjlcdTUxNzNcdTdjZmIiLCJzZWN0aW9uTGlua19tIjoiaHR0cDpcL1wvbS5iYWlrZS5zby5jb21cL2RvY1wvMTAyMzY4MDAuaHRtbD9zaWQ9MTA3NjIxMzgmYW5jaG9yPTIjMTAyMzY4MDAtMTA3NjIxMzgtMiIsInNlY3Rpb25MaW5rIjoiaHR0cDpcL1wvYmFpa2Uuc28uY29tXC9kb2NcLzEwMjM2ODAwLTEwNzYyMTM4Lmh0bWwjMTAyMzY4MDAtMTA3NjIxMzgtMiJ9XX0sImNvbnRlbnQiOnsiY29udGVudCI6eyIxIjp7InNlY3Rpb25fdGl0bGUiOiJcdTRlM2JcdTg5ODFcdTRmNWNcdTU0YzEiLCJzZWN0aW9uX2NvbnRlbnQiOlt7InN1Yl9zZWN0aW9uX3RpdGxlIjoiXHU3NTM1XHU1ZjcxXHU0ZjVjXHU1NGMxIiwic3ViX3NlY3Rpb25fY29udGVudCI6Ijx0YWJsZT48dHI+PHRoIHdpZHRoPVwiNTJcIj5cdTRlMGFcdTY2MjBcdTY1ZjZcdTk1ZjQ8XC90aD48dGg+XHU1MjY3XHU1NDBkPFwvdGg+PHRoPlx1NjI2ZVx1NmYxNFx1ODlkMlx1ODI3MjxcL3RoPjx0aD5cdTViZmNcdTZmMTQ8XC90aD48dGg+XHU0ZTNiXHU2ZjE0PFwvdGg+PHRoPlx1NjJjNVx1NGVmYlx1ODA0Y1x1NTJhMTxcL3RoPjxcL3RyPjx0cj48dGQ+MTk5NjxcL3RkPjx0ZD5TYW50YSBDbGF3czxcL3RkPjx0ZD5NYXJ5IEphbmUgQXVzdGluPFwvdGQ+PHRkPlx1N2VhNlx1N2ZmMFx1MDBiN0FcdTAwYjdcdTljODFcdTdkMjI8XC90ZD48dGQ+RGViYmllIFJvY2hvblx1ZmYwY0dyYW50IENyYW1lcjxcL3RkPjx0ZD5cdTZmMTRcdTU0NTg8XC90ZD48XC90cj48dHI+PHRkPjE5OTY8XC90ZD48dGQ+U2NyZWFtIFF1ZWVucycgTmFrZWQgQ2hyaXN0bWFzPFwvdGQ+PHRkPkhlcnNlbGYgKGFzIExpc2EgRHV2YXVsKTxcL3RkPjx0ZD5cdTdlYTZcdTdmZjBcdTAwYjdBXHUwMGI3XHU5YzgxXHU3ZDIyPFwvdGQ+PHRkPkdyYW50IENyYW1lclx1ZmYwY0RlYmJpZSBSb2Nob248XC90ZD48dGQ+XHU2ZjE0XHU1NDU4PFwvdGQ+PFwvdHI+PFwvdGFibGU+In1dfSwiMiI6eyJzZWN0aW9uX3RpdGxlIjoiXHU0ZWJhXHU3MjY5XHU1MTczXHU3Y2ZiIiwic2VjdGlvbl9jb250ZW50IjoiPHRhYmxlPjx0cj48dGggd2lkdGg9XCI2MFwiPlx1NTQwOFx1NGY1Y1x1NTE3M1x1N2NmYjxcL3RoPjx0aCB3aWR0aD1cIjYwXCI+XHU0ZWJhXHU3MjY5XHU1NDBkXHU3OWYwPFwvdGg+PHRoPlx1NTQwOFx1NGY1Y1x1NGY1Y1x1NTRjMTxcL3RoPjxcL3RyPjx0cj48dGQgcm93c3Bhbj1cIjVcIj5cdTU0MDhcdTRmNWNcdTRlMjRcdTZiMjFcdTRlZTVcdTRlMGFcdTc2ODRcdTVmNzFcdTRlYmE8XC90ZD48dGQ+RGViYmllIFJvY2hvbjxcL3RkPjx0ZD48cD5cdTU0MDhcdTRmNWNcdTRmNWNcdTU0YzEoMilcdWZmMWE8XC9wPjxwPlx1MzAwYVNjcmVhbSBRdWVlbnMmIzM5OyBOYWtlZCBDaHJpc3RtYXNcdTMwMGJcdWZmMGNcdTMwMGFTYW50YSBDbGF3c1x1MzAwYjxcL3A+PFwvdGQ+PFwvdHI+PHRyPjx0ZD5TLiBXaWxsaWFtIEhpbnptYW48XC90ZD48dGQ+PHA+XHU1NDA4XHU0ZjVjXHU0ZjVjXHU1NGMxKDIpXHVmZjFhPFwvcD48cD5cdTMwMGFTY3JlYW0gUXVlZW5zJiMzOTsgTmFrZWQgQ2hyaXN0bWFzXHUzMDBiXHVmZjBjXHUzMDBhU2FudGEgQ2xhd3NcdTMwMGI8XC9wPjxcL3RkPjxcL3RyPjx0cj48dGQ+U3VlIEVsbGVuIFdoaXRlPFwvdGQ+PHRkPjxwPlx1NTQwOFx1NGY1Y1x1NGY1Y1x1NTRjMSgyKVx1ZmYxYTxcL3A+PHA+XHUzMDBhU2FudGEgQ2xhd3NcdTMwMGJcdWZmMGNcdTMwMGFTY3JlYW0gUXVlZW5zJiMzOTsgTmFrZWQgQ2hyaXN0bWFzXHUzMDBiPFwvcD48XC90ZD48XC90cj48dHI+PHRkPkFtYW5kYSBNYWRpc29uPFwvdGQ+PHRkPjxwPlx1NTQwOFx1NGY1Y1x1NGY1Y1x1NTRjMSgyKVx1ZmYxYTxcL3A+PHA+XHUzMDBhU2FudGEgQ2xhd3NcdTMwMGJcdWZmMGNcdTMwMGFTY3JlYW0gUXVlZW5zJiMzOTsgTmFrZWQgQ2hyaXN0bWFzXHUzMDBiPFwvcD48XC90ZD48XC90cj48dHI+PHRkPlx1N2VhNlx1N2ZmMFx1MDBiNyZuYnNwO0FcdTAwYjdcdTljODFcdTdkMjIgSm9obiBBLiBSdXNzbzxcL3RkPjx0ZD48cD5cdTU0MDhcdTRmNWNcdTRmNWNcdTU0YzEoMilcdWZmMWE8XC9wPjxwPlx1MzAwYVNjcmVhbSBRdWVlbnMmIzM5OyBOYWtlZCBDaHJpc3RtYXNcdTMwMGJcdWZmMGNcdTMwMGFTYW50YSBDbGF3c1x1MzAwYjxcL3A+PFwvdGQ+PFwvdHI+PFwvdGFibGU+In19fSwiZW50cnlfZmVhdHVyZSI6eyJpZCI6IjI1MjI4NDUyIiwiZWlkIjoiMTAyMzY4MDAiLCJzaWQiOiIxMDc2MjEzOCIsImVuYW1lIjoiTGlzYSBEZWxpZW4iLCJzbmFtZSI6IiIsInR5cGVfaWQiOiI1NSIsImludHJvX2xlbiI6IjY2IiwiaW50cm9fcGljIjoiMCIsImludHJvX3BpY193IjoiMCIsImludHJvX3BpY19oIjoiMCIsImludHJvX2xpbmsiOiIwIiwibW9kdWxlIjoiMiIsImNvbnRlbnRfbGVuIjoiNjEwIiwiY29udGVudF9saW5rIjoiMCIsImNvbnRlbnRfaW1nIjoiMCIsImNvbnRlbnRfaW1nX2ludHJvIjoiMCIsImgyX251bSI6IjIiLCJoM19udW0iOiIxIiwicmVmX251bSI6IjEiLCJmdXJfbnVtIjoiMCIsInRhZ19udW0iOiIzIiwicHYiOiIwIiwidXBkYXRldGltZSI6IjIwMTUtMDctMjcgMTc6MTc6MjgiLCJpc19lc3NlbmNlIjoiMCIsImlzX3BlcnNvbmFsX3dpZGdldHMiOiIwIiwiaXNfcGFydG5lciI6IjAiLCJpc19iYWlkdV9pbXBvcnQiOiIwIiwiaXNfYmFpa2VfZWRpdCI6IjAifSwiZW50cnlfaW5mbyI6eyJlbmFtZSI6Ikxpc2EgRGVsaWVuIiwidHlwZV9pZCI6IjU1Iiwic25hbWUiOiIiLCJuZXdfdHlwZXMiOiIxNSIsInVybCI6Imh0dHA6XC9cL2JhaWtlLnNvLmNvbVwvZG9jXC8xMDIzNjgwMC0xMDc2MjEzOC5odG1sIn19'
    # obj = json.loads(base64.b64decode(s))['content']['content']
    # print obj.keys()
    # print obj['1']['section_title']
    # print obj['2']['section_content']
    text = parse_text(baike_url, s, False)
    print type(text)
    for title, paras in text:
        print title
        if type(paras) is unicode:
            print paras
        else:
            for s in paras:
                print s
    # print content['intro_info']['summary']
    # out_path = os.path.join(result_dir, '360/360_entity_info.json')
    # if not os.path.exists(os.path.dirname(out_path)):
    #     os.mkdir(os.path.dirname(out_path))
    # outf = file(out_path, 'w')
    # for filepath in glob.glob('data/360/*finish'):
    #     parse(filepath, outf)
    # outf.close()

    