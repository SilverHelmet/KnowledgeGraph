#encoding: utf-8
import glob
import os
from ..IOUtil import data_dir
import pandas as pd
import json
import numpy as np 

class Data:
    def __init__(self, sentence):
        self.sentence = sentence
        self.half_add = False
        self.subjs = []
        self.props = []
        self.objs = []
        self.subj_urls = []
        self.prop_uris = []
        self.obj_urls = []
    
    def add(self, subj, prop, obj):
        if self.half_add:
            self.subj_urls.append(subj)
            self.prop_uris.append(prop)
            self.obj_urls.append(obj)
        else:
            self.subjs.append(subj)
            self.props.append(prop)
            self.objs.append(obj)

        self.half_add = not self.half_add

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
            print idx
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
        else:
            subj, prop, obj = row[:3]
            data.add(subj, prop, obj)
    return datas




def process_labeled_data():
    datas_map = {}
    for filepath in glob.glob(data_dir + '/标注数据/*xlsx'):
        print filepath
        datas = load_labeled_data(filepath)
        name = os.path.basename(filepath).split(".")[0]
        datas_map[name] = datas
    



if __name__ == "__main__":
    process_labeled_data()

