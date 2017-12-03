from src.IOUtil import Print
import sys
import os 
import json

class PredicateMaps:
    def __init__(self):
        self.map = {}
        self.total_cnt = {}

    def add(self, predicate, props):
        if not predicate in self.map:
            self.map[predicate] = {}
            self.total_cnt[predicate] = 0
        pred_map = self.map[predicate]
        for prop in props:
            self.total_cnt[predicate] += 1
            if not prop in pred_map:
                pred_map[prop] = 0
            pred_map[prop] += 1

    def top_k(self, pred_map, topk, total):
        keys = sorted(pred_map.keys(), key = lambda x:pred_map[x], reverse = True)
        keys = keys[:topk]
        ret = [[key, '%d/%d' %(pred_map[key], total)]for key in keys]
        return ret

if __name__ == '__main__':
    inpath = sys.argv[1]
    outpath = sys.argv[2]

    Print('collect from [%s] write to [%s]' %(inpath, outpath))
    pred_maps = PredicateMaps()
    for line in file(inpath):
        if not line.startswith('\t'):
            continue
        l = line.strip()
        p = l.split('\t')
        predicate = p[0]
        predicate = predicate.strip("'\" :")
        if len(predicate) == 0:
            continue
        if len(predicate.decode('utf-8')) < 2 and predicate != '是':
            continue
        props = p[1:]
        pred_maps.add(predicate, props)

    predicates = pred_maps.map.keys()
    predicates.sort(key = lambda x: pred_maps.total_cnt[x], reverse = True)
    outf = file(outpath, 'w')
    for pred in predicates: 
        ret = pred_maps.top_k(pred_maps.map[pred], 20, pred_maps.total_cnt[pred])
        outf.write('%s\t%s\n' %(pred, json.dumps(ret)))
    outf.close()





