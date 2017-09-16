from ...IOUtil import result_dir, Print
import json
import os
from tqdm import tqdm

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
    pairs = []
    for line in file(filepath):
        p = line.split('\t')
        baike_url = p[0]
        fb_uris = json.loads(p[1])
        for fb_uri in fb_uris:
            if baike_url in entities or fb_uri in entities:
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


class SimpleClassifer:
    def __init__(self, infobox_cof, summary_cof, type_infer = False):
        self.infobox_cof = infobox_cof
        self.summary_cof = summary_cof
        self.type_infer = type_infer
    
    def load_score(self, pairs = None):
        self.infobox_scores = load_infobox_score(pairs)
        self.summary_scores = load_summary_score(pairs)

    def set_cof(self, infobox_cof, summary_cof):
        self.infobox_cof = infobox_cof
        self.summary_cof = summary_cof

    def calc_score(self, pairs):
        score_map = {}
        for pair in pairs:
            key = make_key(*pair)
            score = self.infobox_cof * self.infobox_scores.get(key, 0) + self.summary_cof * self.summary_scores.get(key, 0)
            score_map[key] = score
        return score_map

    def save(self, filepath):
        outf = file(filepath, 'w')
        obj = {
            'infobox_cof': self.infobox_cof,
            'summary_cof': self.summary_cof,
        }

        outf.write(json.dumps(obj) + '\n')
        outf.write(json.dumps(self.infobox_scores) + '\n')
        outf.write(json.dumps(self.summary_scores) + '\n')
        outf.close()

    @staticmethod
    def load_from_file(filepath):
        inf = file(filepath, 'r')
        lines = inf.readlines()
        inf.close()
        obj = json.loads(lines[0])
        infobox_cof, summary_cof = obj['infobox_cof'], obj['summary_cof']
        clf = SimpleClassifer(infobox_cof, summary_cof)
        clf.infobox_scores = json.loads(lines[1])
        clf.summary_scores = json.loads(lines[2])
        return clf

def find_map(pairs, score_map):
    keys = sorted(score_map.keys(), key = lambda x:score_map[x], reverse = True)
    mapped_urls = set()
    mapped_uris = set()
    mapped_pairs = []
    for key in keys:
        baike_url, fb_uri = unmake_key(key)
        score = score_map[key]
        if baike_url in mapped_urls or fb_uri in mapped_urls:
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
    

    
if __name__ == "__main__":
    base_dir = os.path.join(result_dir, '360/mapping/classify')
    true_pairs, entities = load_ground_truth(os.path.join(base_dir, 'train_data/ground_truth.txt'))
    train_pairs = load_train_data(os.path.join(base_dir, 'train_data/train_data.json'), entities = entities)

    # clf = SimpleClassifer(1, 1)
    # clf.load_score(train_pairs)
    # clf.save(os.path.join(base_dir, 'SimpleClf.json'))

    clf = SimpleClassifer.load_from_file(os.path.join(base_dir, 'SimpleClf.json'))

    score_map = clf.calc_score(train_pairs)
    test(clf, train_pairs, true_pairs)



    




    
