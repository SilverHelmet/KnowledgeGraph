from .util import load_baike_entity_class, load_mappings_witd_score, load_baike_entity_class, load_fb_type
from ...IOUtil import classify_dir, Print
import os
import json

class BaikeClassCount:
    def __init__(self, baike_class):
        self.baike_cls = baike_class
        self.fb_type_cnt = {}
        self.count = 0
    
    def add(self, fb_types):
        if "fb:book.written_work" in fb_types:
            assert "fb:book.book" in fb_types
        self.count += 1
        for fb_type in fb_types:
            if not fb_type in self.fb_type_cnt:
                self.fb_type_cnt[fb_type] = 0
            self.fb_type_cnt[fb_type] += 1
    
    def to_obj(self, topk = 5):
        top_types = sorted(self.fb_type_cnt.keys(), key = lambda x: self.fb_type_cnt[x], reverse = True)[:topk]
        fb_type_cnt = {}
        for fb_type in top_types:
            fb_type_cnt[fb_type] = self.fb_type_cnt[fb_type]
        obj = {
            'count': self.count,
            'fb_type_cnt': fb_type_cnt,
            'baike_cls': self.baike_cls
        }
        return obj

    def calc_prob(self):
        self.fb_type_prob = {}
        for fb_type in self.fb_type_cnt:
            self.fb_type_prob[fb_type] = (self.fb_type_cnt[fb_type] + 0.0) / self.count

    @staticmethod
    def load_from_obj(obj):
        cls = BaikeClassCount(obj['baike_cls'])
        cls.count = obj['count']
        cls.fb_type_cnt = obj['fb_type_cnt']
        return cls



def gen_baike_cls_to_fb(mappings, baike_cls_map, fb_type_map):
    baike_class_cnts = {}
    for bk_url, fb_uri in mappings:
        if not bk_url in baike_cls_map:
            continue
        bk_clses = baike_cls_map[bk_url]
        for bk_cls in bk_clses:
            if not bk_cls in baike_class_cnts:
                baike_class_cnts[bk_cls] = BaikeClassCount(bk_cls)
            count = baike_class_cnts[bk_cls]
            count.add(fb_type_map[fb_uri])
    return baike_class_cnts

if __name__ == "__main__":

    good_mapping_path = os.path.join(classify_dir, 'good_one2one_mappings.txt')
    good_mappings = load_mappings_witd_score(good_mapping_path)

    bk_urls = set()
    fb_uris = set()
    for bk, fb in good_mappings:
        bk_urls.add(bk)
        fb_uris.add(fb)


    baike_cls_path = os.path.join(classify_dir, 'baike_cls.tsv')
    bk_cls = load_baike_entity_class(filepath = baike_cls_path, baike_urls = bk_urls, simple = True)

    fb_type = load_fb_type(fb_uris = fb_uris)

    baike_class_cnts = gen_baike_cls_to_fb(good_mappings, bk_cls, fb_type)

    out_path = os.path.join(classify_dir, 'baike_cls2fb_type.json')
    outf = file(out_path, 'w')
    for key in sorted(baike_class_cnts.keys()):
        outf.write("%s\n" %(json.dumps(baike_class_cnts[key].to_obj(topk = 5))))
    outf.close()

    






    