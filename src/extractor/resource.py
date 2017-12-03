#encoding: utf-8
from src.IOUtil import *
from ltp import LTP
from src.schema.schema import Schema
import os
import json
from tqdm import tqdm


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
        extra_path = os.path.join(extra_name_dir, 'summary_extra_name.tsv')
        extra_bracket_path = os.path.join(extra_name_dir, 'summary_extra_bracket_name.tsv')
        extra_team_path = os.path.join(extra_name_dir, 'extra_team_name.tsv')
        
        name2bk, url2names = load_baike_names_resource([path, extra_path, extra_bracket_path, extra_team_path])

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
            summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary_with_infobox.json')
            # infobox_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
            self.dict['baike_summary_with_infobox'] = load_summary(summary_path)
        return self.dict['baike_summary_with_infobox']

    def get_predicate_map(self):
        if not "predicate_map" in self.dict:
            main_filepath = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
            dataset_path = os.path.join(dataset_dir, 'summary_dataset.tsv.v1.predicate_map.json')
            extra_path = os.path.join(doc_dir, 'human_add_predicate_map.json')
            
            self.dict['predicate_map'] = load_predicate_map([main_filepath, dataset_path], extra_path)
        return self.dict['predicate_map']

    def get_vertical_domain_baike_dict(self):
        if not "vt_domain_bk_dict" in self.dict:
            path = os.path.join(dict_dir, 'vertical_domain_baike_dict.txt')
            Print("load name dict from [%s]" %path)
            self.dict['vt_domain_bk_dict'] = load_file(path)
        return self.dict['vt_domain_bk_dict']

    def get_baike_ename_title(self):
        if not "baike_ename_title" in self.dict:
            self.dict['baike_ename_title'] = load_url2names(os.path.join(rel_ext_dir, 'baike_ename_title.tsv'))
        return self.dict['baike_ename_title']

    def get_location_dict(self):
        if not 'location_dict' in self.dict:
            dicts = ['province.txt', 'citytown.txt', 'nationality.txt']
            dicts_path = [os.path.join(dict_dir, x) for x in dicts]
            Print('load location dict from [%s]' %" ".join(dicts))
            self.dict['location_dict'] = load_dict(dicts_path)
        return self.dict['location_dict']

    def get_team_suffix_dict(self):
        if not "team_suffix_dict" in self.dict:
            self.dict['team_suffix_dict'] = load_extra_team_suffix_dict()
        return self.dict['team_suffix_dict']

    def get_half_named_fb_info(self):
        if not 'half_named_fb_info' in  self.dict:
            path = os.path.join(rel_ext_dir, 'mapped_fb_entity_info_processed.json')
            self.dict['half_named_fb_info'] = load_half_named_fb_info(path)
        return self.dict['half_named_fb_info']

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

def load_url2names(filepath):
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
        if not os.path.exists(filepath):
            continue
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

def load_predicate_map(filepaths, extra_path = None):
    predicate_map  = {}
    for filepath in filepaths:
        if not os.path.exists(filepath):
            continue
        Print('load predicate map from %s' %filepath)
        for line in file(filepath):
            p = line.split('\t')
            infobox_pred = p[0]
            mappings = json.loads(p[1])[:10]
            if not infobox_pred in predicate_map:
                predicate_map[infobox_pred] = {}
            probs = predicate_map[infobox_pred]
            total = None
            for prop, occur in mappings:
                if not prop in probs:
                    probs[prop] = (0, 0)
                cnt, total = map(int, occur.split('/'))
                pre_cnt, pre_total = probs[prop]
                probs[prop] = (pre_cnt + cnt, pre_total)
            if total:
                for prop in probs:
                    cnt, pre_total = probs[prop]
                    probs[prop] = (cnt, pre_total + total)
            predicate_map[infobox_pred] = probs

    for infobox_pred in predicate_map:
        prop_probs = predicate_map[infobox_pred]
        error_prop = set()
        for fb_prop in prop_probs:
            cnt, total = prop_probs[fb_prop]
            if cnt >= 50 or cnt / (total + 0.0) >= 0.05:
                prop_probs[fb_prop] = cnt / (total + 3.0)
            else:
                error_prop.add(fb_prop)
        for prop in error_prop:
            prop_probs.pop(prop)

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



def load_dict(dicts_path):
    dict_names = set()
    for dict_path in dicts_path:
        for line in file(dict_path):
            name = line.rstrip('\n')
            dict_names.add(name)
    return dict_names
        
def load_summary(summary_path):
    Print("load summary from [%s]" %summary_path)
    summary_map = {}
    for line in tqdm(file(summary_path), total = nb_lines_of(summary_path)):
        bk_url, summary = line.split('\t')
        summary = json.loads(summary)['summary'].encode('utf-8')
        summary_map[bk_url] = summary
    return summary_map

def load_extra_team_suffix_dict():
    team_suffix_dict_path = os.path.join(extra_name_dir, 'extra_team_name_dict.tsv')
    team_suffix_dicts = SuffixDicts.load_from_file(team_suffix_dict_path)
    return team_suffix_dicts


class BaikeInfo:
    def __init__(self, pop, types):
        self.pop = pop
        self.types = types

class SuffixDicts:
    def __init__(self):
        self.dicts = {}
        self.suffixes = set()
        self.activated_suffixes = set()
        self.url2suffix = {}

    def add_url_with_suffix(self, bk_url, suffix):
        self.url2suffix[bk_url] = suffix

    def add_name_with_suffix(self, bk_url, name, suffix):
        if not suffix in self.dicts:
            self.dicts[suffix] = {}
            self.suffixes.add(suffix)
        team_dict = self.dicts[suffix]
        if not name in team_dict:
            team_dict[name] = []
        team_dict[name].append(bk_url)

    def search_name(self, name):
        urls = []
        for suffix in self.activated_suffixes:
            suf_dict = self.dicts[suffix]
            urls.extend(suf_dict.get(name, []))
        return urls

    def meet_url(self, bk_url):
        if bk_url in self.url2suffix:
            suffix = self.url2suffix[bk_url]
            # print 'add suffix', suffix, bk_url
            self.activated_suffixes.add(suffix)

    def refresh(self):
        self.activated_suffixes.clear()

    @staticmethod
    def load_from_file(filepath):
        Print('load team\'s dict from [%s]' %filepath)
        suf_dicts = SuffixDicts()
        for line in file(filepath):
            p = line.strip().split('\t')
            suffix = p[0]
            bk_url = p[1]
            suf_dicts.add_url_with_suffix(bk_url, suffix)
            names = p[2:]
            for name in names:
                suf_dicts.add_name_with_suffix(bk_url, name, suffix)
        return suf_dicts

def load_half_named_fb_info(path):
    Print('load half naemd fb info from [%s]' %os.path.basename(path))

    fb_info = {}
    for line in tqdm(file(path), total = nb_lines_of(path)):
        fb_uri, rels = line.split('\t')
        rels = json.loads(rels)
        total_names = set()
        for prop in rels:
            values = rels[prop]
            total_names.update(values)
            
            if len(values) > 20:
                rels[prop] = set(values)
        rels['total'] = total_names
        fb_info[fb_uri] = rels
        
    return fb_info


if __name__ == "__main__":
    s1 = Resource.get_singleton()
    s2 = Resource.get_singleton()
    print s1 == s2
    s = u'《希斯帕尼亚》，西班牙电影，路易斯·霍马、安娜德、胡安·何塞·巴勒斯塔主演。演职员表演员表角色演员备注Galba路易斯·霍马（Llus Homar）Nerea安娜德�阿玛斯（Ana de Armas）Paulo胡安·何塞·巴勒斯塔（Juan Jos Ballesta）Marco何苏斯奥尔梅多（Jesús Olmedo）Viriato罗伯托·恩里奎兹（Roberto Enrquez）TeodoroAntonio Gil-MartinezDarío阿方索巴萨维（Alfonso Bassave）Helena玛努艾拉·维雷丝（Manuela Vells）BárbaraLuz ValdenebroHctor帕布罗·德奎（Pablo Derqui）SabinaÁngela CremonteSandroHovik影片花絮幕后制作西班牙Antena 3电视台大制作黄金时段古装连续剧，讲述了一个西班牙版的《角斗士》的反叛罗马帝国统治的故事，其主要情节和人物维里亚图斯、迦尔巴在两千多年前都有着历史原型。'
    print filter_bad_summary(s)


