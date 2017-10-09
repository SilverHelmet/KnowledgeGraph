from ..IOUtil import rel_ext_dir, Print, nb_lines_of
import os
import json
from tqdm import tqdm

class BaikeInfo:
    def __init__(self, pop, types):
        self.pop = pop
        self.types = types

def load_mappings(filepath = None):
    if filepath is None:
        filepath = os.path.join(rel_ext_dir, 'mapping_result.tsv')
    Print('load mappings from [%s]' %filepath)
    bk2fb = {}
    for line in file(filepath):
        bk_url, fb_uri = line.strip().decode('utf-8'). split('\t')
        bk2fb[bk_url] = fb_uri
    return bk2fb

def load_bk_entity_pop(filepath = None):
    if filepath is None:
        filepath = os.path.join(rel_ext_dir, 'baike_static_info.tsv')
        total = 21710208
    else:
        total = nb_lines_of(filepath)
    Print('load baike popularity from [%s]'  %filepath)
    
    pop_map = {}
    for line in tqdm(file(filepath), total = total):
        p = line.strip().decode('utf-8').split('\t')
        bk_url = p[0]
        pop = int(p[2])
        pop_map[bk_url] = pop
    return pop_map

def load_bk_types(filepath = None):
    if filepath is None:
        filepath = os.path.join(rel_ext_dir, 'baike_static_info.tsv')
        total = 21710208
    else:
        total = nb_lines_of(filepath)
    Print('load baike types from [%s]'  %filepath)

    type_map = {}
    for line in tqdm(file(filepath), total = total):
        p = line.strip().decode('utf-8').split('\t')
        bk_url = p[0]
        types = json.loads(p[3])
        type_map[bk_url] = types
    return type_map

def load_bk_static_info(filepath):
    total = nb_lines_of(filepath)
    info_map = {}
    Print("load baike static info from [%s]" %filepath)
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        p = line.strip().split('\t')
        bk_url = p[0]
        pop = int(p[2])
        types = json.loads(p[3])
        info = BaikeInfo(pop, types)
        info_map[bk_url] = info
    return info_map


def load_name2baike(filepath = None):
    if filepath is None:
        filepath = os.path.join(rel_ext_dir, 'baike_names.tsv')
        total = nb_lines_of(filepath)
    else:
        total = nb_lines_of(filepath)
    name2bk = {}
    Print('load name -> baike from %s' %filepath)
    for line in tqdm(file(filepath), total = total):
        # p = line.strip().decode('utf-8').split('\t')
        p = line.strip().split('\t')
        bk_url = p[0]
        names = p[1:]
        for name in names:
            if not name in name2bk:
                name2bk[name] = []
            name2bk[name].append(bk_url)
    return name2bk





