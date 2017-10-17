#encoding: utf-8
from ..IOUtil import result_dir, Print, doc_dir
from .entity.test import extract_stanford_result
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
            if line.startswith("#"):
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

def load_stanford_result(sentence_path, stanford_result_path):
    sentence_inf = file(sentence_path)
    stanford_inf = file(stanford_result_path)
    sentences = []
    results = []
    while True:
        
        sentence = sentence_inf.readline().strip()
        if sentence == "":
            break
        sentence = sentence.strip()
        sentences.append(sentence)

        stanford_result_line = stanford_inf.readline()
        results.append(json.loads(stanford_result_line))
    sentence_inf.close()
    stanford_inf.close()

    result_map = {}
    results = extract_stanford_result(results, sentences)
    for idx in range(len(sentences)):
        s = sentences[idx]
        result = results[idx]
        result_map[s] = result
    return result_map

def load_important_domains():
    domains = set()
    for line in file(os.path.join(doc_dir, 'important_domains.txt')):
        line = line.strip()
        if line.startswith("#"):
            continue
        domains.add(line)
    return domains

def get_domain(fb_type):
    return fb_type.split('.')[0]

def get_url_domains(types, valid_domains):
    domains = set()
    for fb_type in types:
        domain = get_domain(fb_type)
        if domain in valid_domains:
            domains.add(domain)
    return list(domains)


if __name__ == "__main__":
    predicate_map = load_predicate_map(extra_path = os.path.join(doc_dir, 'human_add_predicate_map.json'))

    probs =  predicate_map[u'制片人']
    print probs

            


