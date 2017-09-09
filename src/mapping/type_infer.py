#encoding:utf-8
import os
from ..IOUtil import result_dir, Print
from .one2one_mapping_cnt import load_attrs as load_name_attr
from ..fb_process.extract_util import get_type
import json

class Mapping:
    def __init__(self, pair):
        self.fb_prop, prob = pair
        hit, total = prob.split('/')
        self.hit = int(hit)
        self.total = int(total)
    
    def __str__(self):
        return ' '.join([self.fb_prop, '%d/%d' %(self.hit, self.total)])

class TypeInfe:
    def __init__(self, path = os.path.join(result_dir, '360/mapping/predicates_map.json')):
        self.baikeattr2fb_type = self.init(path)

    def init(self, mapping_path):
        Print('load mapping result from [%s]' %mapping_path)
        name_attrs = set(load_name_attr())

        baikeattr2fb_type = {}
        for line in file(mapping_path):
            p = line.decode('utf-8').split('\t')
            baikeattr = p[0]
            mapping_pairs = json.loads(p[1])[:10]
            mappings = []
            for index, pair_str in enumerate(mapping_pairs, start = 1):
                mapping = Mapping(pair_str)

                if (index <=4 or mapping.hit >= 50) and mapping.hit >= 3:
                    mappings.append(mapping)
            baikeattr2fb_type[baikeattr] = mappings

        return baikeattr2fb_type

    def infer_type(self, baike_attrs):
        prob_map = {}
        for attr in baike_attrs:




                

if __name__ == "__main__":

