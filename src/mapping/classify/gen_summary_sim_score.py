from ...IOUtil import result_dir, Print
from ...loader import load_stopwords
import os
from tqdm import tqdm

def load_summary(path, stopwords, total):
    Print('load summary from [%s]' %(path))
    summary_map = {}
    for line in tqdm(file(path), total = total):
        p = line.strip().split('\t')
        key = p[0]
        words = p[1].split(' ')
        words_set = set()
        for word in words:
            if not word in stopwords:
                words_set.add(word)
            else:
                print "stopwords", word
        summary_map[key] = words_set
    return summary_map



if __name__ == "__main__":
    base_dir = os.path.join(result_dir, '360/mapping/classify')
    baike_summary_path = os.path.join(base_dir, 'baike_summary.token')
    fb_summary_path = os.path.join(base_dir, 'fb_description.token')
    stopwords = load_stopwords()

    baike_summary_map = load_summary(baike_summary_path, stopwords, total = 1129345)
    fb_summary_map = load_summary(fb_summary_path, stopwords, total = 181418)

