from ...IOUtil import result_dir, Print, classify_dir
import json
import os
from tqdm import tqdm
from .util import load_baike_entity_class, load_fb_type, load_baike_attr_names
from .type_infer import TypeInfer

def load_ground_truth(filepath):
    ground_truth = []
    es = set()
    for line in file(filepath):
        p = line.strip().split(' ')
        if len(p) != 2:
            continue
        if p[0] == 'error' or p[1] == 'error':
            continue
        ground_truth.append((p[0], p[1]))
        es.add(p[0])
        es.add(p[1])
    return ground_truth, es

def load_train_data(filepath, entities):
    Print('load data from [%s]' %filepath)
    pairs = []
    for line in file(filepath):
        p = line.split('\t')
        baike_url = p[0]
        fb_uris = json.loads(p[1])
        for fb_uri in fb_uris:
            if entities is None or baike_url in entities or fb_uri in entities:
                pairs.append((baike_url, fb_uri))
    return pairs

def make_key(baike_url, fb_uri):
    return baike_url + " # " + fb_uri

def unmake_key(key):
    return key.split(' # ')
    
def load_infobox_score(pairs = None): 
    filepath = os.path.join(result_dir, '360/mapping/classify/map_scores.json')
    total = 26578184
    if pairs is not None:
        load_keys = set([make_key(*pair)for pair in pairs])
    Print("load infobox score from [%s] with #pairs = %d" %(filepath, len(load_keys) if pairs else 0))
    score_map = {}
    for line in tqdm(file(filepath), total = total):
        match_res = json.loads(line)
        score = match_res['#match']
        baike_url = match_res['baike_url']
        fb_uri = match_res['fb_uri']
        key = make_key(baike_url, fb_uri)
        if (pairs is None or key in load_keys) and score > 0:
            score_map[key] = score
    return score_map

def load_summary_score(pairs = None):
    filepath = os.path.join(result_dir, '360/mapping/classify/summary_sim_score.tsv')
    total = 26578184
    if pairs is not None:
        load_keys = set([make_key(*pair)for pair in pairs])
    Print("load summary score from [%s] with #pairs = %d" %(filepath, len(load_keys) if pairs else 0))
    score_map = {}
    for line in tqdm(file(filepath), total = total):
        p = line.split('\t')
        assert len(p) == 5
        baike_url = p[0]
        fb_uri = p[1]
        key = make_key(baike_url, fb_uri)
        score = float(p[2])
        if (pairs is None or key in load_keys) and score > 0:
            score_map[key] = score
    return score_map

def calc_type_infer_score(pairs):
    baike_urls =  set()
    fb_uris = set()
    for bk, fb in pairs:
        baike_urls.add(bk)
        fb_uris.add(fb)
    
    baike_cls_map = load_baike_entity_class(filepath = os.path.join(classify_dir, 'baike_cls.tsv'), baike_urls = baike_urls, simple = True)
    baike_info_map = load_baike_attr_names(filepath = os.path.join(result_dir, '360/360_entity_info_processed.json'),
                                         total = 21710208, baike_urls = baike_urls)

    fb_type_map = load_fb_type(filepath = os.path.join(classify_dir, 'fb_entity_type.json'), fb_uris = fb_uris)

    infobox_path = os.path.join(result_dir, '360/mapping/one2one_predicates_map.json')
    baike_cls_path = os.path.join(classify_dir, 'baike_cls2fb_type.json')
    type_infer = TypeInfer(infobox_path = infobox_path, baike_cls_path = baike_cls_path)

    score_map = {}
    for baike_url, fb_uri in pairs:
        baike_cls = baike_cls_map.get(baike_url, [])
        baike_info = baike_info_map.get(baike_url, [])
        type_probs = type_infer.infer(baike_info, baike_cls)
        fb_types = fb_type_map[fb_uri]
        score = 0
        decided_inferred_types = []
        for inferred_type in type_probs:
            prob = type_probs[inferred_type]
            if prob > 0.8:
                decided_inferred_types.append(inferred_type)
        if len(decided_inferred_types) > 0:
            error_cnt = 0
            for x in decided_inferred_types:
                if not x in fb_types:
                    error_cnt += 1
            if error_cnt == len(decided_inferred_types) and error_cnt >= 2:
                score -= error_cnt
            if error_cnt == 2:
                score -= 0.3
            elif error_cnt == 3:
                score -= 1.5
            elif error_cnt >= 4:
                score -= 5
        max_prob = 0
        for fb_type in fb_types:
            if type_probs.get(fb_type, 0) > max_prob:
                max_prob = type_probs[fb_type]
        score += min(0.02 * max_prob, 0.2)
        score_map[make_key(baike_url, fb_uri)] = score
    return score_map
        
class SimpleClassifer:
    def __init__(self, infobox_cof, summary_cof, type_infer = False):
        self.infobox_cof = infobox_cof
        self.summary_cof = summary_cof
        self.type_infer = type_infer
    
    def load_score(self, pairs = None):
        if self.type_infer:
            self.type_infer_scores = calc_type_infer_score(pairs)
        self.infobox_scores = load_infobox_score(pairs)
        self.summary_scores = load_summary_score(pairs)
        

    def set_cof(self, infobox_cof, summary_cof):
        self.infobox_cof = infobox_cof
        self.summary_cof = summary_cof

    def calc_score(self, pairs):
        Print('calc score for %d pairs' %len(pairs))
        score_map = {}
        for pair in tqdm(pairs, total = len(pairs)):
            key = make_key(*pair)
            summary_score = self.summary_scores.get(key, 0)
            if summary_score > 0.5:
                summary_score *= 10
            score = self.infobox_cof * self.infobox_scores.get(key, 0) + self.summary_cof * summary_score
            if self.type_infer:
                score += self.type_infer_scores[key]
            score_map[key] = score
        return score_map

    def save(self, filepath):
        outf = file(filepath, 'w')
        obj = {
            'infobox_cof': self.infobox_cof,
            'summary_cof': self.summary_cof,
            'type_infer': self.type_infer
        }

        outf.write(json.dumps(obj) + '\n')
        outf.write(json.dumps(self.infobox_scores) + '\n')
        outf.write(json.dumps(self.summary_scores) + '\n')
        if self.type_infer:
            outf.write(json.dumps(self.type_infer_scores) + '\n')
        outf.close()

    @staticmethod
    def load_from_file(filepath):
        inf = file(filepath, 'r')
        lines = inf.readlines()
        inf.close()
        obj = json.loads(lines[0])
        infobox_cof, summary_cof, type_infer = obj['infobox_cof'], obj['summary_cof'], obj['type_infer']
        clf = SimpleClassifer(infobox_cof, summary_cof, type_infer)
        clf.infobox_scores = json.loads(lines[1])
        clf.summary_scores = json.loads(lines[2])
        if type_infer:
            clf.type_infer_scores = json.loads(lines[3])
        return clf

def find_map(pairs, score_map):
    Print('sorting')
    keys = sorted(score_map.keys(), key = lambda x:score_map[x], reverse = True)
    Print('sorting finished')
    mapped_urls = set()
    mapped_uris = set()
    mapped_pairs = []
    for key in keys:
        baike_url, fb_uri = unmake_key(key)
        score = score_map[key]
        # if score < 0.1:
        #     break
        
        if baike_url in mapped_urls or fb_uri in mapped_uris:
            continue
        mapped_urls.add(baike_url)
        mapped_uris.add(fb_uri)
        mapped_pairs.append((key, score))

    return mapped_pairs


def test(clf, pairs, true_pairs):
    score_map = clf.calc_score(pairs)
    maps = find_map(pairs, score_map)
    true_map = {}
    for bk, fb in true_pairs:
        true_map[bk] = fb
    for key, score in maps:
        baike_url, fb_uri = unmake_key(key)
        if baike_url in true_map:
            right = true_map[baike_url] == fb_uri
            print right, baike_url, fb_uri, true_map[baike_url], score
        # print unmake_key(key), score
    
def match(clf, pairs, out_path):
    score_map = clf.calc_score(pairs)
    maps = find_map(pairs, score_map)
    outf = file(out_path, 'w')
    for key, score in maps:
        baike_url, fb_uri = unmake_key(key)
        outf.write('%s\t%s\t%f\n' %(baike_url, fb_uri, score))
    outf.close()

if __name__ == "__main__":
    # base_dir = os.path.join(result_dir, '360/mapping/classify')
    # true_pairs, entities = load_ground_truth(os.path.join(base_dir, 'train_data/ground_truth.txt'))
    # train_pairs = load_train_data(os.path.join(base_dir, 'train_data/train_data.json'), entities = entities)

    # clf = SimpleClassifer(1, 1, True)
    # clf.load_score(train_pairs)
    # clf.save(os.path.join(base_dir, 'SimpleClf.json'))


    train_pairs = load_train_data(os.path.join(classify_dir, 'mappings.txt'), entities = None)
    clf = SimpleClassifer(1, 1, True)
    clf.load_score(train_pairs)
    
    match(clf, train_pairs, os.path.join(classify_dir, 'classify_result.tsv'))
    clf.save(os.path.join(base_dir, 'FullClf.json'))
    # score_map = clf.calc_score(train_pairs)
    # test(clf, train_pairs, true_pairs)



    




    
