from ..IOUtil import result_dir
import os
import json
import sys

class Prob:
    def __init__(self, key):
        self.key = key
        self.total = 0
        self.cnt_map = {}

    def add(self, value):
        self.total += 1
        if not value in self.cnt_map:
            self.cnt_map[value] = 0
        self.cnt_map[value] += 1

    def top_k(self, k):
        top_keys = sorted(self.cnt_map.keys(), key = lambda x: self.cnt_map[x], reverse = True)
        ret = [[key, '%d/%d' %(self.cnt_map[key], self.total)]for key in top_keys]
        return ret


class MappingResult:
    def __init__(self):
        self.baike2fb = {}

    def add(self, baike_info, fb_property):
        assert type(baike_info) == unicode
        baike_info = baike_info.strip().strip(u':')
        baike_info = baike_info.strip(u'：').strip()
        if not baike_info in self.baike2fb:
            self.baike2fb[baike_info] = Prob(baike_info)
        self.baike2fb[baike_info].add(fb_property)

    def sorted_keys(self):
        return sorted(self.baike2fb.keys(), key = lambda x: self.baike2fb[x].total, reverse = True)



if __name__ == "__main__":
    if len(sys.argv) >= 3:
        predict_map_result_path = sys.argv[1]
    else:
        predict_map_result_path = os.path.join(result_dir, '360/mapping/one2one_info_predicate_mapping.tsv')
    map_result = MappingResult()
    for line in file(predict_map_result_path):
        fb_uri, baike_url, fb_property, baike_info, fb_value, baike_value, score = line.strip().decode('utf-8').split("\t")
        map_result.add(baike_info, fb_property)

    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
    else:
        out_path = os.path.join(result_dir, '360/mapping/one2one_predicates_map.json')
    outf = file(out_path, 'w')
    for key in map_result.sorted_keys():
        outf.write("%s\t%s\n" %(key, json.dumps(map_result.baike2fb[key].top_k(20)) ) )
    outf.close()


    

