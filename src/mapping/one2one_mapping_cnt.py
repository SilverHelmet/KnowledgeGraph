# DEPRECATED
import sys
import json
from ..IOUtil import base_dir, load_file, Print, result_dir
import os

def load_attrs():
    path = os.path.join(base_dir, 'docs/one2one_name_attr.txt')
    attrs = load_file(path)
    attrs = [attr.strip().split("\t")[-1].decode('utf-8') for attr in attrs]
    attrs = [x for x in attrs if not x.startswith('#')]
    return attrs

def attr_level(attr):
    '''
     0: none
     1: infobox
     2: multi_infobox
     3: ename, title
     4: multi_ename(title)
    '''
    
    if attr in ['ename', 'title']:
        return 3
    else:
        return 1

def count_lv_map(maps):
    uri_lv_map = {}
    for _, fb_uri, attr in maps:
        if not fb_uri in uri_lv_map:
            uri_lv_map[fb_uri] = 0
        level = attr_level(attr)
        last_level = uri_lv_map[fb_uri]
        if last_level == level and level in [1, 3]:
            uri_lv_map[fb_uri] = level + 1
        else:
            uri_lv_map[fb_uri] = max(level, last_level)


    return uri_lv_map


if __name__ == "__main__":
    attrs = load_attrs()
    out_path = os.path.join(result_dir, '360/mapping/exact_mapping.tsv')
    in_path = os.path.join(result_dir, '360/360_mapping.json')

    # debug
    # in_path = os.path.join(result_dir, 'test/mapping_result.json')
    # out_path = os.path.join(result_dir, 'test/exact_mapping.tsv')
    
    one_cnt = 0
    cnt_map = {}
    for x in attrs:
        cnt_map[x] = 0
    maps = []
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
                    if map_name is None:
                        map_name = name
            # cnt_map[map_name] += 1
            one_cnt += 1

            fb_uri = list(fb_uris)[0]
            maps.append((key.decode('utf-8'), fb_uri, map_name))

            # key = key.decode('utf-8')
            # x = key + '\t' + list(fb_uris)[0] + '\t' + map_name + '\n'

    print "one cnt = %d" %one_cnt
    fb_uris = [uri for _, uri, _ in maps]
    fb_uri_cnt = {}
    for uri in fb_uris:
        if not uri in fb_uri_cnt:
            fb_uri_cnt[uri] = 0
        fb_uri_cnt[uri] += 1

    exact_one_cnt = 0
    for baike_key, fb_uri, _ in maps:
        if fb_uri_cnt[fb_uri] == 1:
            exact_one_cnt += 1
    print 'exact one cnt = %d' %exact_one_cnt
        

    uri_lv_map = count_lv_map(maps)


    outf = file(out_path, 'w')
    one_cnt = 0
    for baike_key, fb_uri, map_name in maps:

        level = uri_lv_map[fb_uri]
        if attr_level(map_name) == level:
            cnt_map[map_name] += 1
            one_cnt += 1
            x = baike_key + "\t" + fb_uri + '\t' + map_name + '\n'
            outf.write(x.encode('utf-8'))
    outf.close()

    print "one cnt = %d" %one_cnt

    for key in sorted(cnt_map.keys(), key = lambda x: cnt_map[x], reverse = True):
        print key.encode('utf-8'), cnt_map[key]

    
    

        
    