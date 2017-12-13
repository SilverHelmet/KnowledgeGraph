#encoding: utf-8
import os
import json

from bs4 import BeautifulSoup
from tqdm import tqdm

from src.baike_process.parse import html_unescape
from src.IOUtil import rel_ext_dir, nb_lines_of, table_dir, Print


class ValueStorage:
    def __init__(self, size):
        self.value_lists = []
        self.list_idx = []
        for i in range(size):
            self.value_lists.append([])
            self.list_idx.append(0)

    def push(self, idx, value, times):
        for _ in range(times):
            self.value_lists[idx].append(value)

    def pop(self, idx):
        pos = self.list_idx[idx]
        self.list_idx[idx] += 1
        return self.value_lists[idx][pos]

    def has_value(self, idx):
        return self.list_idx[idx] != len(self.value_lists[idx])
            

def is_table(html):
    return html.startswith('<table') and html.endswith('</table>')

def parse_table(table):
    heads = table.find_all('thead')
    if len(heads) != 1:
        return None

    head = heads[0]
    columns = []
    for tr in head.find_all('th'):
        col = html_unescape(tr.get_text()).strip()
        columns.append(col)
    nb_cols = len(columns)

    tbody = table.find('tbody')
    if not tbody:
        return None
    
    rows = []
    storage = ValueStorage(nb_cols)
    for tr in tbody.find_all('tr'):
        row = []
        tds = tr.find_all('td')
        td_idx = 0
        for i in range(nb_cols):
            if not storage.has_value(i):
                td = tds[td_idx]
                td_idx += 1
                text = html_unescape(td.get_text()).strip()
                cnt = td.get('rowspan', "1")
                if int(td.get('colspan', "1")):
                    return None
                storage.push(i, text, int(cnt))
            row.append(storage.pop(i))
        rows.append(row)
    
    return {'columns': columns, 'rows': rows}





def parse_tables_from_html(html):
    soup = BeautifulSoup(html, 'lxml')
    rets = []
    tables = soup.find_all('table')
    for table in tables:
        ret = parse_table(table)
        if ret:
            rets.append(ret)
    return rets

def extract_table_columns():
    outpath = os.path.join(table_dir, 'table_column_count.tsv')
    outf = file(outpath, 'w')
    doc_path = os.path.join(rel_ext_dir, 'baike_doc.json')
    Print('count table\'s columns')
    for line in tqdm(file(doc_path), total = nb_lines_of(doc_path)):
        bk_url, doc = line.split('\t')
        doc = json.loads(doc)
        for title, chapter in doc:
            if type(chapter) is not unicode:
                continue
            try:
                tables = parse_tables_from_html(chapter)
                for table in tables:
                    outf.write('%s\t%s\t%s\n' %(bk_url, title, " # ".join(table['columns'])))
            except Exception, e:
                print 'error at parse %s title = %s' %(bk_url, title)
    outf.close()



def test():
    html = '<table><thead><tr><th width=\"110\">角色</th><th width=\"110\">演员</th><th width=\"200\">备注</th></tr></thead><tbody><tr><td>江阳</td><td><a target=\"_blank\" href=\"/doc/5785535-5998321.html\">曹磊</a></td><td>----</td></tr><tr><td>钱程</td><td><a target=\"_blank\" href=\"/doc/3456059-3636614.html\">刘雨涛</a></td><td>----</td></tr><tr><td>苏清</td><td><a target=\"_blank\" href=\"/doc/5429313-5667540.html\">冯静</a></td><td>----</td></tr><tr><td>赵娜</td><td><a target=\"_blank\" href=\"/doc/1181672-1250052.html\">陶飞霏</a></td><td>----</td></tr><tr><td>熊早</td><td><a target=\"_blank\" href=\"/doc/5394530-5631649.html\">任重</a></td><td>----</td></tr><tr><td>王一涤</td><td>黄超</td><td>----</td></tr><tr><td>孟大为</td><td>王馨苒</td><td>----</td></tr><tr><td>老托</td><td><a target=\"_blank\" href=\"/doc/5350510-5585966.html\">张晓龙</a></td><td>----</td></tr><tr><td>胡燕</td><td>刘一霏</td><td>----</td></tr><tr><td>曹红梅</td><td>王文娟</td><td>----</td></tr><tr><td>杨昕巍</td><td>刘红雨</td><td>----</td></tr><tr><td>宋志飞</td><td><a target=\"_blank\" href=\"/doc/1599671-1691007.html\">胡亚捷</a></td><td>----</td></tr><tr><td>张仲年</td><td><a target=\"_blank\" href=\"/doc/5425282-5663502.html\">郑乾龙</a></td><td>----</td></tr><tr><td>苏晗</td><td>陈颖</td><td>----</td></tr><tr><td>梅昕</td><td><a target=\"_blank\" href=\"/doc/5426206-5664428.html\">向梅</a></td><td>----</td></tr><tr><td>彭洁</td><td>庞敏</td><td>----</td></tr><tr><td>苏天</td><td><a target=\"_blank\" href=\"/doc/4157036-4357026.html\">石燕京</a></td><td>----</td></tr><tr><td>周军</td><td><a target=\"_blank\" href=\"/doc/5367311-5603071.html\">白凡</a></td><td>----</td></tr><tr><td colspan=\"3\"></td></tr><tr><td>梅兆龙</td><td>吴晓东</td><td>----</td></tr><tr><td>江父</td><td>郭杰</td><td>----</td></tr><tr><td>小江阳</td><td>娄少青</td><td>----</td></tr></tbody></table>"'
    tables =  parse_tables_from_html(html)
    for table in tables:
        print  " ".join(table['columns'])



    

if __name__ == "__main__":
    # test()
    extract_table_columns()
