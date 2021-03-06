import json
from ..IOUtil import result_dir, write_dict_cnt, Print
import os
import sys

class Mapping:
    def __init__(self, baike_uri, fb_uri):
        self.baike_uri = baike_uri
        self.fb_uri = fb_uri

    def __hash__(self):
        return hash(self.baike_uri) + hash(self.fb_uri)

    def __cmp__(self, other):
        c = cmp(self.baike_uri, other.baike_uri)
        if c != 0:
            return c
        return cmp(self.fb_uri, other.fb_uri)

    def __str__(self):
        return (self.baike_uri + " " + self.fb_uri).encode('utf-8')

        

def count(mapping_path):
    Print("counting %s" %mapping_path)
    mapping_cnt = {}
    mapping_set = {}
    for cnt, line in enumerate(file(mapping_path), start = 1):
        if cnt % 100000 == 0:
            Print("count %d" %cnt)
        p = line.split('\t')
        key = p[0]
        mappings = json.loads(p[1])
        cnted_maps = set()
        for baike_uri in mappings:
            values = mappings[baike_uri]
            for tag in values:
                mapped_fb_uri, fb_uri = tag.split("#")
                mapping = Mapping(baike_uri, fb_uri)
                if not mapping in mapping_cnt:
                    mapping_cnt[mapping] = 0
                    mapping_set[mapping] = set()
                mapping_set[mapping].add(mapped_fb_uri)
                if mapping in cnted_maps:
                    continue
                cnted_maps.add(mapping)
                
                mapping_cnt[mapping] += 1
    return mapping_cnt, mapping_set


if __name__ == "__main__":
    inpath = os.path.join(result_dir, '360/360_mapping.json')
    outpath = os.path.join(result_dir, '360/360_mapping_cnt.txt')

    # inpath = os.path.join(result_dir, 'test/mapping_result.json')
    # outpath = os.path.join(result_dir, 'test/mapping_cnt.txt')

    
    mapping_cnt, mapping_set = count(inpath)
    Print("write")
    outf = file(outpath, 'w')
    for key in sorted(mapping_cnt.keys(), key = lambda x: mapping_cnt[x], reverse = True):
        outf.write("%s\t%s\t%s\n" %(key, mapping_cnt[key], len(mapping_set[key])))
    outf.close()

    inpath = os.path.join(result_dir, '360/360_mapping_lowercase.json')
    outpath = os.path.join(result_dir, '360/360_mapping_lower_cnt.txt')

    mapping_cnt, mapping_set = count(inpath)
    Print("write")
    outf = file(outpath, 'w')
    for key in sorted(mapping_cnt.keys(), key = lambda x: mapping_cnt[x], reverse = True):
        outf.write("%s\t%s\t%s\n" %(key, mapping_cnt[key], len(mapping_set[key])))
    outf.close()

        
        
    # write_dict_cnt(mapping_cnt, outpath)



    
