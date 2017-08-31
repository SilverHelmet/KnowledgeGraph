import json
import os

from tqdm import tqdm

from ...IOUtil import result_dir, load_json_map
from ..predicate_mapping import load_baike_info, load_name_attr, load_ttl2map, extend_fb_ttls
from .gen_fb_property import load_mapping_pairs



if __name__ == "__main__":
	mapping_file = os.path.join(result_dir, '360/360_mapping.json')
	out_dir = os.path.join(result_dir, '360/mapping/classify')
	baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
	print "baike2fb_map", len(baike2fb_map)
	print "baike_entities", len(baike_entities)
	print "fb_entities", len(fb_entities)

    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
	baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208, entities = baike_entities)
	print "baike_entitiy_info", len(baike_entity_info)

    fb_entity_info_path = os.path.join(result_dir, '360/mapping/classify/mapped_fb_entity_info.json')
    fb_entity_info = load_json_map(fb_entity_info_path, total = 6282988)


	name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
			os.path.join(result_dir, 'freebase/entity_alias.json')]
	totals = [39345270, 2197095]
	name_map = load_name_attr(name_files, totals, set(fb_entities))
	# print "name_map", len(name_map)
	# description_map = load_name_attr([os.path.join(result_dir, 'freebase/entity_description.json')], totals = [6426977], fb_entities = set(fb_entities))
	





	