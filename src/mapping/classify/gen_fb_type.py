from ...IOUtil import result_dir, nb_lines_of
import os
from tqdm import tqdm
from .gen_fb_property import load_mapping_pairs

if __name__ == "__main__":
    mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
    fb_entities = set(fb_entities)
    fb_type_path = os.path.join(result_dir, 'freebase/entity_type.json')
    hit_cnt = 0
    outf = file(os.path.join(result_dir, '360/mapping/classify/fb_entity_type.tsv'), 'w')
    for line in tqdm(file(fb_type_path), total = nb_lines_of(fb_type_path)):
        p = line.split('\t')
        fb_uri = p[0].decode('utf-8')
        if fb_uri in fb_entities:
        outf.write(line)
    outf.close()


