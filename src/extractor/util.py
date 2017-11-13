#encoding: utf-8
from ..IOUtil import result_dir, Print, doc_dir
from .entity.test import extract_stanford_result
import json
import os

def load_stanford_result(sentence_path, stanford_result_path):
    sentence_inf = file(sentence_path)
    stanford_inf = file(stanford_result_path)
    sentences = []
    results = []
    while True:
        
        sentence = sentence_inf.readline().strip()
        if sentence == "":
            break
        stanford_result_line = stanford_inf.readline().strip()
        if stanford_result_line == "":
            break
        sentences.append(sentence)
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

            


