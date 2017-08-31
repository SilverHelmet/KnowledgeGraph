from ...IOUtil import load_json_map, result_dir
from .gen_fb_property import load_mapping_pairs
import os

if __name__ == "__main__":
    fb_entity_info_path = os.path.join(result_dir, '360/mapping/classify/mapped_fb_entity_info.json')
    fb_entity_info = load_json_map(fb_entity_info_path, total = 6282988)

    mapping_file = os.path.join(result_dir, '360/360_mapping.json')

    baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
    fb_entities = set(fb_entities)
    for key in fb_entities:
        if not key in fb_entity_info:
            print key
            break