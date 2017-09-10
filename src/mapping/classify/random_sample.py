from ...IOUtil import result_dir, Print
import json
from tqdm import tqdm
import os

def count_occur(mapping_path):
    Print("count occur from [%s]" %mapping_path)
    baike_cnt = {}
    fb_cnt = {}
    for line in tqdm(file(mapping_path), total = 1129601)[:100]:
        p = line.split('\t')
        baike_url = p[0]
        obj = [w.encode('utf-8') for w in json.loads(p[1])]
        baike_cnt[baike_url] = len(obj)
        for fb_uri in obj:
            if not fb_uri in fb_cnt:
                fb_cnt[fb_uri] =0
            fb_cnt[fb_uri] +=1
    return baike_cnt, fb_cnt



if __name__ == "__main__":
    baike_urls = set(['baike.so.com/doc/10066508-10591843.html', 
    'baike.so.com/doc/1287918-1361771.html',
    'baike.so.com/doc/5807317-6020118.html',
    'baike.so.com/doc/6773200-6988367.html'])
    fb_uris = set(['fb:m.02hrt7', 'fb:m.022fj_', 'fb:m.022fj'])


    small_rest = 40
    big_rest = 40
    fb2baike_big_rest = 20

    base_dir = os.path.join(result_dir, '360/mapping/classify')
    mapping_path = os.path.join(base_dir, 'mappings.txt')
    baike_cnt, fb_cnt = count_occur(mapping_path)

    for key in fb_cnt.keys()[:10]:
        print "test", key

    for bk in baike_urls:
        print bk, baike_cnt[bk]


    print ""
    print ""


    for fb in fb_uris:
        print fb, fb_cnt[fb]
