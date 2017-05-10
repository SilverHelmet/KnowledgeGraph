import sys
import json
from ..IOUtil import base_dir, load_file, Print, result_dir
import os

def load_attrs():
    path = os.path.join(base_dir, 'docs/name_attr.txt')
    attrs = load_file(path)
    attrs = [attr.strip().split("\t")[-1].decode('utf-8') for attr in attrs]
    return attrs

if __name__ == "__main__":
    attrs = load_attrs()
    out_path = os.path.join(result_dir, '360/mapping/exact_mapping.tsv')
    in_path = os.path.join(result_dir, '360/360_mapping.json')

    # debug
    in_path = os.path.join(result_dir, 'test/mapping_result.json')
    out_path = os.path.join(result_dir, 'test/exact_mapping.tsv')

    outf = file(out_path, 'w')
    
    one_cnt = 0
    cnt_map = {}
    for x in attrs:
        cnt_map[x] = 0

    for cnt, line in enumerate(file(in_path), start = 1):
        if cnt % 100000 == 0:
            Print("cnt = %d one_cnt = %d" %(cnt, one_cnt))
        key, obj = line.split('\t')
        obj = json.loads(obj)
        fb_uris = []
        for name_attr in attrs:
            if name_attr in obj:
                fb_uris_list = [x.split("#")[0] for x in obj[name_attr]]
                fb_uris.extend(fb_uris_list)
        fb_uris = set(fb_uris)
        if len(fb_uris) == 1:
            map_name = None
            for name in attrs:
                if name in obj:
                    cnt_map[name] += 1
                    if map_name is None:
                        map_name = name
            one_cnt += 1
            key = key.decode('utf-8')
            x = key + '\t' + list(fb_uris)[0] + '\t' + map_name + '\n'
            outf.write(x.encode('utf-8'))

    outf.close()
    print "one cnt = %d" %one_cnt
    for key in sorted(cnt_map.keys(), key = lambda x: cnt_map[x], reverse = True):
        print type(key)
        print key
        print key, cnt_map[key]

    
    

        
    