import json
import os

from tqdm import tqdm

from ...IOUtil import result_dir, write_json_map, Print
from ...schema.schema import Schema
from ..one2one_mapping_cnt import load_attrs
from ..predicate_mapping import load_baike_info, load_name_attr, load_ttl2map, extend_fb_ttls


def load_mapping_pairs(filepath, total = 4483846):
    Print("load mapping from file [%s]" %filepath)
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


def load_ext_write_entity_info(fb_property_path, mediator_ttl_map, out_path, total = None, entities = None):
    max_ext_cnt = 0
    Print("read property from [%s], write to [%s]" %(fb_property_path, out_path))
    schema = Schema()
    schema.init()
    # entity_info = {}
    outf = file(out_path, 'w')
    for line in tqdm(file(fb_property_path), total = total):
        p = line.split('\t')
        fb_uri = p[0]
        if entities is not None and fb_uri not in entities:
            continue
        ttls = json.loads(p[1])
        ttls, ext_cnt = extend_fb_ttls(ttls, fb_uri, mediator_ttl_map, schema)
        max_ext_cnt = max(max_ext_cnt, ext_cnt)
        outf.write("%s\t%s\n" %(fb_uri, json.dumps(ttls, ensure_ascii = True)))
        # entity_info[fb_uri] = ttls
    outf.close()
    Print("max extend cnt = %d" %max_ext_cnt)
    # return entity_info
    






if __name__ == "__main__":
    mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    out_dir = os.path.join(result_dir, '360/mapping/classify')
    baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
    print "baike2fb_map", len(baike2fb_map)
    print "baike_entities", len(baike_entities)
    print "fb_entities", len(fb_entities)

    # total = 71350023
    total = None
    mediator_ttl_map = load_ttl2map(os.path.join(result_dir, 'freebase/mediator_med_property.ttl'), total = total, entities = None)
    print "mediator_ttl_mapl", len(mediator_ttl_map)

    fb_property_path = os.path.join(result_dir, 'freebase/entity_property.json')
    out_path = os.path.join(out_dir, 'mapped_fb_entity_info.json')
    load_ext_write_entity_info(fb_property_path, mediator_ttl_map, out_path = out_path, total = 53574900, entities = set(fb_entities))
    
    # write_json_map(out_path, fb_entity_info, sort = True)





    # baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    # baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208, entities = baike_entities)
    # print "baike_entitiy_info", len(baike_entity_info)
