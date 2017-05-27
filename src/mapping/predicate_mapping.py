import sys
from ..IOUtil import result_dir, Print
import os
import json
from tqdm import tqdm

def extract_name(value):
    suffix = value[-4:]
    assert suffix == '"@en' or suffix == '"@zh'
    name = value[1:-4]
    return name


def load_name_attr(filepaths, totals):
    name_map = {}
    for filepath, total in zip(filepaths, totals):
        Print("load name %s" %filepath)
        for line in tqdm(file(filepath), total = total):
            p = line.split('\t')
            key = p[0].decode('utf-8')
            if not key in name_map:
                name_map[key] = []
            obj = json.loads(p[1])
            if "fb:type.object.name" in obj:
                for x in obj['fb:type.object.name']:
                    name = extract_name(x)
                    name_map[key].append(name)
            if "fb:common.topic.alias" in obj:
                for x in obj['fb:common.topic.alias']:
                    name = extract_name(x)
                    name_map[key].append(name)
    return name_map

def load_baike_info(filepath, total):
    Print("load baike info from %s" %filepath)
    info_map = {}
    for line in tqdm(file(filepath), total = total):
        p = line.split('\t')
        key = p[0]
        obj = json.loads(p[1])
        attr = {}
        if 'ename' in obj:
            attr['ename'] = [obj['ename']]
        if 'title' in obj:
            attr['title'] = [obj['title']]
        info = obj.get('info', {})
        for name in info:
            attr[name] = info[name]
        info_map[key] = attr
    return info_map

def load_exact_map(exact_map_path, total = 558541):
    fb2baike = {}
    Print("load exact map %s" %exact_map_path)
    for line in tqdm(file(exact_map_path), total = total):
        p = line.split('\t')
        baike_url = p[0]
        fb_uri = p[1]
        fb2baike[fb_uri] = baike_url
    return fb2baike

def do_predicate_mapping(name_map, fb2baike, baike_entity_info, fb_property_path, total):
    for line in tqdm(file(fb_property_path), total = total):
        pass


if __name__ == "__main__":
    exact_mapping_file = os.path.join(result_dir, "360/mapping/exact_mapping.tsv")
    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'), 
                os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]

    # name_map = load_name_attr(name_files, totals)

    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    # baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208)
    
    print baike_entity_info['baike.so.com/doc/6692614-6906520.html']

    exact_map_path = os.path.join(result_dir, '360/mapping/exact_mapping.tsv')
    fb2baike = load_exact_map(exact_map_path)

    # fb_property_path = os.path.join(result_dir, 'entity_property.json')
    # do_predicate_mapping(name_map, fb2baike, baike_entity_info, fb_property_path, total = 53574900)