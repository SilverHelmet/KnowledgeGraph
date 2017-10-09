#encoding: utf-8
import glob
import os
from ..IOUtil import data_dir, rel_ext_dir, Print
import pandas as pd
import json
import numpy as np 
from .structure import Knowledge
from .entity.naive_ner import NaiveNer
from .entity.ner import NamedEntityReg
from dependency.relation_extractors import RelTagExtractor
from entity.linkers import SeparatedLinker, PopularityEntityLinker, MatchRelLinker, TopPopEntityLinker
from .simple_extractors import SimpleLTPExtractor
from .entity.test import extract_stanford_result
from ..schema.schema import Schema

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
                if len(data.knowledges) > 0:
                    new_datas.append(data)
            datas = new_datas

        nb_data += len(datas)
        for data in datas:
            nb_kl += len(data.knowledges)

        name = os.path.basename(filepath).split(".")[0]
        datas_map[name] = datas
    return datas_map, nb_data, nb_kl

def load_stanford_result(sentence_path, stanford_result_path):
    sentence_inf = file(sentence_path)
    stanford_inf = file(stanford_result_path)
    sentences = []
    results = []
    while True:
        
        sentence = sentence_inf.readline().strip()
        if sentence == "":
            break
        sentence = sentence.strip()
        sentences.append(sentence)

        stanford_result_line = stanford_inf.readline()
        results.append(json.loads(stanford_result_line))
    sentence_inf.close()
    stanford_inf.close()

    result_map = {}
    results = extract_stanford_result(results, sentences)
    for idx in range(len(sentences)):
        s = sentences[idx]
        result = results[idx]
        result_map[s] = result
    return result_map
        



def test_ltp_extractor():
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_miss = True)

    
    print "#data = %d, #labeled kl = %d" %(nb_data, nb_kl)
    Print('init extractor')

    base_dir = os.path.join(data_dir, '标注数据')
    stf_results_map = load_stanford_result(os.path.join(base_dir, 'sentences.txt'), os.path.join(base_dir, 'sentences_stanf_nlp.json'))

    ner = NamedEntityReg()    
    rel_extractor = RelTagExtractor()
    entity_linker = TopPopEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    rel_linker = MatchRelLinker()
    linker = SeparatedLinker(entity_linker, rel_linker)

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
            stf_result = stf_results_map[sentence.encode('utf-8')]
            triples, ltp_result = ltp_extractor.parse_sentence(sentence, None, stf_result)
            
            kl_set = set()
            for kl in data.knowledges:
                kl_set.add(kl.knowledge())
                reverse_prop = schema.reverse_property(kl.prop)
                if reverse_prop:
                    kl_set.add("%s\t%s\t%s" %(kl.obj, reverse_prop, kl.subj))

            estimation['total labeled'] += len(kl_set)

            for triple in triples:
                info = triple.info(ltp_result)
                print info
                estimation['total output'] += 1
                if info in kl_set:
                    estimation['total output'] += 1

            for kl in data.knowledges:
                print '\t', kl
    print estimation

if __name__ == "__main__":
    test_ltp_extractor()




