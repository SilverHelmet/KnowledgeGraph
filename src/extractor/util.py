#encoding: utf-8
from ..IOUtil import result_dir, Print, doc_dir
import json
import os

def load_predicate_map(filepath = None, extra_path = None):
    if filepath is None:
        filepath = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
    Print('load predicate map from %s' %filepath)
    predicate_map  = {}
    for line in file(filepath):
        p = line.split('\t')
        infobox_pred = p[0]
        mappings = json.loads(p[1])[:7]
        probs = {}
        for prop, occur in mappings:
            cnt, total = map(int, occur.split('/'))
            prob = (cnt + 0.0) / (total + 3)
            probs[prop] = prob
        predicate_map[infobox_pred] = probs

    if extra_path is not None:
        Print("load extra rule from [%s]" %extra_path)
        for line in file(extra_path):
            line = line.strip()
            if line == "":
                continue
            p = line.split('\t')
            infobox_pred = p[0]
            fb_props = json.loads(p[1])
            probs = predicate_map[infobox_pred]
            for prop in fb_props:
                if not prop in probs:
                    probs[prop] = 0
                probs[prop] += 1.0
    return predicate_map

if __name__ == "__main__":
    predicate_map = load_predicate_map(extra_path = os.path.join(doc_dir, 'human_add_predicate_map.json'))

    probs =  predicate_map[u'制片人']
    print probs

            


