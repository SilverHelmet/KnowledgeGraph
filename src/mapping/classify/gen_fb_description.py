from .gen_fb_property import load_mapping_pairs
from ...IOUtil import result_dir
from tqdm import tqdm
import os
import json

if __name__ == "__main__":
    mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    out_dir = os.path.join(result_dir, '360/mapping/classify')
    baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
    fb_entities = set(fb_entities)

    des_path = os.path.join(result_dir, 'freebase/entity_description.json')
    outf = file(os.path.join(out_dir, 'fb_description.token'), 'w')
    hit_cnt = 0
    for line in tqdm(file(des_path), total = 6426977):
        p = line.split('\t')
        fb_uri = p[0].decode('utf-8')
        if not fb_uri in fb_entities:
            continue
        hit_cnt += 1
        des_list = json.loads(p[1])
        for des in des_list:
            if des[-4:] == u'"@zh':
                des = des[1:-4]
                words = jieba.cut(des)
                words = [word for word in words if word.strip() != ""]
                token_str = " ".join(words)
                outf.write("%s\t%s\n" %(fb_uri, token_str))
                continue
            else:
                print des[:-4]
    outf.close()
    print "hit cnt = %d" %(hit_cnt)


