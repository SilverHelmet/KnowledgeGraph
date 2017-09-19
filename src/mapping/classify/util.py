import os
from ...IOUtil import result_dir, Print
from tqdm import tqdm
import json

def load_mappings(with_score = False):
    mapping_path = os.path.join(result_dir, '360/mapping/classify/mappings.txt')
    Print('load mappings from [%s]' %mapping_path)
    total = 1129601
    baike2fb = {}
    for line in tqdm(file(mapping_path), total = total):
        p = line.split('\t')
        baike_url = p[0]
        fb_uris = json.loads(p[1])
        if with
        baike2fb[baike_url] = fb_uris
    return baike2fb

def load_



if __name__ == "__main__":
    print len(load_mappings())