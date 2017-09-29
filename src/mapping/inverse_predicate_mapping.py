from ..IOUtil import base_dir,result_dir
import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Mapping:
    def __init__(self, concept):
        self.concept = concept
        self.maps = []
        self.name = None
        self.count = 0

    def add(self, name, count, total):
        self.maps.append((name, count, total))
        self.count += count

    def check_filter(self, threshold = 0.05, min_count = 3, k  = 5):
        maps = []
        for name, count, total in self.maps:
            if count / (total + 0.0) < threshold or count < min_count:
                continue
            else:
                maps.append((name, count, total))
        maps = sorted(maps, key = lambda x: x[1], reverse = True)
        good_names = set(map(lambda x: x[0], maps[:k]))
        good_names.update(map(lambda x: x[0],sorted(maps, key = lambda x: x[1] / (x[2] + 0.0), reverse = True)[:k]))
        self.maps = []
        for name, count, total in maps:
            if name in good_names:
                self.maps.append((name, count, total))

            
        
        self.count = 0
        for _, count, total in self.maps:
            self.count += count


    def infer(self):
        max_count = 0
        for name, count, total in self.maps:
            if count > max_count:
                self.name = name
                max_count = count
    
    def __str__(self):
        map_out = "\t".join(["%s %d/%d" %(name, count, total) for name , count, total in self.maps])
        # out = "%s\t%s\t%s" %(self.concept, self.name, map_out)
        out = "%s\t%s" %(self.concept, map_out)
        # map_out = "\t".join(["%s" %(name) for name , count, total in self.maps])
        # out = "%s\t%s\t%s" %(self.concept, self.name, map_out)
        return out

            

if __name__ == "__main__":
    inpath = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
    outpath = os.path.join(result_dir, '360/mapping/final_predicates_map.txt')

    mappings = {}
    for line in file(inpath):
        p = line.split("\t")
        name = p[0]
        obj = json.loads(p[1])
        for concept, prob in obj:
            count, total = map(int, prob.split('/'))
            if not concept in mappings:
                mappings[concept] = Mapping(concept)
            mappings[concept].add(name, count, total)

    outf = file(outpath, 'w')
    for mapping in mappings.itervalues():
        mapping.check_filter()
        mapping.infer()

    for mapping in sorted(mappings.values(), key = lambda x: x.count, reverse = True):
        if mapping.count > 0:
            outf.write(str(mapping) + '\n')
    outf.close()
        




