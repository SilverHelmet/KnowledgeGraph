import os
from ...IOUtil import result_dir, Print, data_dir, nb_lines_of, classify_dir
from tqdm import tqdm
import json

def load_mappings(mapping_path = None):
    if mapping_path is None:
        mapping_path = os.path.join(result_dir, '360/mapping/classify/mappings.txt')
        total = 1129601
    else:
        total = nb_lines_of(mapping_path)
    Print('load mappings from [%s]' %mapping_path)
    
    baike2fb = {}
    for line in tqdm(file(mapping_path), total = total):
        p = line.split('\t')
        baike_url = p[0]
        fb_uris = json.loads(p[1])
        baike2fb[baike_url] = fb_uris
    return baike2fb

def load_baike_entity_class(filepath = None, baike_urls = None, simple = False):
    if filepath is None:
        filepath = os.path.join(data_dir, 'entityHypernym_v16_all_ex_darts.txt')
    Print("load baike entity class from [%s]" %filepath)
    bk2cls = {}
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        if simple:
            url, cls = line.strip().split('\t')
        else:
            name, popular, url, cls, small_cl = line.strip().split('\t')
        if cls == "NO_TYPE":
            continue
        if url.startswith('http://'):
            url = url[7:]
        if baike_urls is None or url in baike_urls:
            bk2cls[url] = cls.split(" ")
    return bk2cls


def load_mappings_witd_score(filepath, threshold = 0.1):
    Print('load mappings from [%s] with score' %filepath)
    mappings = []
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        bk_url, fb_uri, score = line.split('\t')
        if float(score) > threshold:
            mappings.append((bk_url, fb_uri))
    return mappings

def load_match_result(filepath = None):
    if filepath is None:
        filepath = os.path.join(classify_dir, 'mapping_result.tsv')
    bk2fb = {}
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        bk_url, fb_uri = line.strip().decode('utf-8').split('\t')
        bk2fb[bk_url] = fb_uri
    return bk2fb



def load_fb_type(filepath = None, fb_uris = None):
    if filepath is None:
        filepath = os.path.join(classify_dir, 'fb_entity_type.json')
    Print('load freebase type from [%s]' %filepath)
    fb_types = {}
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        fb_uri, types  = line.split('\t')
        if fb_uris is not None and fb_uri not in fb_uris:
            continue
        types = json.loads(types)['fb:type.object.type']
        fb_types[fb_uri] = types
    return fb_types

def load_baike_attr_names(filepath, total, baike_urls = None):
    Print("load baike attr's name from %s" %filepath)
    info_map = {}
    
    for line in tqdm(file(filepath), total = total):
        p = line.split('\t')
        key = p[0].decode('utf-8')
        if baike_urls is not None and key not in baike_urls:
            continue
        obj = json.loads(p[1])
        info = obj.get('info', {})
        names = info.keys()
        info_map[key] = names
    return info_map



if __name__ == "__main__":
    pass