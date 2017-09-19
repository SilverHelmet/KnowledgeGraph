from .calc_infobox_mapping_score import extend_name
from ..predicate_mapping import load_name_attr
from tqdm import tqdm
from ...IOUtil import Print, result_dir, load_json_map
import json
import os

def process_fb_value(fb_str):
    if fb_str.startswith('"') and fb_str.endswith('"'):
        fb_str = fb_str[1:-1]
    elif fb_str[0] == '"' and fb_str[-4:] in['"@en', '"@zh']:
        fb_str = fb_str[1:-4]
    return fb_str

def add_property_name_all(in_path, total, name_map, out_path):
    Print("add fb property name, read from [%s] write to [%s]" %(in_path, out_path))
    outf = file(out_path, 'w')
    for line in tqdm(file(in_path), total = total):
        p = line.split('\t')
        fb_e = p[0].decode('utf-8')
        fb_info = json.loads(p[1])
        str_names = set()
        for name, value in fb_info:
            if value in name_map:
                str_names.update(name_map[value])
            else:
                str_names.add(process_fb_value(value))

        outf.write("%s\t%s\n" %(fb_e, json.dumps(list(str_names), ensure_ascii = False)))
    outf.close()



if __name__ == "__main__":
    out_dir = os.path.join(result_dir, '360/mapping/classify')
    in_path = os.path.join(out_dir, 'mapped_fb_entity_info.json')
    out_path = os.path.join(out_dir, 'mapped_fb_entity_info_processed.json')

    
    
    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
        os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]
    name_map = load_name_attr(name_files, totals)

    
    # fb_entity_info = load_json_map(in_path)
    add_property_name_all(in_path, 6282988, name_map, out_path)