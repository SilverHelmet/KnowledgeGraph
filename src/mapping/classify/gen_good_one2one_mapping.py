from ...IOUtil import result_dir, Print
from .util import load_mappings
from .simple_classify import SimpleClassifer, make_key
import os

def count_entity(baike2fb):
    bk_cnt = {}
    fb_cnt = {}
    for bk_url in baike2fb:
        for fb_uri in baike2fb[bk_url]:
            if not bk_url in bk_cnt:
                bk_cnt[bk_url] = 0
            if not fb_uri in fb_cnt:
                fb_cnt[fb_uri] = 0
            bk_cnt[bk_url] += 1
            fb_cnt[fb_uri] += 1
    return bk_cnt, fb_cnt


if __name__ == "__main__":
    baike2fb = load_mappings()
    bk_cnt, fb_cnt = count_entity(baike2fb)
    
    one2one_mapping_pairs = []
    for bk_url in bk_cnt:
        if bk_cnt[bk_url] != 1:
            continue
        fb_uri = baike2fb[bk_url][0]
        if fb_cnt[fb_uri] != 1:
            continue
        one2one_mapping_pairs.append((bk_url, fb_uri))
    Print("#one2one mapping pairs = %d" %len(one2one_mapping_pairs))

    clf = SimpleClassifer(1, 1)
    clf.load_score(one2one_mapping_pairs)
    score_map = clf.calc_score(one2one_mapping_pairs)

    good_mapping_pairs = []
    for bk_url, fb_uri in one2one_mapping_pairs:
        key = make_key(bk_url, fb_uri)
        score = score_map[key]
        # if score > 0.1:
        good_mapping_pairs.append((bk_url, fb_uri, score))

    Print("#good mapping pairs = %d" %len(good_mapping_pairs))

    out_path = os.path.join(result_dir, '360/mapping/classify/good_one2one_mappings.tsv')
    outf = file(out_path, 'w')
    for bk_url, fb_uri, score in good_mapping_pairs:
        outf.write("%s\t%s\t%f\n" %(bk_url, fb_uri, score))
    outf.close()








    
