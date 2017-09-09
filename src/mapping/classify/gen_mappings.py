from .gen_fb_property import load_mapping_pairs
from ...IOUtil import  result_dir
import json

mapping_file = os.path.join(result_dir, '360/360_mapping.json')
baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)

outf = file(os.path.join(result_dir, '360/mapping/classify/mappings.txt'), 'w')
for baike_url in baike2fb_map:
    fb_uris = baike2fb_map[baike_url]
    outf.write("%s\t%s\n" %(baike_url, json.dumps(fb_uris)))
outf.close()



