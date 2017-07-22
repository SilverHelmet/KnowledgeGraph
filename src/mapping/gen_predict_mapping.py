from ..IOUtil import base_dir,result_dir
import os
import json

class Mapping:
    def __init__(self, concept):
        self.concept = concept
        self.maps = []
        self.name = None

    def add(self, name, count, total):
        self.maps.append((name, count, total))

    def filter(self, threshold = 0.1, min_count = 5, k  = 7):
        maps = []
        for name, count, total in self.maps:
            if count / (total + 0.0) < threshold or count < min_count:
                continue
            else:
                maps.append((name, count, total))
        self.maps = sorted(maps, key = lambda x: x[1] / (x[2] + 0.0), reverse = True)[:k]


    def infer(self):
        max_count = 0
        for name, count, total in self.maps:
            if count > max_count:
                self.name = name
    
    def __str__(self):
        map_out = "\t".join(["%s %d/%d" %(name, count, total) for name , count, total in self.maps])
        out = "%s\t%s\t%s" %(self.concept, self.name, map_out)
        return out

            

if __name__ == "__main__":
    inpath = os.path.join(result_dir, '360/mapping/predicates_map.json')
    outpath = os.path.join(result_dir, '360/mapping/predicates_map.txt')
    x = [['123', '1/123']]
    print json.dumps(x)
    print json.loads(json.dumps(x))
    # for line in file(inpath):
    #     p = line.split("\t")
    #     name = p[0]
    #     print p[1]
    #     obj = json.loads(p[1])

