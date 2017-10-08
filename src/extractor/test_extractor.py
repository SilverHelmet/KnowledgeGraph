#encoding: utf-8
import glob
import os
from ..IOUtil import data_dir
import pandas as pd
import json
import numpy as np 
from .structure import Knowledge
from entity.naive_ner import NaiveNer
from dependency.relation_extractors import RelTagExtractor
from .linkers import SeparatedLinker, PopularityEntityLinker, MatchRelLinker

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
    
    def clear_miss_data(self):
        knowledges = []
        for kl in self.knowledges:
            flag = True
            if kl.subj.find("*") != -1 or kl.prop.find('*') != -1 or kl.obj.find('*') != -1:
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
            sentence = row[0]
            data = Data(sentence)
            datas.append(data)
        else:
            subj, prop, obj = row[:3]
            data.add(subj, prop, obj)
    return datas

def process_labeled_data(ignore_miss):
    datas_map = {}
    nb_data = 0
    nb_kl = 0
    for filepath in glob.glob(data_dir + '/标注数据/*xlsx'):
        print 'load %s' %filepath

        datas = load_labeled_data(filepath)
        if ignore_miss:      
            new_datas = []
            for data in datas:
                data.clear_miss_data()
                if (data.knowledges) > 0:
                    new_datas.append(data)
            datas = new_datas

        nb_data += len(datas)
        for data in datas:
            nb_kl += len(data.knowledges)

        name = os.path.basename(filepath).split(".")[0]
        datas_map[name] = datas
    return datas_map, nb_data, nb_kl
    
if __name__ == "__main__":
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_miss = True)

    
    print "#data = %d, #labeled kl = %d" %(nb_data, nb_kl)
    ner = NaiveNer()    
    rel_extractor = RelTagExtractor()
    entity_linker = PopularityEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    rel_linker = MatchRelLinker()
    linker = SeparatedLinker(entity_linker, rel_linker)

    ltp_extractor = SimpleLTPExtractor(ner, rel_extractor, linker)

    for baike_name in datas_map:
        datas = datas_map[baike_name]
        for data in datas:
            sentence = data.sentence
            triples, ltp_result = ltp_extractor.parse_sentence(sentence)
            print sentence
            for triple in triples:
                print triple.info(ltp_result)
                for kl in data.knowledges:
                    print '\t', kl




