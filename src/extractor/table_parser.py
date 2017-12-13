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
    html = '<table width=\"NaN\"><thead><tr><th>号码</th><th>球员名字</th><th>出生日期</th><th>身高</th><th>体重</th><th>籍贯/国籍</th><th>加盟赛季</th><th>前属球队</th></tr></thead><tbody><tr><th colspan=\"8\">门 将</th></tr><tr><td align=\"center\">1</td><td align=\"center\"><a target=\"_blank\" href=\"/doc/7213382-7438082.html\">邓子豪</a></td><td align=\"center\">1993年11月2日</td><td align=\"center\">189CM</td><td align=\"center\">84KG</td><td align=\"center\">湖南</td><td align=\"center\">2011</td><td align=\"center\">湖南体育学院足球队</td></tr><tr><td>12</td><td><a target=\"_blank\" href=\"/doc/4688698-4902644.html\">董建宏</a></td><td>1991年9月10日</td><td>187CM</td><td>82KG</td><td>辽宁</td><td>2012</td><td>青海森科</td></tr><tr><td>17</td><td>王鹏</td><td>1989年9月19日</td><td>193CM</td><td>104KG</td><td>北京</td><td>2015</td><td>暂空缺</td></tr><tr><th colspan=\"8\">后 卫</th></tr><tr><td>3</td><td>王永鑫</td><td>1990年1月16日</td><td>186CM</td><td>83KG</td><td>河南</td><td>2014</td><td>成都谢菲联</td></tr><tr><td>4</td><td><a target=\"_blank\" href=\"/doc/4558165-4768913.html\">曹驩</a></td><td>1983年11月25日</td><td>177CM</td><td>83KG</td><td>上海</td><td>2011</td><td>陕西宝荣</td></tr><tr><td>5</td><td><a target=\"_blank\" href=\"/doc/4053001-4251212.html\">贝特斯</a></td><td>1981年11月29日</td><td>190CM</td><td>87KG</td><td>塞尔维亚</td><td>2014</td><td>OFK贝尔格莱德</td></tr><tr><td>15</td><td>王钰洋</td><td>1991年8月30日</td><td>190CM</td><td>84KG</td><td>江苏</td><td>2011</td><td>江苏舜天</td></tr><tr><td>19</td><td>孙国梁</td><td>1991年2月6日</td><td>183CM</td><td>79KG</td><td>山东</td><td>2012</td><td>广州富力</td></tr><tr><td>22</td><td><a target=\"_blank\" href=\"/doc/1414165-1494986.html\">刘玉圣</a></td><td>1990年9月30日</td><td>185CM</td><td>76KG</td><td>辽宁</td><td>2010</td><td>大连实德</td></tr><tr><td>23</td><td>赵旭东</td><td>1985年12月10日</td><td>183CM</td><td>80KG</td><td>辽宁</td><td>2014</td><td>重庆FC</td></tr><tr><td>28</td><td>秦鹏</td><td>1994年8月18日</td><td>186CM</td><td>80KG</td><td>辽宁</td><td>2013</td><td>湖南湘涛梯队</td></tr><tr><th colspan=\"8\">中 场</th></tr><tr><td>6</td><td>孔涛</td><td>1988年3月8日</td><td>179CM</td><td>71KG</td><td>山东</td><td>2008</td><td>暂空缺</td></tr><tr><td>7</td><td><a target=\"_blank\" href=\"/doc/2766495-2920045.html\">陈子介</a></td><td>1989年12月24日</td><td>184CM</td><td>80KG</td><td>陕西</td><td>2015</td><td>贵州人和</td></tr><tr><td>8</td><td>杨柯</td><td>1989年4月19日</td><td>184CM</td><td>76KG</td><td>湖南</td><td>2015</td><td>杭州绿城预备队</td></tr><tr><td>10</td><td><a target=\"_blank\" href=\"/doc/309682-327903.html\">布尔扎诺维奇</a></td><td>1985年8月25日</td><td>182CM</td><td>79KG</td><td>黑山</td><td>2015</td><td>艾迪殊</td></tr><tr><td>13</td><td>王琛</td><td>1984年4月20日</td><td>175CM</td><td>75KG</td><td>湖南</td><td>2005</td><td>湖南湘军二队</td></tr><tr><td>14</td><td>钟浩然</td><td>1994年7月15日</td><td>178CM</td><td>72KG</td><td>湖北</td><td>2013</td><td>湖南湘涛梯队</td></tr><tr><td>16</td><td><a target=\"_blank\" href=\"/doc/3640129-3826275.html\">谢维超</a></td><td>1989年7月6日</td><td>170CM</td><td>76KG</td><td>辽宁</td><td>2011</td><td>长沙金德</td></tr><tr><td>20</td><td><a target=\"_blank\" href=\"/doc/2835146-2991976.html\">刘鑫瑜</a></td><td>1991年11月17日</td><td>183CM</td><td>70KG</td><td>河北</td><td>2012</td><td>河北中基</td></tr><tr><td>21</td><td>曹国栋</td><td>1993年1月26日</td><td>187CM</td><td>75KG</td><td>湖北</td><td>2013</td><td>湖南湘涛梯队</td></tr><tr><td>26</td><td>陈昭安</td><td>1995年6月22日</td><td>177CM</td><td>68KG</td><td>中华台北</td><td>2015</td><td>国立台湾体育运动大学</td></tr><tr><td>27</td><td><a target=\"_blank\" href=\"/doc/7271526-7500889.html\">袁露</a></td><td>1990年1月10日</td><td>178CM</td><td>68KG</td><td>湖南</td><td>2013</td><td>湖南体育学院足球队</td></tr><tr><td>29</td><td>周琛威</td><td>1992年5月5日</td><td>179CM</td><td>74KG</td><td>湖南</td><td>2013</td><td>湖南湘涛梯队</td></tr><tr><td>31</td><td>刘帅</td><td>1990年7月30日</td><td>182CM</td><td>77KG</td><td>河北</td><td>2009</td><td>杭州绿城</td></tr><tr><td>33</td><td><a target=\"_blank\" href=\"/doc/308932-327132.html\">姚江山</a></td><td>1987年7月30日</td><td>177CM</td><td>68KG</td><td>山东</td><td>2015</td><td>青岛中能</td></tr><tr><th colspan=\"8\">前 锋</th></tr><tr><td>9</td><td>卡贝萨斯</td><td>1986年3月3日</td><td>184CM</td><td>83KG</td><td>哥伦比亚</td><td>2014</td><td>上海东亚</td></tr><tr><td>11</td><td>李想</td><td>1991年1月25日</td><td>187CM</td><td>86KG</td><td>北京</td><td>2015</td><td>北京理工</td></tr><tr><td>30</td><td>邱凌枫</td><td>1997年1月29日</td><td>192CM</td><td>83KG</td><td>湖南</td><td>2013</td><td>湖南湘涛梯队</td></tr></tbody></table>'
    tables =  parse_tables_from_html(html)
    for table in tables:
        print  " ".join(table['columns'])



    

if __name__ == "__main__":
    test()
    extract_table_columns()
