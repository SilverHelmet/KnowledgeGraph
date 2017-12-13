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
                td = tds[td_idx]
                td_idx += 1
                text = html_unescape(td.get_text()).strip()
                cnt = td.get('rowspan', "1")
                if int(td.get('colspan', "1")) > 1:
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
    html = '<table><thead><tr><th colspan=\"4\" width=\"0\"><br /> </th><th colspan=\"3\" width=\"0\"><p>投篮</p></th><th colspan=\"3\" width=\"0\"><p>3分球</p></th><th colspan=\"3\" width=\"0\"><p>罚球</p></th><th colspan=\"3\" width=\"0\"><p>篮板</p></th><th colspan=\"6\" width=\"0\"><p>其他</p></th></tr></thead><tbody><tr><th><p>赛季</p></th><th><p>球队</p></th><th><p>场次</p></th><th><p>时间</p></th><th><p>投中</p></th><th><p>出手</p></th><th><p>命中率</p></th><th><p>投中</p></th><th><p>出手</p></th><th><p>命中率</p></th><th><p>投中</p></th><th><p>出手</p></th><th><p>命中率</p></th><th><p>进攻</p></th><th><p>防守</p></th><th><p>总计</p></th><th><p>助攻</p></th><th><p>失误</p></th><th><p>抢断</p></th><th><p>盖帽</p></th><th><p>犯规</p></th><th><p><em>得分</em></p></th></tr><tr><td><p>2002-03</p></td><td><p>老鹰</p></td><td><p>29</p></td><td><p>09:24</p></td><td><p>0.7</p></td><td><p>1.5</p></td><td><p>45.2</p></td><td><p>0</p></td><td><p>0</p></td><td><p>0</p></td><td><p>0.6</p></td><td><p>1</p></td><td><p>60.7</p></td><td><p>0.3</p></td><td><p>0.8</p></td><td><p>1.1</p></td><td><p>1.2</p></td><td><p>0.5</p></td><td><p>0.3</p></td><td><p>0.1</p></td><td><p>0.9</p></td><td><p><em>1.9</em></p></td></tr><tr><td><p>2004-05</p></td><td><p>尼克斯</p></td><td><p>21</p></td><td><p>11:00</p></td><td><p>0.8</p></td><td><p>1.6</p></td><td><p>51.5</p></td><td><p>0</p></td><td><p>0.1</p></td><td><p>0</p></td><td><p>0.4</p></td><td><p>0.6</p></td><td><p>61.5</p></td><td><p>0.1</p></td><td><p>1</p></td><td><p>1.1</p></td><td><p>1.1</p></td><td><p>0.5</p></td><td><p>0.3</p></td><td><p>0.1</p></td><td><p>1.2</p></td><td><p><em>2</em></p></td></tr><tr><td><p>2005-06</p></td><td><p><a href=\"/doc/1692895-1790058.html\" target=\"_blank\">雄鹿</a></p></td><td><p>30</p></td><td><p>06:42</p></td><td><p>0.4</p></td><td><p>0.9</p></td><td><p>42.3</p></td><td><p>0</p></td><td><p>0.1</p></td><td><p>25</p></td><td><p>0.4</p></td><td><p>0.5</p></td><td><p>85.7</p></td><td><p>0.3</p></td><td><p>0.6</p></td><td><p>0.9</p></td><td><p>0.8</p></td><td><p>0.4</p></td><td><p>0.1</p></td><td><p>0</p></td><td><p>0.6</p></td><td><p><em>1.2</em></p></td></tr></tbody></table>'
    tables =  parse_tables_from_html(html)
    for table in tables:
        print  " ".join(table['columns'])



    

if __name__ == "__main__":
    # test()
    extract_table_columns()
