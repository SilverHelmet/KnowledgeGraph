#encoding:utf-8
import jieba
import os
from ...IOUtil import result_dir
import json
from tqdm import tqdm

if __name__ == "__main__":
    base_dir = os.path.join(result_dir, '360/mapping/classify')
    baike_summary_path = os.path.join(base_dir, 'baike_summary.json')
    inf = file(baike_summary_path, 'r')
    outf = file(os.path.join(base_dir, 'baike_summary.tokens'), 'w')
    total = 1129345
    for line in tqdm(inf, total = total):
        p = line.split('\t')
        baike_url = p[0]
        summary = json.loads(p[1])['summary']
        words = jieba.cut(summary)
        words = [word for word in words if word.strip() != ""]
        token_str = " ".join(words)
        outf.write("%s\t%s\n" %(baike_url, token_str))
    outf.close()



 

