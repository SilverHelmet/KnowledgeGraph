import os
from ..IOUtil import result_dir, Print
from .one2one_mapping_cnt import load_attrs as load_name_attr

class Mapping:
    def __init__(self, pair):
        self.fb_prop, prob = pair
        hit, total = prob.split('/')
        self.hit = int(hit)
        self.total = int(total)
    



class TypeInfe:
    def __init__(self, path = os.path.join(result_dir, '360/mapping/predicates_map.json')):
        self.baikeattr2fb_type = init(path)

    def init(self, mapping_path):
        Print('load mapping result from [%s]' %mapping_path)
        name_attrs = set(load_name_attr())

        baikeattr2fb_type = {}
        for line in file(mapping_path):
            p = line.deocde('utf-8').split('\t')
            baikeattr = p[0]
            mapping_pairs = json.loads(p[1])[:4]
            mappings = []
            for pair_str in mapping_pairs:
                mapping = Mapping(pair_str)
                mappings.append(mapping)
            baikeattr2fb_type[baikeattr] = mappings
        return baikeattr2fb_type
        

                

if __name__ == "__main__":
    
