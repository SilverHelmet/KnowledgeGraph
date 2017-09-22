#encoding:utf-8
import os
from ..IOUtil import result_dir, Print
from .one2one_mapping_cnt import load_attrs as load_name_attr
from ..fb_process.extract_util import get_type
import json
from .classify.gen_baike_class_to_fb import BaikeClassCount

class Mapping:
    def __init__(self, pair):
        self.fb_prop, prob = pair
        hit, total = prob.split('/')
        self.hit = int(hit)
        self.total = int(total)

    def prob(self):
        return (self.hit + 0.0) / (self.total + 6)

    def fb_type(self):
        return get_type(self.fb_prop)
    
    def __str__(self):
        return ' '.join([self.fb_prop, '%d/%d' %(self.hit, self.total)])

class InfoboxTypeInfer:
    def __init__(self, path):
        self.baikeattr2fb_type = self.init(path)

    def init(self, mapping_path):
        Print('load mapping result from [%s]' %mapping_path)

        baikeattr2fb_type = {}
        for line in file(mapping_path):
            p = line.decode('utf-8').split('\t')
            baikeattr = p[0]
            mapping_pairs = json.loads(p[1])[:5]
            mappings = []
            for index, pair_str in enumerate(mapping_pairs, start = 1):
                mapping = Mapping(pair_str)

                if (index <= 2 or mapping.hit >= 50) and mapping.hit >= 3:
                    mappings.append(mapping)
            baikeattr2fb_type[baikeattr] = mappings

        return baikeattr2fb_type

    def infer(self, baike_attrs):
        prob_map = {}
        for attr in baike_attrs:
            if not attr in self.baikeattr2fb_type:
                continue
            mappings = self.baikeattr2fb_type[attr]
            for mapping in mappings:
                fb_type = mapping.fb_type()
                prob = mapping.prob()
                if not fb_type in prob_map:
                    prob_map[fb_type] = prob
                else:
                    prob_map[fb_type] += prob
        return prob_map      

class BKClassTypeInfer:
    def __init__(self, path):
        self.baike_cls_cnt_map = self.init(path)

    def init(self, path):
        Print("init Baike Url type infer from [%s]" %path)
        baike_cls_cnt_map = {}
        for line in file(path):
            obj = json.loads(line)
            baike_cls_cnt = BaikeClassCount.load_from_obj(obj)
            baike_cls_cnt.calc_prob()
            baike_cls = baike_cls_cnt.baike_cls
            baike_cls_cnt_map[baike_cls] = baike_cls_cnt
        return baike_cls_cnt_map

    def infer(self, baike_clses):
        prob = {}
        for cls in baike_clses:
            cls_cnt = self.baike_cls_cnt_map[cls]
            for fb_type in cls_cnt:
                if not fb_type in prob:
                    fb_type[prob] + 




if __name__ == "__main__":
    type_infer = InfoboxTypeInfer(path = os.path.join(result_dir, '360/mapping/predicates_map.json'))
    attr = [u'民族', u'影视作品', u'音乐作品']
    res = type_infer.infer(attr)
    print res