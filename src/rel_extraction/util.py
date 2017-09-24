from ..IOUtil import rel_ext_dir, Print, nb_lines_of
import os
import json
from tqdm import tqdm

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
    Print('load entity popularity from [%s]'  %filepath)
    
    pop_map = {}
    for line in tqdm(file(filepath), total = total):
        p = line.strip().decode('utf-8').split('\t')
        bk_url = p[0]
        pop = int(p[2])
        pop_map[bk_url] = pop
    return pop_map

def load_name2baike(filepath = None):
    if filepath is None:
        filepath = os.path.jion(rel_ext_dir, 'baike_names.tsv')
        total = None
    else:
        total = nb_lines_of(filepath)
    name2bk = {}
    for line in file(filepath):
        p = line.strip().decode('utf-8').split('\t')
        bk_url = p[0]
        names = p[1:]
        for name in names:
            if not name in name2bk:
                name2bk[name] = []
            name2bk[name].append(bk_url)
    return name2bk





