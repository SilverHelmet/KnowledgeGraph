from ...IOUtil import result_dir, Print
import json
from tqdm import tqdm
import os
import numpy as np

def count_occur(mapping_path):
    Print("count occur from [%s]" %mapping_path)
    baike_cnt = {}
    fb_cnt = {}
    for line in tqdm(file(mapping_path), total = 1129601):
        p = line.split('\t')
        baike_url = p[0]
        obj = [w.encode('utf-8') for w in json.loads(p[1])]
        baike_cnt[baike_url] = len(obj)
        for fb_uri in obj:
            if not fb_uri in fb_cnt:
                fb_cnt[fb_uri] =0
            fb_cnt[fb_uri] +=1
    return baike_cnt, fb_cnt

def random_sample(cnt_map, rest, test_fn):
    pool = []
    for key in cnt_map:
        if test_fn(cnt_map[key]):
            pool.append(key)
    sample_indices = np.random.permutation(len(pool))[:rest]
    samples = set()
    for idx in sample_indices:
        samples.add(pool[idx])
    return samples



def generate_sample(baike_urls, fb_uris, out_path, mapping_path):
    Print('generate sample')
    fb_lines = {}
    for fb in fb_uris:
        fb_lines[fb] = []

    outf = file(out_path, 'w')

    for line in tqdm(file(mapping_path), total = 1129601):
        p = line.split('\t')
        baike_url = p[0]
        if baike_url in baike_urls:
            outf.write(line)
        else:
            obj = [w.encode('utf-8') for w in json.loads(p[1])]
            add_cnt = 0
            for fb in obj:
                if fb in fb_lines:
                    add_cnt += 1
                    fb_lines[fb].append(line)
            assert add_cnt < 2

    for fb in sorted(fb_lines.keys()):
        outf.write("".join(fb_lines[fb]))
    outf.close()

if __name__ == "__main__":
    baike_urls = set(['baike.so.com/doc/10066508-10591843.html', 
    'baike.so.com/doc/1287918-1361771.html',
    'baike.so.com/doc/5807317-6020118.html',
    'baike.so.com/doc/6773200-6988367.html',
    'baike.so.com/doc/5363940-5599529.html'])
    fb_uris = set(['fb:m.02hrt7', 'fb:m.022fj_'])


    small_rest = 40 #  2 - 5
    big_rest = 40 # 6 - 20
    fb2baike_big_rest = 20 # >= 3

    base_dir = os.path.join(result_dir, '360/mapping/classify')
    mapping_path = os.path.join(base_dir, 'mappings.txt')
    baike_cnt, fb_cnt = count_occur(mapping_path)

    baike_small = random_sample(baike_cnt, small_rest, lambda x: x >=2 and x <= 5)
    baike_big = random_sample(baike_cnt, big_rest, lambda x: x >= 6 and x <= 20)
    fb_big = random_sample(fb_cnt, fb2baike_big_rest, lambda x: x >= 3)

    baike_urls.update(baike_small)
    baike_urls.update(baike_big)
    
    fb_uris.update(fb_big)
    print len(baike_urls)
    print len(fb_uris)

    cnt = 0
    cnt += len(baike_urls)
    for fb in fb_cnt:
        cnt += fb_cnt[fb]
    
    print "cnt is %d" %cnt

    out_path = os.path.join(base_dir, 'train_data/train_data.json')
    generate_sample(baike_urls, fb_uris, out_path, mapping_path)
    




    
