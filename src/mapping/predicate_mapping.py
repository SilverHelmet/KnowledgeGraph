import sys
from ..IOUtil import result_dir, Print, load_ttl2map
import os
import json
from tqdm import tqdm
from .fb_date import FBDatetime, BaikeDatetime
from .name_mapping import del_space
from ..schema.schema import Schema
from .one2one_mapping_cnt import load_baike_name_attrs
from .classify.simple_classify import make_key
from ..fb_process.process_fb_result import process_fb_value
from ..baike_process.process_entity_info import del_book_bracket, ignore_baike_name_attr

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
    fb_str = process_fb_value(fb_str)
    baike_str = del_book_bracket(baike_str)

    longer = max(len(fb_str), len(baike_str))
    shorter = min(len(fb_str), len(baike_str))
    if shorter * 1.5 < longer:
        return False
    return fb_str.find(baike_str) != -1 or baike_str.find(fb_str) != -1

def map_value(fb_value, baike_value, cache):
    # fb_value = del_space(fb_value).strip()
    # baike_value = del_space(baike_value).strip()
    
    if len(fb_value) == 0 or len(baike_value) == 0:
        return False
    fb_key = 'fb##' + fb_value
    bk_key = 'bk##' + baike_value
    if not fb_key in cache:
        cache[fb_key] = FBDatetime.parse_fb_datetime(fb_value)
    fb_date = cache[fb_key]
    fb_date = FBDatetime.parse_fb_datetime(fb_value)
    if fb_date is not None:
        if not bk_key in cache:
            cache[bk_key] = BaikeDatetime.parse(baike_value)
        baike_date = cache[bk_key]
        return map_time(fb_date, baike_date)
    else:
        return map_str(fb_value, baike_value)
 

def extend_fb_ttls(fb_ttls, fb_uri, mediator_ttl_map, schema):
    visited_entities = set([fb_uri])
    new_fb_ttls = []
    for p1, value1 in fb_ttls:
        if not schema.is_mediator(schema.schema_type(p1)):
            new_fb_ttls.append((p1, value1))
            visited_entities.add(value1)
    fb_ttls = new_fb_ttls

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
        if extend_cnt >= 2:
            break
    new_fb_ttls = []
    for p, v in fb_ttls:
        if not schema.is_mediator_prop(p) and p.split("^")[-1] != u'fb:music.release_track.track_number':
            new_fb_ttls.append((p, v))

    return new_fb_ttls

def do_predicate_mapping(outpath, name_map, fb2baike, baike_entity_info, fb_property_path, score_map, total):
    baike_name_attrs = load_baike_name_attrs()
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
        score = score_map[make_key(baike_url, fb_uri)]
        fb_ttls = json.loads(p[1])
        # fb_ttls, _ = extend_fb_ttls(fb_ttls, fb_uri, mediator_ttl_map, schema)
        # baike_attr = baike_entity_info[baike_url]
        baike_info = ignore_baike_name_attr(baike_entity_info, baike_name_attrs, baike_url)
        cache = {}
        for name, value in fb_ttls:
            if value in name_map:
                values = name_map[value]
            else:
                values = [value]
            
            for fb_value_name in values:
                for baike_info_name in baike_info:
                    baike_values = baike_info[baike_info_name]
                    for baike_value in baike_values:
                        if map_value(fb_value_name, baike_value, cache):
                            outf.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(fb_uri, baike_url, name, baike_info_name, fb_value_name, baike_value, score))
                        
        
    outf.close()

def load_exact_mappings(filepath, threshold):
    Print("load exact mapping from [%s]" %filepath)
    fb2bk = {}
    bk_es = set()
    score_map = {}
    for line in file(filepath):
        p = line.strip().split('\t')
        if len(p) == 3:
            bk, fb, score = p
            score = float(score)
            if score > threshold:
                fb2bk[fb] = bk
                bk_es.add(bk)
                score_map[make_key(bk, fb)] = score
        else:
            bk, fb = p
            score = 1
            fb2bk[fb] = bk
            bk_es.add(bk)
            score_map[make_key(bk, fb)] = score
    return fb2bk, bk_es, score_map



if __name__ == "__main__":
    # exact_mapping_file = os.path.join(result_dir, "360/mapping/exact_mapping.tsv")
    # fb2baike = load_exact_map(exact_mapping_file)
    if len(sys.argv) >= 3:
        mapping_path = sys.argv[1]
    else:
        mapping_path = os.path.join(result_dir, '360/mapping/classify/good_one2one_mappings.txt')
    fb2baike, baike_entities, score_map = load_exact_mappings(mapping_path, 0.01)


    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
                os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]

    name_map = load_name_attr(name_files, totals)
    # mediator_ttl_map = load_ttl2map(os.path.join(result_dir, 'freebase/mediator_med_property.ttl'), total = 50413655)

    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208, entities = baike_entities)
    Print("#baike entity info = %d" %len(baike_entity_info))
    

    fb_property_path = os.path.join(result_dir, '360/mapping/classify/mapped_fb_entity_info.json')
    if len(sys.argv) >= 3:
        outpath = sys.argv[2]
    else:
        outpath = os.path.join(result_dir, '360/mapping/one2one_info_predicate_mapping.tsv')
    do_predicate_mapping(outpath, name_map, fb2baike, baike_entity_info, fb_property_path, score_map, total = 6282988)

