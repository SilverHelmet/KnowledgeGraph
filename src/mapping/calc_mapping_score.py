from ..IOUtil import result_dir
import os
import json
from .one2one_mapping_cnt import load_attrs
from tqdm import tqdm
from .predicate_mapping import load_name_attr

def load_mapping_pairs(filepath, total = 4483846):
	mapping_attrs = load_attrs()

	baike_entities = []
	fb_entities = set()
	baike2fb = {}
	for line in tqdm(file(filepath), total = total):
		baike_url, map_info = line.split('\t')
		baike_url = baike_url.decode('utf-8')
		map_info = json.loads(map_info)
		fb_uris = []
		for attr in mapping_attrs:
			if attr in map_info:
				fb_list = [x.split("#")[0] for x in map_info[attr]]
				fb_uris.extend(fb_list)
		fb_uris = set(fb_uris)
		if len(fb_uris) > 0:
			baike2fb[baike_url] = list(fb_uris)
			baike_entities.append(baike_url)
			fb_entities.update(fb_uris)
	
	return baike2fb, baike_entities, list(fb_entities)







if __name__ == "__main__":
	mapping_file = os.path.join(result_dir, '360/360_mapping.json')
	mapping_pairs, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
	print len(mapping_pairs)
	name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
			os.path.join(result_dir, 'freebase/entity_alias.json')]
	totals = [39345270, 2197095]

	name_map = load_name_attr(name_files, totals, set(fb_entities))
	print len(name_map)
	# mediator_ttl_map = load_ttl2map(os.path.join(result_dir, 'freebase/mediator_med_property.ttl'), total = 50413655)

	# baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
	# baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208)