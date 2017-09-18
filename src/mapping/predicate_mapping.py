import sys
from ..IOUtil import result_dir, Print, load_ttl2map
import os
import json
from tqdm import tqdm
from .fb_date import FBDatetime, BaikeDatetime
from .name_mapping import del_space
from ..schema.schema import Schema
from .one2one_mapping_cnt import load_attrs

def extract_name(value):
    suffix = value[-4:]
    assert suffix == '"@en' or suffix == '"@zh'
    name = value[1:-4]
    return name


def load_name_attr(filepaths, totals, fb_entities = None):
    name_map = {}
    for filepath, total in zip(filepaths, totals):
        Print("load name %s" %filepath)
        for line in tqdm(file(filepath), total = total):
            p = line.split('\t')
            key = p[0].decode('utf-8')
            if fb_entities is not None and key not in fb_entities:
                continue
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
            if "fb:common.topic.description" in obj:
                for x in obj['fb:common.topic.description']:
                    name = extract_name(x)
                    name_map[key].append(name)
    return name_map

def load_baike_info(filepath, total, entities = None):
    Print("load baike info from %s" %filepath)
    info_map = {}
    for line in tqdm(file(filepath), total = total):
        p = line.split('\t')
        key = p[0]
        if entities is not None and key not in entities:
            continue
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

def map_time(fb_date, baike_date):
    if fb_date is None or baike_date is None:
        return False
    if fb_date.year != baike_date.year:
        return False
    if fb_date.month == 0 or baike_date.month == 0:
        return True
    if fb_date.month != baike_date.month:
        return False
    if fb_date.day == 0 or baike_date.day == 0:
        return True
    return fb_date.day == baike_date.day

def map_str(fb_str, baike_str):
    if fb_str.startswith('"') and fb_str.endswith('"'):
        fb_str = fb_str[1:-1]
    longer = max(len(fb_str), len(baike_str))
    shorter = min(len(fb_str), len(baike_str))
    if shorter * 1.5 < longer:
        return False
    return fb_str.find(baike_str) != -1 or baike_str.find(fb_str) != -1

def map_value(fb_value, baike_value):
    fb_value = del_space(fb_value)
    baike_value = del_space(baike_value)
    if len(fb_value) == 0 or len(baike_value) == 0:
        return False
    fb_date = FBDatetime.parse_fb_datetime(fb_value)
    if fb_date is not None:
        baike_date = BaikeDatetime.parse(baike_value)
        return map_time(fb_date, baike_date)
    else:
        return map_str(fb_value, baike_value)
 

def extend_fb_ttls(fb_ttls, fb_uri, mediator_ttl_map, schema):
    visited_entities = set([fb_uri])
    for p1, value1 in fb_ttls:
        visited_entities.add(value1)
    stop_extend = False
    extend_cnt = 0
    while not stop_extend:
        extend_cnt += 1
        new_fb_ttls = []
        stop_extend = True
        for p1, value1 in fb_ttls:
            value1_type = schema.expected_type(p1)
            if schema.is_mediator(value1_type):
                for p2, value2 in mediator_ttl_map.get(value1, []):
                    if schema.schema_type(p2) == value1_type and  value2 not in visited_entities:
                        p = '%s^%s' %(p1, p2)
                        new_fb_ttls.append((p, value2))
                        visited_entities.add(value2)
                        value2_type = schema.expected_type(p2)
                        if schema.is_mediator(value2_type):
                            stop_extend = False
            else:
                new_fb_ttls.append((p1, value1))
        fb_ttls = new_fb_ttls
        if extract_cnt >= 2:
            break
    return new_fb_ttls, extend_cnt

def do_predicate_mapping(outpath, mediator_ttl_map, name_map, fb2baike, baike_entity_info, fb_property_path, total):
    schema = Schema()
    schema.init()
    Print("do predicate mapping %s, write to %s" %(fb_property_path, outpath))
    outf = file(outpath, 'w')
    for line in tqdm(file(fb_property_path), total = total):
        p = line.split('\t')
        fb_uri = p[0]
        if not fb_uri in fb2baike:
            continue
        baike_url = fb2baike[fb_uri]
        fb_ttls = json.loads(p[1])
        fb_ttls, _ = extend_fb_ttls(fb_ttls, fb_uri, mediator_ttl_map, schema)
        baike_attr = baike_entity_info[baike_url]

        for name, value in fb_ttls:
            if value in name_map:
                values = name_map[value]
            else:
                values = [value]
            
            for fb_value_name in values:
                for baike_info_name in baike_attr:
                    baike_values = baike_attr[baike_info_name]
                    match = False
                    for baike_value in baike_values:
                        if map_value(fb_value_name, baike_value):
                            match = True
                            break
                    if match:
                        outf.write("{}\t{}\t{}\t{}\t{}\n".format(fb_uri, baike_url, name, baike_info_name, fb_value_name))
        
    outf.close()


if __name__ == "__main__":
    exact_mapping_file = os.path.join(result_dir, "360/mapping/exact_mapping.tsv")
    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
                os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]

    name_map = load_name_attr(name_files, totals)
    mediator_ttl_map = load_ttl2map(os.path.join(result_dir, 'freebase/mediator_med_property.ttl'), total = 50413655)

    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208, entities = None)
    

    fb2baike = load_exact_map(exact_mapping_file)

    fb_property_path = os.path.join(result_dir, 'freebase/entity_property.json')
    outpath = os.path.join(result_dir, '360/mapping/info_predicate_mapping.tsv')
    do_predicate_mapping(outpath, mediator_ttl_map, name_map, fb2baike, baike_entity_info, fb_property_path, total = 53574900)

