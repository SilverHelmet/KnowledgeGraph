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
                print 'error at parse %s' %bk_url
    outf.close()



def test():
    html = "<table><thead><tr><th width=\"76\">上映时间</th><th width=\"155\">剧名</th><th width=\"98\">扮演角色</th><th width=\"113\">导演</th><th width=\"168\">合作演员</th></tr></thead><tbody><tr><td colspan=\"1\" rowspan=\"1\" width=\"74\">2015<br></td><td colspan=\"1\" rowspan=\"1\" width=\"155\"><a target=\"_blank\" href=\"/doc/8395551.html\">十二金鸭</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"98\">张近莱<br></td><td colspan=\"1\" rowspan=\"1\" width=\"110\"><a target=\"_blank\" href=\"/doc/371288.html\">邹凯光</a></td><td colspan=\"1\" rowspan=\"1\" width=\"161\"><a target=\"_blank\" href=\"/doc/2601175.html\">黄秋生</a>, <a target=\"_blank\" href=\"/doc/3396551.html\">谢霆锋</a>, <a target=\"_blank\" href=\"/doc/3351364.html\">赵薇</a><br></td></tr><tr><td colspan=\"1\" rowspan=\"1\" width=\"74\">2015<br></td><td colspan=\"1\" rowspan=\"1\" width=\"155\"><a target=\"_blank\" href=\"/doc/2578968.html\">捉妖记</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"98\">胖荧<br></td><td colspan=\"1\" rowspan=\"1\" width=\"110\"><a target=\"_blank\" href=\"/doc/5428348.html\">许诚毅</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"161\"><a target=\"_blank\" href=\"/doc/5351354.html\">白百合</a>, <a target=\"_blank\" href=\"/doc/4921261.html\">井柏然</a>, <a target=\"_blank\" href=\"/doc/317602.html\">曾志伟</a><br></td></tr><tr><td colspan=\"1\" rowspan=\"1\" width=\"74\">2015<br></td><td colspan=\"1\" rowspan=\"1\" width=\"155\">煎饼侠<br></td><td colspan=\"1\" rowspan=\"1\" width=\"98\"><a target=\"_blank\" href=\"/doc/4816562.html\">吴君如</a></td><td colspan=\"1\" rowspan=\"1\" width=\"110\">董成鹏<br></td><td colspan=\"1\" rowspan=\"1\" width=\"161\"><a target=\"_blank\" href=\"/doc/3758580.html\">袁姗姗</a>, <a target=\"_blank\" href=\"/doc/317602.html\">曾志伟</a>, <a target=\"_blank\" href=\"/doc/277355-293614.html\">柳岩</a></td></tr><tr><td colspan=\"1\" rowspan=\"1\" width=\"74\">2015<br></td><td colspan=\"1\" rowspan=\"1\" width=\"155\"><a target=\"_blank\" href=\"/doc/7302005.html\">失孤</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"98\">人贩子<br></td><td colspan=\"1\" rowspan=\"1\" width=\"110\"><a target=\"_blank\" href=\"/doc/6136772.html\">彭三源</a></td><td colspan=\"1\" rowspan=\"1\" width=\"161\"><a target=\"_blank\" href=\"/doc/1287918.html\">刘德华</a>, <a target=\"_blank\" href=\"/doc/4921261.html\">井柏然</a>, <a target=\"_blank\" href=\"/doc/3560909.html\">梁家辉</a><br></td></tr><tr><td colspan=\"1\" rowspan=\"1\" width=\"74\">2014<br></td><td colspan=\"1\" rowspan=\"1\" width=\"155\"><a target=\"_blank\" href=\"/doc/7348434.html\">六福喜事</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"98\">宫三<br></td><td colspan=\"1\" rowspan=\"1\" width=\"110\"><a target=\"_blank\" href=\"/doc/4681252.html\">谷德昭</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"161\"><a target=\"_blank\" href=\"/doc/3138669.html\">黄百鸣</a>, <a target=\"_blank\" href=\"/doc/317602.html\">曾志伟</a>, <a target=\"_blank\" href=\"/doc/5024739.html\">薛凯琪</a><br></td></tr><tr><td colspan=\"1\" rowspan=\"1\" width=\"74\">2013<br></td><td colspan=\"1\" rowspan=\"1\" width=\"155\"><a target=\"_blank\" href=\"/doc/2004836.html\">花漾</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"98\">花月娘<br></td><td colspan=\"1\" rowspan=\"1\" width=\"110\"><a target=\"_blank\" href=\"/doc/6541929.html\">周美玲</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"161\"><a target=\"_blank\" href=\"/doc/1515676.html\">任达华</a>, <a target=\"_blank\" href=\"/doc/5009131.html\">陈妍希</a>, <a target=\"_blank\" href=\"/doc/4939238.html\">陈意涵</a></td></tr><tr><td colspan=\"1\" rowspan=\"1\" width=\"74\">2013<br></td><td colspan=\"1\" rowspan=\"1\" width=\"155\"><a target=\"_blank\" href=\"/doc/5366239.html\">百星酒店</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"98\"><a target=\"_blank\" href=\"/doc/81954.html\">桃姐</a><br></td><td colspan=\"1\" rowspan=\"1\" width=\"110\"><a target=\"_blank\" href=\"/doc/4681252.html\">谷德昭</a></td><td colspan=\"1\" rowspan=\"1\" width=\"161\"><a target=\"_blank\" href=\"/doc/4844847.html\">郑中基</a>, <a target=\"_blank\" href=\"/doc/660266.html\">杜汶泽</a>, <a target=\"_blank\" href=\"/doc/3138669.html\">黄百鸣</a><br></td></tr><tr><td width=\"74\"><p>2013</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5333807.html\">越来越好之村晚</a></p></td><td width=\"98\"><p>元芳</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/590846.html\">张一白</a>, 谢东燊</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5352786.html\">郭富城</a>, <a target=\"_blank\" href=\"/doc/2881740.html\">王宝强</a>, <a target=\"_blank\" href=\"/doc/184208.html\">王珞丹</a></p></td></tr><tr><td width=\"74\"><p>2013</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5335719.html\">笑功震武林</a></p></td><td width=\"98\"><p>麦当娜</p></td><td width=\"114\"><p>王晶, 姜国民</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/4884606.html\">洪金宝</a>, <a target=\"_blank\" href=\"/doc/317602.html\">曾志伟</a>, <a target=\"_blank\" href=\"/doc/4844847.html\">郑中基</a></p></td></tr><tr><td width=\"74\"><p>2012</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/1554800.html\">八星抱喜</a></p></td><td width=\"98\"><p>宋秋波</p></td><td width=\"114\"><p>陈庆嘉, 秦小珍</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/343238.html\">甄子丹</a>, <a target=\"_blank\" href=\"/doc/3138669.html\">黄百鸣</a>, <a target=\"_blank\" href=\"/doc/592390.html\">古天乐</a></p></td></tr><tr><td width=\"74\"><p>2010</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/2943396.html\">美丽密令</a></p></td><td width=\"98\"><p>铁美丽</p></td><td width=\"114\"><p>王晶</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/465818.html\">蔡卓妍</a>, <a target=\"_blank\" href=\"/doc/1423027.html\">陆毅</a>, <a target=\"_blank\" href=\"/doc/3734178.html\">谢娜</a></p></td></tr><tr><td width=\"74\"><p>2010</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/2182858-2309702.html\">岁月神偷</a></p></td><td width=\"98\"><p>罗太太</p></td><td width=\"114\"><p>罗启锐</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1515676.html\">任达华</a>, <a target=\"_blank\" href=\"/doc/2566338.html\">李治廷</a>, <a target=\"_blank\" href=\"/doc/5428654.html\">钟绍图</a></p></td></tr><tr><td width=\"74\"><p>2009</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5742926.html\">家有喜事2009</a></p></td><td width=\"98\"><p>余珠</p></td><td width=\"114\"><p>谷德超</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/592390.html\">古天乐</a>, <a target=\"_blank\" href=\"/doc/3138669.html\">黄百鸣</a>, <a target=\"_blank\" href=\"/doc/465818.html\">蔡卓妍</a></p></td></tr><tr><td width=\"74\"><p>2009</p></td><td width=\"152\"><p>大内密探灵灵狗</p></td><td width=\"98\"><p>西宫娘娘</p></td><td width=\"114\"><p>王晶</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/592390.html\">古天乐</a>, <a target=\"_blank\" href=\"/doc/1507437.html\">樊少皇</a>, <a target=\"_blank\" href=\"/doc/261355.html\">徐熙媛</a></p></td></tr><tr><td width=\"74\"><p>2006</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/4130929.html\">春田花花同学会</a></p></td><td width=\"98\"><p>赵良骏</p></td><td width=\"114\"><a target=\"_blank\" href=\"/doc/2990796.html\">赵良骏</a><br></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/2533422.html\">周笔畅</a>, <a target=\"_blank\" href=\"/doc/2601175.html\">黄秋生</a>, <a target=\"_blank\" href=\"/doc/4815368.html\">吴镇宇</a></p></td></tr><tr><td width=\"74\"><p>2003</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/6344787.html\">金鸡2</a></p></td><td width=\"98\"><p>金如</p></td><td width=\"114\"><p>赵良骏</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1287918.html\">刘德华</a>, <a target=\"_blank\" href=\"/doc/3537559.html\">张学友</a>, <a target=\"_blank\" href=\"/doc/4623833.html\">田蕊妮</a></p></td></tr><tr><td width=\"74\"><p>2002</p></td><td width=\"155\"><p>古惑仔情义篇之洪兴十三妹</p></td><td width=\"98\"><p>崔小小</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5370153-5606024.html\">叶伟民</a></p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1524726.html\">方中信</a>, <a target=\"_blank\" href=\"/doc/1035001.html\">舒淇</a>, <a target=\"_blank\" href=\"/doc/4188610.html\">杨恭如</a></p></td></tr><tr><td width=\"74\"><p>2002</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/4615089-7429939.html\">金鸡</a></p></td><td width=\"98\"><p>金如</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/2990796.html\">赵良骏</a></p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/317602.html\">曾志伟</a>, <a target=\"_blank\" href=\"/doc/2409815.html\">陈奕迅</a>, <a target=\"_blank\" href=\"/doc/1287918.html\">刘德华</a></p></td></tr><tr><td width=\"74\"><p>2001</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5329010-5564182.html\">爱君如梦</a></p></td><td width=\"98\"><p>阿金</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5329583-5564757.html\">刘伟强</a></p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1287918.html\">刘德华</a>, <a target=\"_blank\" href=\"/doc/4163115.html\">梅艳芳</a>, <a target=\"_blank\" href=\"/doc/3985592.html\">陈冠希</a></p></td></tr><tr><td width=\"74\"><p>2000</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/659379.html\">江湖告急</a></p></td><td width=\"98\"><p>苏花</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1630008.html\">林超贤</a></p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/3560909.html\">梁家辉</a>, <a target=\"_blank\" href=\"/doc/2601175.html\">黄秋生</a>, <a target=\"_blank\" href=\"/doc/2409815.html\">陈奕迅</a></p></td></tr><tr><td width=\"74\"><p>2000</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5572039.html\">朱丽叶与梁山伯</a></p></td><td width=\"98\"><p>朱迪</p></td><td width=\"114\"><p>叶伟信</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/4815368.html\">吴镇宇</a>, <a target=\"_blank\" href=\"/doc/1515676.html\">任达华</a>, <a target=\"_blank\" href=\"/doc/5571706.html\">戴碧芝</a></p></td></tr><tr><td width=\"74\"><p>1999</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5120705.html\">半支烟</a></p></td><td width=\"98\"><p>客串</p></td><td width=\"114\"><p>叶锦鸿</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/3396551.html\">谢霆锋</a>, <a target=\"_blank\" href=\"/doc/317602.html\">曾志伟</a>, <a target=\"_blank\" href=\"/doc/1035001.html\">舒淇</a></p></td></tr><tr><td width=\"74\"><p>1998</p></td><td width=\"155\"><p>越快乐越堕落</p></td><td width=\"98\"><p>Video Dealer</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/6216598.html\">魏绍恩</a>, 杨智深</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/3766268.html\">邱淑贞</a>, <a target=\"_blank\" href=\"/doc/317602.html\">曾志伟</a>, <a target=\"_blank\" href=\"/doc/1509644.html\">陈锦鸿</a></p></td></tr><tr><td width=\"74\"><p>1997</p></td><td width=\"155\"><p>97古惑仔战无不胜</p></td><td width=\"98\"><p>崔小小</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5329583-5564757.html\">刘伟强</a></p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1105506.html\">郑伊健</a>, <a target=\"_blank\" href=\"/doc/5329590.html\">陈小春</a>, <a target=\"_blank\" href=\"/doc/1243615.html\">李嘉欣</a></p></td></tr><tr><td width=\"74\"><p>1996</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/1951564.html\">四面夏娃</a></p></td><td width=\"98\"><p>客串</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5393577.html\">甘国亮</a>, <a target=\"_blank\" href=\"/doc/1530336.html\">葛民辉</a></p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5426349.html\">夏萍</a>, <a target=\"_blank\" href=\"/doc/5349799.html\">陈百祥</a>, <a target=\"_blank\" href=\"/doc/2666034.html\">莫文蔚</a></p></td></tr><tr><td width=\"74\"><p>1996</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/6261193.html\">麻雀飞龙</a></p></td><td width=\"98\"><p>秀钿</p></td><td width=\"114\"><p>元奎</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/3378582.html\">赵文卓</a>, <a target=\"_blank\" href=\"/doc/3520542.html\">萧芳芳</a>, <a target=\"_blank\" href=\"/doc/4931433.html\">柯受良</a></p></td></tr><tr><td width=\"74\"><p>1994</p></td><td width=\"155\"><p>等着你回来</p></td><td width=\"98\"><p>Julia</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5426758-5664980.html\">张之亮</a></p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5705.html\">梁朝伟</a>, <a target=\"_blank\" href=\"/doc/2940221.html\">吴倩莲</a>, <a target=\"_blank\" href=\"/doc/8612001.html\">毛俊辉</a></p></td></tr><tr><td width=\"74\"><p>1994</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5408816.html\">火云传奇</a></p></td><td width=\"98\"><p>Tang Lyn-Yu</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5415852-5653997.html\">袁和平</a></p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/2088176.html\">林青霞</a>, <a target=\"_blank\" href=\"/doc/939668.html\">莫少聪</a>, <a target=\"_blank\" href=\"/doc/3317358.html\">单立文</a></p></td></tr><tr><td width=\"74\"><p>1993</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/4234048.html\">花田喜事</a></p></td><td width=\"98\"><p>周吉</p></td><td width=\"114\"><p>高志森</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1467986.html\">张国荣</a>, <a target=\"_blank\" href=\"/doc/3138669.html\">黄百鸣</a>, <a target=\"_blank\" href=\"/doc/43857.html\">许冠杰</a></p></td></tr><tr><td width=\"74\"><p>1992</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/6772077.html\">霸王花4</a></p></td><td width=\"98\"><p>Amy</p></td><td width=\"114\"><p>钱升玮</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1789067.html\">杨丽菁</a>, <a target=\"_blank\" href=\"/doc/1607562.html\">惠英红</a>, <a target=\"_blank\" href=\"/doc/817573.html\">陈淑兰</a></p></td></tr><tr><td width=\"74\"><p>1992</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/944825.html\">家有喜事</a></p></td><td width=\"98\"><p>程大嫂</p></td><td width=\"114\"><p>高志森</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1467986.html\">张国荣</a>, <a target=\"_blank\" href=\"/doc/88963.html\">周星驰</a>, <a target=\"_blank\" href=\"/doc/3138669.html\">黄百鸣</a></p></td></tr><tr><td width=\"74\"><p>1992</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5388727.html\">笑八仙</a></p></td><td width=\"98\"><p>何仙姑</p></td><td width=\"114\"><a target=\"_blank\" href=\"/doc/3341222.html\">陶白莉</a>, <a target=\"_blank\" href=\"/doc/7535715.html\">邹集城</a><br></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/920393.html\">郑少秋</a>, <a target=\"_blank\" href=\"/doc/5350449.html\">吴孟达</a>, <a target=\"_blank\" href=\"/doc/1276123.html\">关之琳</a></p></td></tr><tr><td width=\"74\"><p>1991</p></td><td width=\"155\"><p>赌圣延续篇之<a target=\"_blank\" href=\"/doc/6764916-6979833.html\">赌霸</a></p></td><td width=\"98\"><p>客串</p></td><td width=\"114\"><p>刘镇伟</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/5350449.html\">吴孟达</a>, <a target=\"_blank\" href=\"/doc/1506204.html\">郑裕玲</a>, <a target=\"_blank\" href=\"/doc/88963.html\">周星驰</a></p></td></tr><tr><td width=\"74\"><p>1991</p></td><td width=\"155\"><p>上海滩赌圣</p></td><td width=\"98\"><p>春天</p></td><td width=\"114\"><p>王晶</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/88963.html\">周星驰</a>, <a target=\"_blank\" href=\"/doc/3911682.html\">巩俐</a>, <a target=\"_blank\" href=\"/doc/5350449.html\">吴孟达</a></p></td></tr><tr><td width=\"74\"><p>1991</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5350546-5680008.html\">鹿鼎记</a></p></td><td width=\"98\"><p>韦春花</p></td><td width=\"114\"><p>王晶</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/88963.html\">周星驰</a>, <a target=\"_blank\" href=\"/doc/1192551.html\">张敏</a>, <a target=\"_blank\" href=\"/doc/5350449.html\">吴孟达</a></p></td></tr><tr><td width=\"74\"><p>1990</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/4622674-4835166.html\">无敌幸运星</a></p></td><td width=\"98\"><p>巢飞飞, 阿凤</p></td><td width=\"114\"><p>陈友</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/88963.html\">周星驰</a>, <a target=\"_blank\" href=\"/doc/5425334.html\">陈友</a>, <a target=\"_blank\" href=\"/doc/2601175.html\">黄秋生</a></p></td></tr><tr><td width=\"74\"><p>1990</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/6765753.html\">霸王花3</a></p></td><td width=\"98\"><p>Amy</p></td><td width=\"114\"><p>钱升玮</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1507173.html\">胡慧中</a>, 叶子楣, <a target=\"_blank\" href=\"/doc/1607562.html\">惠英红</a></p></td></tr><tr><td width=\"74\"><p>1990</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/944239-998145.html\">赌圣</a></p></td><td width=\"98\"><p>阿萍</p></td><td width=\"114\"><p>刘镇伟, 元奎</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/88963.html\">周星驰</a>, <a target=\"_blank\" href=\"/doc/1192551.html\">张敏</a>, <a target=\"_blank\" href=\"/doc/5350449.html\">吴孟达</a></p></td></tr><tr><td width=\"74\"><p>1990</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/943761.html\">望夫成龙</a></p></td><td width=\"98\"><p>啊娣</p></td><td width=\"114\"><p>梁家树</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/6146522.html\">关佩琳</a>, <a target=\"_blank\" href=\"/doc/88963.html\">周星驰</a>, <a target=\"_blank\" href=\"/doc/234590.html\">关秀媚</a></p></td></tr><tr><td width=\"74\"><p>1989</p></td><td width=\"155\"><p>流氓差婆</p></td><td width=\"98\"><p>啊楠</p></td><td width=\"114\"><p>刘镇伟</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/88963.html\">周星驰</a>, <a target=\"_blank\" href=\"/doc/3317346.html\">柏安妮</a>, <a target=\"_blank\" href=\"/doc/2680533.html\">成奎安</a></p></td></tr><tr><td width=\"74\"><p>1989</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5381979-6981881.html\">霸王花</a>2</p></td><td width=\"98\"><p>Amy</p></td><td width=\"114\"><p>钱升玮</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1507173.html\">胡慧中</a>, <a target=\"_blank\" href=\"/doc/1607562.html\">惠英红</a>, <a target=\"_blank\" href=\"/doc/2272498.html\">罗美薇</a></p></td></tr><tr><td width=\"74\"><p>1988</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5332757.html\">最佳损友闯情关</a></p></td><td width=\"98\"><p>万人迷</p></td><td width=\"114\"><p>王晶</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1287918.html\">刘德华</a>, <a target=\"_blank\" href=\"/doc/1276123.html\">关之琳</a>, <a target=\"_blank\" href=\"/doc/5349799.html\">陈百祥</a></p></td></tr><tr><td width=\"74\"><p>1988</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/5381979-6981881.html\">霸王花</a></p></td><td width=\"98\"><p>Amy</p></td><td width=\"114\"><p>钱升玮</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1607562.html\">惠英红</a>, <a target=\"_blank\" href=\"/doc/1507173.html\">胡慧中</a>, <a target=\"_blank\" href=\"/doc/4754827.html\">陈雅伦</a></p></td></tr><tr><td width=\"74\"><p>1988</p></td><td width=\"155\"><p><a target=\"_blank\" href=\"/doc/927954-980852.html\">最佳损友</a></p></td><td width=\"98\"><p>万人迷</p></td><td width=\"114\"><p>王晶</p></td><td width=\"114\"><p><a target=\"_blank\" href=\"/doc/1287918.html\">刘德华</a>, <a target=\"_blank\" href=\"/doc/267228.html\">陈玉莲</a>, <a target=\"_blank\" href=\"/doc/3766268.html\">邱淑贞</a></p></td></tr></tbody></table>"

    h2 = '<table width=\"100%\"><thead><tr><th>时间</th><th>类型</th><th>作品名称</th><th>导演</th><th>身份</th></tr></thead><tbody><tr><td>1994年</td><td rowspan=\"8\">电影</td><td>《<a target=\"_blank\" href=\"/doc/3877960-4070979.html\">天与地</a>》</td><td>黎大炜</td><td rowspan=\"8\">制作人</td></tr><tr><td>1997年<br></td><td>《<a target=\"_blank\" href=\"/doc/5675988-5888659.html\">香港制造</a>》</td><td>陈果</td></tr><tr><td>1998年</td><td>《<a target=\"_blank\" href=\"/doc/6304949-6518476.html\">去年烟花特别多</a>》</td><td>陈果</td></tr><tr><td>2000年</td><td>《<a target=\"_blank\" href=\"/doc/1054271-1115215.html\">阿虎</a>》</td><td>李仁港</td></tr><tr><td>2001年</td><td>《<a target=\"_blank\" href=\"/doc/4720590-4935251.html\">全职杀手</a>》</td><td>杜琪峰</td></tr><tr><td>2005年</td><td>《<a target=\"_blank\" href=\"/doc/1054739-1115730.html\">再说一次我爱你</a>》</td><td>余伟国</td></tr><tr><td>2011年</td><td>《<a target=\"_blank\" href=\"/doc/3917049-4111093.html\">我知女人心</a>》</td><td>陈大明</td></tr><tr><td>2013年</td><td>《<a target=\"_blank\" href=\"/doc/5417476-6991186.html\">风暴</a>》</td><td>袁锦麟</td></tr></tbody></table>"'

    h3 = '<table width=\"100%\"><thead><tr><th><p>时间</p></th><th><p>类型</p></th><th><p>名称</p></th><th><p>导演</p></th><th><p>主演</p></th></tr></thead><tbody><tr><td><p>1991</p></td><td rowspan=\"10\"><p>电影</p></td><td><p>《91神雕侠侣》</p></td><td><p>元奎、<a target=\"_blank\" href=\"/doc/5429087-5667311.html\">黎大炜</a></p></td><td><p>刘德华、<a target=\"_blank\" href=\"/doc/4163115-4363268.html\">梅艳芳</a>、<a target=\"_blank\" href=\"/doc/5352786-5588244.html\">郭富城</a></p></td></tr><tr><td rowspan=\"2\"><p>1992</p></td><td><p>《92神雕侠侣》</p></td><td><p>元奎、黎大炜</p></td><td><p>刘德华、关之琳</p></td></tr><tr><td><p>《<a target=\"_blank\" href=\"/doc/6348903-13773955.html\">战神传说</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/4884606-5102614.html\">洪金宝</a></p></td><td><p>刘德华、<a target=\"_blank\" href=\"/doc/4846597-5063695.html\">钟镇涛</a>、张曼玉、梅艳芳</p></td></tr><tr><td><p>1993</p></td><td><p>《<a target=\"_blank\" href=\"/doc/184752-196187.html\">天长地久</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/2233319-2363123.html\">刘镇伟</a></p></td><td><p>刘德华、刘锦玲、吴家丽、徐濠莹、叶德娴</p></td></tr><tr><td><p>1994</p></td><td><p>《<a target=\"_blank\" href=\"/doc/3877960-4070979.html\">天与地</a>》</p></td><td><p>黎大炜</p></td><td><p>刘德华、刘松仁、<a target=\"_blank\" href=\"/doc/4163001-4363118.html\">陈少霞</a></p></td></tr><tr><td><p>1997</p></td><td><p>《<a target=\"_blank\" href=\"/doc/5675988-5888659.html\">香港制造</a>》</p></td><td rowspan=\"2\"><p><a target=\"_blank\" href=\"/doc/1536565-1625171.html\">陈果</a><em>（兼编剧）</em></p></td><td><p><a target=\"_blank\" href=\"/doc/1023781-1082776.html\">严栩慈</a>、<a target=\"_blank\" href=\"/doc/7895347-8169442.html\">李栋全</a>、<a target=\"_blank\" href=\"/doc/9914064-10261344.html\">谭嘉荃</a>、林杰芳、<a target=\"_blank\" href=\"/doc/655789-694169.html\">周燕华</a>、<a target=\"_blank\" href=\"/doc/434172-459717.html\">胡慧冲</a></p></td></tr><tr><td><p>1998</p></td><td><p>《去年的烟花特别多》</p></td><td><p><a target=\"_blank\" href=\"/doc/5333413-5568848.html\">何华超</a>、<a target=\"_blank\" href=\"/doc/2499713-2641570.html\">李灿森</a>、<a target=\"_blank\" href=\"/doc/492628-521639.html\">谷祖琳</a>、黎志豪、<a target=\"_blank\" href=\"/doc/5676110-5888781.html\">陈生</a>、梁耀华</p></td></tr><tr><td><p>2000</p></td><td><p>《<a target=\"_blank\" href=\"/doc/1054271-1115215.html\">阿虎</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/859194-908381.html\">李仁港</a></p></td><td><p>刘德华、常盘贵子</p></td></tr><tr><td rowspan=\"3\"><p>2001</p></td><td><p>《<a target=\"_blank\" href=\"/doc/4720590-4935251.html\">全职杀手</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/1802440-1906060.html\">杜琪峰</a>、<a target=\"_blank\" href=\"/doc/5365637-5601324.html\">韦家辉</a></p></td><td><p>刘德华、<a target=\"_blank\" href=\"/doc/1515676-1602447.html\">任达华</a>、<a target=\"_blank\" href=\"/doc/5181843-5412932.html\">林熙蕾</a>、<a target=\"_blank\" href=\"/doc/3057413-3222881.html\">应采儿</a>、<a target=\"_blank\" href=\"/doc/5365872-5601564.html\">林雪</a>、<a target=\"_blank\" href=\"/doc/5425273-10506929.html\">连晋</a></p></td></tr><tr><td><p>《<a target=\"_blank\" href=\"/doc/5329010-5564182.html\">爱君如梦</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/5329583-5564757.html\">刘伟强</a></p></td><td><p>刘德华、梅艳芳、<a target=\"_blank\" href=\"/doc/4816562-5033111.html\">吴君如</a>、<a target=\"_blank\" href=\"/doc/4232337-4434187.html\">谭小环</a></p></td></tr><tr><td><p>电视</p></td><td><p>《<a target=\"_blank\" href=\"/doc/5400068-5637643.html\">方谬神探</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/6932100-7154423.html\">束一德</a></p></td><td><p>张卫健、袁咏仪、<a target=\"_blank\" href=\"/doc/2454282-2594356.html\">郑国霖</a>、<a target=\"_blank\" href=\"/doc/5392546-5629375.html\">胡静</a>、<a target=\"_blank\" href=\"/doc/5351437-5586895.html\">张茜</a>、<a target=\"_blank\" href=\"/doc/5401842-5639506.html\">潘洁</a>、<a target=\"_blank\" href=\"/doc/5857244-6070087.html\">杨升</a></p></td></tr><tr><td><p>2003</p></td><td rowspan=\"11\"><p>电影</p></td><td><p>《<a target=\"_blank\" href=\"/doc/5400341-5637929.html\">继续跳舞</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/5425280-5663500.html\">邱礼涛</a></p></td><td><p><a target=\"_blank\" href=\"/doc/2601175-2746608.html\">黄秋生</a>、<a target=\"_blank\" href=\"/doc/1505310-1591650.html\">许志安</a></p></td></tr><tr><td><p>2005</p></td><td><p>《<a target=\"_blank\" href=\"/doc/273751-289732.html\">人鱼朵朵</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/5427266-5665489.html\">李芸婵</a></p></td><td><p><a target=\"_blank\" href=\"/doc/59663-62768.html\">徐若瑄</a>、Duncan</p></td></tr><tr><td rowspan=\"5\"><p>2006</p></td><td><p>《<a target=\"_blank\" href=\"/doc/5397006-5634284.html\">疯狂的石头</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/4306959-4510858.html\">宁浩</a></p></td><td><p><a target=\"_blank\" href=\"/doc/5365626-5601311.html\">郭涛</a>、<a target=\"_blank\" href=\"/doc/4300540-4504310.html\">黄渤</a>、<a target=\"_blank\" href=\"/doc/1117785-1182683.html\">徐峥</a></p></td></tr><tr><td><p>《<a target=\"_blank\" href=\"/doc/5364550-6991410.html\">爱情故事</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/5044647-5271511.html\">唐永健</a></p></td><td><p>林依伦、<a target=\"_blank\" href=\"/doc/229391-242658.html\">陈毓芸</a>、李之晴</p></td></tr><tr><td><p>《<a target=\"_blank\" href=\"/doc/10036462-10518544.html\">太阳雨</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/5425839-5664060.html\">何宇恒</a></p></td><td><p>廖伟雄、<a target=\"_blank\" href=\"/doc/4168416-4368713.html\">张颖康</a></p></td></tr><tr><td><p>《师奶唔易做》</p></td><td><p><a target=\"_blank\" href=\"/doc/5494833-5732745.html\">李公乐</a></p></td><td><p>田蕊妮、<a target=\"_blank\" href=\"/doc/5330435-5565609.html\">雪梨</a></p></td></tr><tr><td><p>《<a target=\"_blank\" href=\"/doc/5383112-5619498.html\">得闲饮茶</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/4656071-4869382.html\">林子聪</a></p></td><td><p><a target=\"_blank\" href=\"/doc/852847-901781.html\">方力申</a>、<a target=\"_blank\" href=\"/doc/1570609-1660159.html\">林家栋</a>、<a target=\"_blank\" href=\"/doc/875007-924982.html\">梁慧嘉</a></p></td></tr><tr><td><p>2007</p></td><td><p>《<a target=\"_blank\" href=\"/doc/358104-379388.html\">兄弟之生死同盟</a>》</p></td><td><a target=\"_blank\" href=\"/doc/5425247-5663467.html\">赵崇基</a></td><td><p>刘德华、<a target=\"_blank\" href=\"/doc/1542551-1630744.html\">苗侨伟</a>、<a target=\"_blank\" href=\"/doc/2409815-2547784.html\">陈奕迅</a>、<a target=\"_blank\" href=\"/doc/1201660-1271085.html\">黄奕</a>、黄日华、汤镇业</p></td></tr><tr><td><p>2010</p></td><td><p>《<a target=\"_blank\" href=\"/doc/186809-197323.html\">打擂台</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/6305639-6519167.html\">郭子健</a>、<a target=\"_blank\" href=\"/doc/460073-487158.html\">郑思杰</a></p></td><td><p>梁小龙、<a target=\"_blank\" href=\"/doc/5207354-5439308.html\">陈观泰</a>、<a target=\"_blank\" href=\"/doc/10523780-11049131.html\">泰迪罗宾</a></p></td></tr><tr><td><p>2011</p></td><td><p>《<a target=\"_blank\" href=\"/doc/81954-86509.html\">桃姐</a>》</p></td><td><p><a target=\"_blank\" href=\"/doc/1802793-1906407.html\">许鞍华</a></p></td><td><p>刘德华、<a target=\"_blank\" href=\"/doc/4830643-5047492.html\">叶德娴</a>、秦海璐</p></td></tr><tr><td>2013</td><td>《<a target=\"_blank\" href=\"/doc/6751032-6965591.html\">初恋未满</a>》</td><td>刘娟</td><td>冉旭、<a target=\"_blank\" href=\"/doc/5329579-5564753.html\">张含韵</a></td></tr></tbody></table>'
    tables =  parse_tables_from_html(html)
    for table in tables:
        print  " ".join(table['columns'])



    

if __name__ == "__main__":
    extract_table_columns()
