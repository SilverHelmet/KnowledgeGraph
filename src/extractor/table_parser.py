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
    for th in head.find_all('th'):
        if int(th.get('colspan', "1")) > 1:
            return None
        col = html_unescape(th.get_text()).strip()
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
                if td_idx == len(tds):
                    return None
                td = tds[td_idx]
                td_idx += 1
                if int(td.get('colspan', "1")) > 1:
                    return None
                text = html_unescape(td.get_text()).strip()
                cnt = td.get('rowspan', "1")
                storage.push(i, text, int(cnt))
            if not storage.has_value(i):
                return None
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
    html = '<table><thead><tr><th><p>年份</p></th><th><p>作品</p></th><th><p>角色</p></th></tr></thead><tbody><tr><td width=\"0\"><p>2004</p></td><td width=\"0\"><p><a target=\"_blank\" href=\"/doc/1352581-1429974.html\">真实游戏</a>Game Box 1.0</p></td><td width=\"0\"><p>Michelle</p></td></tr><tr><td width=\"0\" height=\"0\" align=\"left\" valign=\"center\" colspan=\"0\" rowspan=\"2\"><div class=\"para\">2007</div></td><td width=\"0\" align=\"left\" valign=\"center\"><div class=\"para\">Final Approach</div></td><td width=\"0\" align=\"left\" valign=\"center\"><div class=\"para\">Agent Harris</div></td></tr><tr><td width=\"0\"><p>夺命保姆While the Children Sleep</p></td><td width=\"0\"><p>Abby Reed</p></td></tr><tr><td width=\"0\"><p>2010</p></td><td width=\"0\"><p>没有主人，没有上帝No God, No Master</p></td><td width=\"0\"><p>Louise Berger</p></td></tr></tbody></table>"], ["表演作品_电视剧作品", "<table><thead><tr><th><p>年份</p></th><th><p>作品</p></th><th colspan=\"0\" width=\"63\"><p>角色</p></th></tr></thead><tbody><tr><td rowspan=\"0\" colspan=\"0\" width=\"0\"><p>2008-2010</p></td><td rowspan=\"0\" colspan=\"0\" width=\"0\"><p><a target=\"_blank\" href=\"/doc/5369175.html\">真爱如血</a><strong>True Blood</strong></p></td><td rowspan=\"0\" colspan=\"0\" width=\"143\"><p>Lorena Krasiki</p></td></tr><tr><td width=\"0\" height=\"52\" align=\"left\" valign=\"center\" colspan=\"1\" rowspan=\"1\">2013</td><td width=\"0\" height=\"52\" align=\"left\" valign=\"center\" colspan=\"1\" rowspan=\"1\">蛇蝎女佣，魔鬼女佣</td><td width=\"0\" height=\"52\" align=\"left\" valign=\"center\" colspan=\"1\" rowspan=\"1\"><div class=\"para\">Peri Westmore</div></td></tr><tr><td rowspan=\"1\" colspan=\"1\"><p>2014</p></td><td rowspan=\"1\" colspan=\"1\">跟踪者Stalker</td><td rowspan=\"1\" colspan=\"1\">Janice Lawrence<br /> </td></tr></tbody></table>'
    tables =  parse_tables_from_html(html)
    for table in tables:
        print  " ".join(table['columns'])



    

if __name__ == "__main__":
    test()
    extract_table_columns()
