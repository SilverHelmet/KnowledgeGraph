#encoding: utf-8
from ...IOUtil import result_dir, Print
from ...loader import load_stopwords
import os
from tqdm import tqdm
from .calc_infobox_mapping_score import load_mapping_pairs

def load_summary(path, stopwords, total):
    Print('load summary from [%s]' %(path))
    summary_map = {}
    for line in tqdm(file(path), total = total):
        p = line.rstrip('\n').split('\t')
        key = p[0]
        words = p[1].decode('utf-8').split(" ")
        words_set = set()
        for word in words:
            if not word in stopwords:
                words_set.add(word)
        summary_map[key] = words_set
    return summary_map



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
    for baike_url in baike2fb_map:
        for fb_uri in baike2fb_map[baike_url]:
            baike_words = baike_summary_map.get(baike_url, set())
            nb_baike_words = len(baike_words)

            fb_words = fb_summary_map.get(fb_uri, set())
            nb_fb_words = len(fb_words)
            
            out = [baike_url, fb_uri]
            nb_match = len(fb_words.intersection(baike_words))
            out = [baike_url, fb_uri, nb_match, nb_baike_words, nb_fb_words]
            out = map(str, out)
            outf.write("%s\n" %"\t".join(out))
    outf.close()




