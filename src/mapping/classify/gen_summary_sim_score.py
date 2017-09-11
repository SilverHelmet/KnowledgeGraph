#encoding: utf-8
from ...IOUtil import result_dir, Print
from ...loader import load_stopwords
import os
from tqdm import tqdm
from .calc_infobox_mapping_score import load_mapping_pairs
import numpy as np

def load_summary(path, stopwords, total):
    Print('load summary from [%s]' %(path))
    summary_map = {}
    for line in tqdm(file(path), total = total):
        p = line.rstrip('\n').split('\t')
        key = p[0]
        words = p[1].decode('utf-8').split(" ")
        words_list = []
        for word in words:
            if not word in stopwords:
                words_list.append(word)
        summary_map[key] = words_list
    return summary_map

def gen_word_cnt(words):
    word_cnt = {}
    for word in words:
        if not word in word_cnt:
            word_cnt[word] = 0
        word_cnt[word] += 1
    length = 0
    for cnt in word_cnt.itervalues():
        length += cnt * cnt
    length = np.sqrt(length)
    if length > 0:
        for word in word_cnt:
            word_cnt[word] /= length
    return word_cnt



if __name__ == "__main__":
    base_dir = os.path.join(result_dir, '360/mapping/classify')
    baike_summary_path = os.path.join(base_dir, 'baike_summary.token')
    fb_summary_path = os.path.join(base_dir, 'fb_description.token')
    stopwords = load_stopwords()

    baike_summary_map = load_summary(baike_summary_path, stopwords, total = 1129345)
    fb_summary_map = load_summary(fb_summary_path, stopwords, total = 181418)

    mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)

    outf = file(os.path.join(base_dir, 'summary_sim_score.tsv'), 'w')
    Print("calc summary sim score")
    for baike_url in tqdm(baike2fb_map, total = len(baike2fb_map)):
        baike_words = baike_summary_map.get(baike_url, [])
        nb_baike_words = len(baike_words)
        baike_words = gen_word_cnt(baike_words)
        for fb_uri in baike2fb_map[baike_url]:
        
            fb_words = fb_summary_map.get(fb_uri, [])
            nb_fb_words = len(fb_words)
            fb_words = gen_word_cnt(fb_words)
            
            match_cos_score = 0
            for word in baike_words:
                if word in fb_words:
                    match_cos_score += baike_words[word] * fb_words[word]                
            
            out = [baike_url, fb_uri, '%.5f' %match_cos_score, nb_baike_words, nb_fb_words]
            out = map(str, out)
            outf.write("%s\n" %"\t".join(out))
    outf.close()




