from ..IOUtil import result_dir
import json
import os

def load_predicate_map(filepath = None):
    if filepath is None:
        filepath = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
    predicate_map  = {}
    for line in file(filepath):
        p = line.split('\t')
        infobox_pred = p[0].decode('utf-8')
        mappings = json.loads(p[1])[:7]
        probs = {}
        for prop, occur in mappings:
            cnt, total = map(int, occur.split('/'))
            prob = (cnt + 0.0) / (total + 5)
            probs[prop] = prob
        predicate_map[infobox_pred] = probs
    return predicate_map


            


