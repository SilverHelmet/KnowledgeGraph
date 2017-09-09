import os
from ..IOUtil import result_dir, Print
from .one2one_mapping_cnt import load_attrs as load_name_attr

class Mapping:
    def __init__()
class TypeInfe:
    def __init__(self, path = os.path.join(result_dir, '360/mapping/predicates_map.json')):
        baikeattr2fb_type = init(path)

    def init(self, mapping_path):
        Print('load mapping result from [%s]' %mapping_path)
        name_attrs = set(load_name_attr())
        for line in file(mapping_path):
            p = line.split('\t')
            mapping_pairs = json.loads(p[1])[:4]
            



    
if __name__ == "__main__":
