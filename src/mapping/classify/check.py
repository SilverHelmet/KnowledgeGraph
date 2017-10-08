from ...IOUtil import load_json_map, result_dir
from .gen_fb_property import load_mapping_pairs
from ..one2one_mapping_cnt import load_baike_name_attrs
import os

if __name__ == "__main__":
    mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    out_dir = os.path.join(result_dir, '360/mapping/classify')
    baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
    print "baike2fb_map", len(baike2fb_map)
    print "baike_entities", len(baike_entities)
    print "fb_entities", len(fb_entities)

    baike_name_attrs = load_baike_name_attrs()

    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208, entities = set(baike_entities))

    baike_url = 'baike.so.com/doc/2180018-2307096.html'
    baike_info = baike_entity_info['baike.so.com/doc/2180018-2307096.html']
    print baike_info
    