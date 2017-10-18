#encoding: utf-8
import glob
import os
from ..IOUtil import data_dir, rel_ext_dir, Print, cache_dir
import pandas as pd
import json
import numpy as np 
from ..IOUtil import doc_dir
import os
from .structure import Knowledge, PageInfo, BaikeEntity
from .entity.naive_ner import NaiveNer
from .entity.ner import NamedEntityReg
# from dependency.relation_extractors import RelTagExtractor
from dependency.verb_relation_advanced_extractor import VerbRelationExtractor
from entity.linkers import SeparatedLinker, MatchRelLinker, PageMemoryEntityLinker
from .simple_extractors import SimpleLTPExtractor
from ..schema.schema import Schema
from .util import load_stanford_result, get_url_domains, load_important_domains
from .ltp import LTP

def load_same_linkings():
    path = os.path.join(doc_dir, 'same_links.tsv')
    link_map = {}
    for line in file(path):
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        p = line.strip().split('\t')
        for link in p[1:]:
            link_map[link] = p[0]
    return link_map

def load_url_map():
    path = os.path.join(data_dir, '实体标注/urls.txt')
    url_map = {}
    for line in file(path):
        line = line.strip()
        p = line.split('\t')
        if len(p) == 2:
            url_map[p[0]] = p[1]
    return url_map

def load_links_map(filepath):
    link_maps = {}
    for line in file(filepath):
        p = line.strip().split('\t')
        sentence = p[0]
        links = json.loads(p[1])
        m = {}
        for name in links:
            m[name.encode('utf-8')] = BaikeEntity.load_from_obj(links[name])
        link_maps[sentence] = m
    return link_maps


def decode(text):
    return str(text).decode('utf-8')

class Data:
    def __init__(self, sentence):
        self.sentence = sentence
        self.half_add = False
        self.knowledges = []
        self.subj, self.prop, self.obj = [None] * 3

    
    def add(self, subj, prop, obj):

        subj = decode(subj)
        prop = decode(prop)
        obj = decode(obj)
        if subj.startswith('https://'):
            subj = subj[len('https://'):]
        if obj.startswith('https://'):
            obj = obj[len('https://'):]



        if self.half_add:
            self.knowledges.append(Knowledge(self.subj, self.prop, self.obj, subj, prop, obj))
        else:
            self.subj, self.prop, self.obj = subj, prop, obj

        self.half_add = not self.half_add
    
    def clear_miss_data(self, ignore_subj_miss, ignore_verb_miss):
        knowledges = []
        for kl in self.knowledges:
            flag = True
            if ignore_subj_miss and (kl.subj.find("*") != -1 or kl.obj.find('*') != -1):
                flag = False
            if ignore_verb_miss and kl.prop.find('*') != -1:
                flag = False
            if kl.obj.find('/') != -1:
                flag = False
            if flag:
                knowledges.append(kl)
            else:
                pass
        self.knowledges = knowledges 



def parse_title(row):
    title = row[0]
    x = row[1]
    if type(row[1]) is float:
        return title
    else:
        return title +  '\t' + row[1]

def load_labeled_data(filepath):
    table = pd.read_excel(filepath, header = None)
    title = None
    sentence = None
    datas = []
    data = None
    for idx, row in table.iterrows():
        if title is None:
            title = parse_title(row)
            continue
        if row[0] == '$':
            assert data.half_add == False
            sentence = None
            data = None
            continue
        if row[0] == '$$':
            title = None
            assert sentence is None and data is None
            continue
        if sentence is None:
            sentence = row[0].strip()
            data = Data(sentence)
            datas.append(data)
        else:
            subj, prop, obj = row[:3]
            data.add(subj, prop, obj)
    return datas

def process_labeled_data(ignore_subj_miss, ignore_verb_miss):
    datas_map = {}
    nb_data = 0
    nb_kl = 0
    for filepath in glob.glob(data_dir + '/标注数据/*xlsx'):
        # print 'load %s' %filepath

        datas = load_labeled_data(filepath)
        if ignore_subj_miss or ignore_verb_miss:      
            new_datas = []
            for data in datas:
                data.clear_miss_data(ignore_subj_miss, ignore_verb_miss)
                if len(data.knowledges) > 0:
                    new_datas.append(data)
            datas = new_datas

        nb_data += len(datas)
        for data in datas:
            nb_kl += len(data.knowledges)

        name = os.path.basename(filepath).split(".")[0]
        if name == '塞尔达传说时之笛':
            name = '塞尔达传说:时之笛'
        datas_map[name] = datas
    return datas_map, nb_data, nb_kl
    



def test_ltp_extractor(datas_map, ner, rel_extractor, linker, ltp, schema):

    base_dir = os.path.join(data_dir, '标注数据')
    stf_results_map = load_stanford_result(os.path.join(base_dir, 'sentences.txt'), os.path.join(base_dir, 'sentences_stanf_nlp.json'))

    link_maps = None
    # link_maps = load_links_map(os.path.join(cache_dir, 'link_map.json'))
    ltp_extractor = SimpleLTPExtractor(ner, rel_extractor, linker, ltp, link_maps is None)

    url2names = linker.entity_linker.url2names
    bk_info_map = linker.entity_linker.bk_info_map
    url_map = load_url_map()
    important_domains = load_important_domains()
    same_link_map = load_same_linkings()

    estimation = {
        "total output": 0,
        'total labeled': 0,
        'right output': 0,
    }

    str_estimation = {
        "total output": 0,
        'total labeled': 0,
        'right output': 0,
    }

    for baike_name in datas_map:
        datas = datas_map[baike_name]
        url = url_map[baike_name]
        # print baike_name
        # print url
        names = url2names[url]
        types = bk_info_map[url].types
        page_info = PageInfo(baike_name, names, url, get_url_domains(types, important_domains))
        linker.entity_linker.start_new_page()
        for data in datas:
            sentence = data.sentence.encode('utf-8')
            # if sentence != '2008年6月23日，刘德华与朱丽倩在美国拉斯维加斯注册结婚 。':
            #     continue
            print sentence
            stf_result = stf_results_map[sentence]
            triples, ltp_result,  = ltp_extractor.parse_sentence(sentence, page_info, stf_result, link_maps)
            
            kl_set = set()
            str_set = set()
            for kl in data.knowledges:
                
                kl.subj_url = same_link_map.get(kl.subj_url, kl.subj_url)
                kl.obj_url = same_link_map.get(kl.obj_url, kl.obj_url)

                str_set.add("%s\t%s\t%s" %(kl.subj_url, kl.prop, kl.obj_url))
                str_set.add("%s\t%s\t%s" %(kl.obj_url, kl.prop, kl.subj_url))

                kl_set.add("%s\t%s\t%s" %(kl.subj_url, kl.prop_uri, kl.obj_url))
                reverse_prop_uri = schema.reverse_property(kl.prop_uri)

                
                if reverse_prop_uri:
                    kl_set.add("%s\t%s\t%s" %(kl.obj_url, reverse_prop_uri, kl.subj_url))

            estimation['total labeled'] += len(data.knowledges)
            str_estimation['total labeled'] += len(data.knowledges)
            for triple in triples:
                str_estimation['total output'] += 1

                subj = ltp_result.text(triple.baike_subj.st, triple.baike_subj.ed)
                obj = ltp_result.text(triple.baike_obj.st, triple.baike_obj.ed)
                rel = ltp_result.text(triple.fb_rel.st, triple.fb_rel.ed)
                

                subj_url = same_link_map.get(triple.baike_subj.baike_url, triple.baike_subj.baike_url)
                obj_url = same_link_map.get(triple.baike_obj.baike_url, triple.baike_obj.baike_url)
                prop = triple.fb_rel.fb_prop
                
                triple_str = "%s\t%s\t%s" %(subj_url, rel, obj_url)

                if triple_str in str_set:
                    flag_str = 'str_right'
                    str_estimation['right output'] += 1
                else:
                    flag_str = "str_error"
                    
                if prop == 'None':
                    info = "%s:%s\t%s\t%s:%s" %(subj, subj_url, rel, obj, obj_url)
                    print "\t%s\t%s" %(info, flag_str)
                    continue

                info = triple.info(ltp_result)
                estimation['total output'] += 1
                if "%s\t%s\t%s" %(subj_url, prop, obj_url) in kl_set or "%s\t%s\t%s" %(subj_url, prop.split("^")[0], obj_url) in kl_set or "%s\t%s\t%s" %(subj_url, prop.split("^")[-1], obj_url) in kl_set:
                    estimation['right output'] += 1
                    print '\t%s\t%s' %(info, 'full_right')
                else:
                    print '\t%s\t%s' %(info, 'full_error')

            # str_estimation['total labeled'] += len(data.knowledges)
            # str_estimation['total output'] += len(half_linked_triples)
            # for triple in half_linked_triples:
                
            #     subj = ltp_result.text(triple.baike_subj.st, triple.baike_subj.ed)
            #     obj = ltp_result.text(triple.baike_obj.st, triple.baike_obj.ed)
            #     subj_url = same_link_map.get(triple.baike_subj.baike_url, triple.baike_subj.baike_url)
            #     obj_url = same_link_map.get(triple.baike_obj.baike_url, triple.baike_obj.baike_url)
            #     rel = ltp_result.text(triple.str_rel.st, triple.str_rel.ed)

            #     triple_str = "%s\t%s\t%s" %(subj_url, rel, obj_url)
            #     info = "%s:%s\t%s\t%s:%s" %(subj, subj_url, rel, obj, obj_url)
            #     if triple_str in str_set:
            #         str_estimation['right output'] += 1
            #         print "\t%s\t%s" %(info, 'str_right')
            #     else:
            #         print "\t%s\t%s" %(info, 'str_error')

            for kl in data.knowledges:
                print '\t\t%s' %kl.info()
    print estimation
    print str_estimation
    ltp_extractor.finish()

    

if __name__ == "__main__":
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_subj_miss = True, ignore_verb_miss = True)
    print "#data = %d, #labeled kl = %d" %(nb_data, nb_kl)

    ltp = LTP(None)
    ner = NamedEntityReg(ltp)  

    # rel_extractor = RelTagExtractor()
    rel_extractor = VerbRelationExtractor()

    schema = Schema()
    schema.init(init_type_neighbor = True)

    entity_linker = PageMemoryEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    rel_linker = MatchRelLinker()
    linker = SeparatedLinker(entity_linker, rel_linker, schema)

    test_ltp_extractor(datas_map, ner, rel_extractor, linker, ltp, schema)

