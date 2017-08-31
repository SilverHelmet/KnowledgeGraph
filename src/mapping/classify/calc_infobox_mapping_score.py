import json
import os

from tqdm import tqdm

from ...IOUtil import result_dir, load_json_map, Print
from ..predicate_mapping import load_baike_info, load_name_attr, load_ttl2map, extend_fb_ttls
from .gen_fb_property import load_mapping_pairs
from ..one2one_mapping_cnt import load_attrs
from ..predicate_mapping import map_value

def ignore_baike_name_attr(baike_entity_info, baike_name_attrs, url):
    baike_info = baike_entity_info[url]
    for name in baike_name_attrs:
        if name in baike_info:
            baike_info.pop(name)
    return baike_info

def extend_name(fb_info, name_map):
    value_names = []
    for name, value in fb_info:
        if value in name_map:
            values = name_map[value]
        else:
            values = [value]
        value_names.append((name, values))
    return value_names

def find_match(baike_value, fb_info):
    for fb_name, fb_values in fb_info:
        for fb_value in fb_values:
            if map_value(fb_value, baike_value):
                return True
    return False

def calc_infobox_mapping_score(baike2fb_map, baike_entitiy_info, fb_entity_info, fb_name_map, baike_name_attrs):
    baike_name_attrs = set(baike_name_attrs)
    Print('calc mapping score')
    maps = []
    for baike_url in tqdm(baike2fb_map, total = len(baike2fb_map)):
        fb_uris = baike2fb_map[baike_url]
        baike_info = ignore_baike_name_attr(baike_entity_info, baike_name_attrs, baike_url)
        nb_baike_info = len(baike_info)
        for fb_uri in fb_uris:
            fb_info = fb_entity_info.get(fb_uri, [])
            nb_fb_info = len(fb_info)
            fb_info = extend_name(fb_info, fb_name_map)
            match_cnt = 0

            for baike_info_name in baike_info:
                baike_values = baike_info[baike_info_name]
                match = False

                for baike_value in baike_values:
                    if find_match(baike_value, fb_info):
                        match = True
                        break
                if match:
                    match_cnt += 1
            map_obj = {
                'nb_baike_info': nb_baike_info,
                "nb_fb_info": nb_fb_info,
                "#match": match_cnt
            }
            maps.append(map_obj)
    return maps


if __name__ == "__main__":
	mapping_file = os.path.join(result_dir, '360/360_mapping.json')
	out_dir = os.path.join(result_dir, '360/mapping/classify')
	baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
	print "baike2fb_map", len(baike2fb_map)
	print "baike_entities", len(baike_entities)
	print "fb_entities", len(fb_entities)

    name_attrs = load_attrs()

    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
	baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208, entities = baike_entities)
    baike_name_attrs = load_attrs()
	print "baike_entitiy_info", len(baike_entity_info)

    fb_entity_info_path = os.path.join(result_dir, '360/mapping/classify/mapped_fb_entity_info.json')
    fb_entity_info = load_json_map(fb_entity_info_path, total = 6282988)


	name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
			os.path.join(result_dir, 'freebase/entity_alias.json')]
	totals = [39345270, 2197095]
	name_map = load_name_attr(name_files, totals, set(fb_entities))

    map_scores = calc_infobox_mapping_score(baike2fb_map, baike_entity_info, fb_entity_info, name_map, baike_name_attrs)
    out_path = os.path.join(out_dir, 'map_scores.json')
    outf = file(out_path, 'w')
    for map_obj in map_scores:
        outf.write(json.dumps(map_obj) + '\n')
    outf.close()
    
	# print "name_map", len(name_map)
	# description_map = load_name_attr([os.path.join(result_dir, 'freebase/entity_description.json')], totals = [6426977], fb_entities = set(fb_entities))
	





	