#encoding: utf-8
import glob
import os
from ..IOUtil import data_dir, rel_ext_dir, Print
import pandas as pd
import json
import numpy as np 
from ..IOUtil import doc_dir
import os
from .structure import Knowledge, PageInfo
from .entity.naive_ner import NaiveNer
from .entity.ner import NamedEntityReg
# from dependency.relation_extractors import RelTagExtractor
from dependency.verb_relation_simple_extractor import VerbRelationExtractor
from entity.linkers import SeparatedLinker, MatchRelLinker, TopRelatedEntityLinker
from .simple_extractors import SimpleLTPExtractor
from ..schema.schema import Schema
from .util import load_stanford_result

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




def decode(text):
    return str(text).decode('utf-8')

class Data:
    def __init__(self, sentence):
        self.sentence = sentence
        self.half_add = False
        self.knowledges = []
        self.subj, self.prop, self.obj = [None] * 3
        # self.subjs = []
        # self.props = []
        # self.objs = []
        # self.subj_urls = []
        # self.prop_uris = []
        # self.obj_urls = []
    
    def add(self, subj, prop, obj):
        subj = decode(subj)
        prop = decode(prop)
        obj = decode(obj)

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
    



def test_ltp_extractor(datas_map, ner, rel_extractor, linker):

    Print('init extractor')

    base_dir = os.path.join(data_dir, '标注数据')
    stf_results_map = load_stanford_result(os.path.join(base_dir, 'sentences.txt'), os.path.join(base_dir, 'sentences_stanf_nlp.json'))

    ltp_extractor = SimpleLTPExtractor(ner, rel_extractor, linker)

    Print('init finished')

    estimation = {
        "total output": 0,
        'total labeled': 0,
        'right output': 0,
    }
    schema = Schema()
    schema.init()
    for baike_name in datas_map:
        datas = datas_map[baike_name]
        for data in datas:
            sentence = data.sentence
            print sentence
            stf_result = stf_results_map[sentence.encode('utf-8')]
            page_info = PageInfo(baike_name)
            triples, ltp_result = ltp_extractor.parse_sentence(sentence, page_info, stf_result)

            str_entites = self.ner.recognize(sentence, ltp_result, page_info, stf_result)
            
            kl_set = set()
            for kl in data.knowledges:
                # kl_set.add(kl.knowledge())
                kl_set.add("%s\t%s\t%s" %(kl.subj, kl.prop_uri, kl.obj))
                reverse_prop_uri = schema.reverse_property(kl.prop_uri)
                if reverse_prop_uri:
                    kl_set.add("%s\t%s\t%s" %(kl.obj, reverse_prop_uri, kl.subj))

            estimation['total labeled'] += len(data.knowledges)

            for triple in triples:
                info = triple.info(ltp_result)

                subj = ltp_result.text(triple.baike_subj.st, triple.baike_subj.ed)
                obj = ltp_result.text(triple.baike_obj.st, triple.baike_obj.ed)
                prop = triple.fb_rel.fb_prop

                
                estimation['total output'] += 1
                if "%s\t%s\t%s" %(subj, prop, obj) in kl_set:
                    estimation['right output'] += 1
                    print info, 'right'
                else:
                    print info

            for kl in data.knowledges:
                print '\t', kl
    print estimation

    

if __name__ == "__main__":
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_subj_miss = True, ignore_verb_miss = True)
    print "#data = %d, #labeled kl = %d" %(nb_data, nb_kl)

    ner = NamedEntityReg()    

    # rel_extractor = RelTagExtractor()
    rel_extractor = VerbRelationExtractor()

    # entity_linker = TopPopEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    entity_linker = TopRelatedEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    rel_linker = MatchRelLinker()
    linker = SeparatedLinker(entity_linker, rel_linker)

    test_ltp_extractor(datas_map, ner, rel_extractor, linker)




