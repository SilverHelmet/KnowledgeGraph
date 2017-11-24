#encoding: utf-8
from src.IOUtil import *
from ltp import LTP
from src.schema.schema import Schema
import os
import json

class Resource:
    singleton = None
    def __init__(self):
        self.dict = {}

    def get_important_domains(self):
        if not 'important_domains' in self.dict:
            self.dict['important_domains'] = load_important_domains()
        return self.dict['important_domains']

    def get_ltp(self):
        if not 'ltp' in self.dict:
            self.dict['ltp'] = LTP(None)
        return self.dict['ltp']

    def get_schema(self):
        if not 'schema' in self.dict:
            schema = Schema()
            schema.init(init_type_neighbor = True)
            self.dict['schema'] = schema
        return self.dict['schema']

    def get_baike_info(self):
        if not 'baike_info' in self.dict:
            path = os.path.join(rel_ext_dir, 'baike_static_info.tsv')
            self.dict['baike_info'] = load_bk_static_info(path)
        return self.dict['baike_info']

    def load_baike_names(self, lowercase):
        path = os.path.join(rel_ext_dir, 'baike_names.tsv')
        extra_path = os.path.join(rel_ext_dir, 'extra_name/summary_extra_name.tsv')
        
        name2bk, url2names = load_baike_names_resource([path,extra_path])

        self.dict['name2bk'] = name2bk
        self.dict['url2names'] = url2names

        if lowercase:
            lower_name2bk = gen_lowercase_name(name2bk)
            self.dict['lower_name2bk'] = lower_name2bk

    def get_name2bk(self, lowercase = False):
        if not 'name2bk' in self.dict:
            self.load_baike_names(lowercase)
        return self.dict['name2bk']

    def get_url2names(self, lowercase = False):
        if not 'url2names' in self.dict:
            self.load_baike_names(lowercase)
        return self.dict['url2names']

    def get_lower_name2bk(self):
        if not 'lower_name2bk' in self.dict:
            self.load_baike_names(lowercase = True)
        return self.dict['lower_name2bk']

    def get_summary_with_infobox(self):
        if not 'baike_summary_with_infobox' in self.dict:
            summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary.json')
            infobox_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
            self.dict['baike_summary_with_infobox'] = load_summary_and_infobox(summary_path, infobox_path)
        return self.dict['baike_summary_with_infobox']

    def get_predicate_map(self):
        if not "predicate_map" in self.dict:
            filepath = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
            extra_path = os.path.join(doc_dir, 'human_add_predicate_map.json')
            self.dict['predicate_map'] = load_predicate_map(filepath, extra_path)
        return self.dict['predicate_map']

    def get_vertical_domain_baike_dict(self):
        if not "vt_domain_bk_dict" in self.dict:
            path = os.path.join(dict_dir, 'vertical_domain_baike_dict.txt')
            Print("load name dict from [%s]" %path)
            self.dict['vt_domain_bk_dict'] = load_file(path)
        return self.dict['vt_domain_bk_dict']

    def get_baike_ename_title(self):
        if not "baike_ename_title" in self.dict:
            self.dict['baike_ename_title'] = load_baike_ename_title()
        return self.dict['baike_ename_title']

    def get_location_dict(self):
        if not 'location_dict' in self.dict:
            dicts = ['province.txt', 'citytown.txt', 'nationality.txt']
            dicts_path = [os.path.join(dict_dir, x) for x in dicts]
            Print('load location dict from [%s]' %" ".join(dicts))
            self.dict['location_dict'] = load_dict(dicts_path)
        return self.dict['location_dict']

    @staticmethod
    def get_singleton():
        if Resource.singleton is None:
            Resource.singleton = Resource()
        return Resource.singleton

def load_name2baike(filepath = None):
    if filepath is None:
        filepath = os.path.join(rel_ext_dir, 'baike_names.tsv')
    total = nb_lines_of(filepath)
    name2bk = {}
    Print('load name -> baike from %s' %filepath)
    for line in tqdm(file(filepath), total = total):
        # p = line.strip().decode('utf-8').split('\t')
        p = line.strip().split('\t')
        bk_url = p[0]
        names = p[1:]
        for name in names:
            name = name.strip()
            if not name in name2bk:
                name2bk[name] = []
            name2bk[name].append(bk_url)
    return name2bk

def gen_lowercase_name(name2bk):
    lower_name2bk = {}
    for name in name2bk:
        if name.lower() != name:
            lower_name2bk[name.lower()] = name2bk[name]
    return lower_name2bk

def load_url2names(filepath = None):
    if filepath is None:
        filepath = os.path.join(rel_ext_dir, 'baike_names.tsv')
    total = nb_lines_of(filepath)

    Print('load url -> names from [%s]' %filepath)

    url2names = {}
    for line in tqdm(file(filepath), total = total):
        p = line.strip().split('\t')
        bk_url = p[0]
        names = p[1:]
        url2names[bk_url] = p[1:]
    return url2names

def load_baike_names_resource(filepaths):
    url2names = {}
    name2bk = {}
    for filepath in filepaths:
        Print('generate url2names & name2baike from baike name file [%s]' %filepath)
        total = nb_lines_of(filepath)
        for line in tqdm(file(filepath, 'r'), total = total):
            p = line.strip().split('\t')
            bk_url = p[0]
            names = p[1:]
            if bk_url in url2names:
                url2names[bk_url].extend(names)
            else:
                url2names[bk_url] = names
            for name in names:
                if not name in name2bk:
                    name2bk[name] = []
                name2bk[name].append(bk_url)
    
    return name2bk, url2names

def load_important_domains():
    domains = set()
    for line in file(os.path.join(doc_dir, 'important_domains.txt')):
        line = line.strip()
        if line.startswith("#"):
            continue
        domains.add(line)
    return domains


class BaikeInfo:
    def __init__(self, pop, types):
        self.pop = pop
        self.types = types

        
def load_bk_static_info(filepath):
    total = nb_lines_of(filepath)
    info_map = {}
    Print("load baike static info from [%s]" %filepath)
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        p = line.strip().split('\t')
        bk_url = p[0]
        pop = int(p[2])
        if p[1] != "None":
            pop = pop + 5
        types = json.loads(p[3])
        info = BaikeInfo(pop, types)
        info_map[bk_url] = info
    return info_map



def load_summary_and_infobox(summary_path, infobox_path):
    Print("load summary from [%s]" %summary_path)
    summary_map = {}
    for line in tqdm(file(summary_path, 'r'), total = nb_lines_of(summary_path)):
        p = line.split('\t')
        key = p[0]
        summary = json.loads(p[1])['summary']
        # summary = filter_bad_summary(summary)
        summary_map[key] = summary.encode('utf-8')
    Print('add infobox value to summary, path is [%s]' %infobox_path)
    for line in tqdm(file(infobox_path), total = nb_lines_of(infobox_path)):
        p = line.split('\t')
        key = p[0]
        info_values = list()
        info = json.loads(p[1])['info']
        for value_list in info.values():
            for value in value_list:
                info_values.append(value)
        if len(info_values) == 0:
            continue
        text = u"。" + u"#".join(info_values)
        text = text.encode('utf-8')
        if not key in summary_map:
            summary_map[key] = text
        else:
            summary_map[key] = summary_map[key] + text
    return summary_map    

def load_predicate_map(filepath = None, extra_path = None):
    if filepath is None:
        filepath = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
    Print('load predicate map from %s' %filepath)
    predicate_map  = {}
    for line in file(filepath):
        p = line.split('\t')
        infobox_pred = p[0]
        mappings = json.loads(p[1])[:7]
        probs = {}
        for prop, occur in mappings:
            cnt, total = map(int, occur.split('/'))
            prob = (cnt + 0.0) / (total + 3)
            probs[prop] = prob
        predicate_map[infobox_pred] = probs

    if extra_path is not None:
        Print("load extra rule from [%s]" %extra_path)
        for line in file(extra_path):
            line = line.strip()
            if line == "":
                continue
            if line.startswith("#"):
                continue
            p = line.split('\t')
            infobox_pred = p[0]
            if not infobox_pred in predicate_map:
                predicate_map[infobox_pred] = {}
            fb_props = json.loads(p[1])

            probs = predicate_map[infobox_pred]
            for prop in fb_props:
                if not prop in probs:
                    probs[prop] = 0
                probs[prop] += 1.0
    return predicate_map

def load_baike_ename_title():
    path = os.path.join(result_dir, '360/360_entity_info.json')
    Print('load baike\'s ename and title from [%s]' %path)
    ename_title_map = {}
    for line in tqdm(file(path), total = nb_lines_of(path)):
        bk_url, obj = line.split('\t')
        obj = json.loads(obj)
        ename, title = obj['ename'].encode('utf-8'), obj['title'].encode('utf-8')
        if title != ename:
            ename_title_map[bk_url] = [ename, title]
        else:
            ename_title_map[bk_url] = [ename]
    return ename_title_map

def load_dict(dicts_path):
    dict_names = set()
    for dict_path in dicts_path:
        for line in file(dict_path):
            name = line.rstrip('\n')
            dict_names.add(name)
    return dict_names
        


if __name__ == "__main__":
    s1 = Resource.get_singleton()
    s2 = Resource.get_singleton()
    print s1 == s2
    s = u'《希斯帕尼亚》，西班牙电影，路易斯·霍马、安娜德、胡安·何塞·巴勒斯塔主演。演职员表演员表角色演员备注Galba路易斯·霍马（Llus Homar）Nerea安娜德�阿玛斯（Ana de Armas）Paulo胡安·何塞·巴勒斯塔（Juan Jos Ballesta）Marco何苏斯奥尔梅多（Jesús Olmedo）Viriato罗伯托·恩里奎兹（Roberto Enrquez）TeodoroAntonio Gil-MartinezDarío阿方索巴萨维（Alfonso Bassave）Helena玛努艾拉·维雷丝（Manuela Vells）BárbaraLuz ValdenebroHctor帕布罗·德奎（Pablo Derqui）SabinaÁngela CremonteSandroHovik影片花絮幕后制作西班牙Antena 3电视台大制作黄金时段古装连续剧，讲述了一个西班牙版的《角斗士》的反叛罗马帝国统治的故事，其主要情节和人物维里亚图斯、迦尔巴在两千多年前都有着历史原型。'
    print filter_bad_summary(s)


