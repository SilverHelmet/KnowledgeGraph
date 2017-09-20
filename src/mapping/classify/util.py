import os
from ...IOUtil import result_dir, Print, data_dir, nb_lines_of
from tqdm import tqdm
import json

def load_mappings():
    mapping_path = os.path.join(result_dir, '360/mapping/classify/mappings.txt')
    Print('load mappings from [%s]' %mapping_path)
    total = 1129601
    baike2fb = {}
    for line in tqdm(file(mapping_path), total = total):
        p = line.split('\t')
        baike_url = p[0]
        fb_uris = json.loads(p[1])
        baike2fb[baike_url] = fb_uris
    return baike2fb

def load_baike_entity_class(filepath = None, baike_urls = None):
    if filepath is None:
        filepath = os.path.join(data_dir, 'entityHypernym_v16_all_ex_darts.txt')
    bk2cls = {}
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        name, popular, url, cls, small_cl = line.strip().split('\t')
        if cls == "NO_TYPE":
            continue
        assert url.startswith('http://')
        url = url[7:]
        if baike_urls is None or url in baike_urls:
            bk2cls[url] = cls.split(" ")
    return bk2cls


if __name__ == "__main__":
    pass