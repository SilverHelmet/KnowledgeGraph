#encoding: utf-8
from src.IOUtil import rel_ext_dir, result_dir, nb_lines_of, Print
from src.util import is_chinese
import os
from tqdm import tqdm
import json

def count_predicate(inpath, outpath, predicate):
    cnt_map = {}
    for line in tqdm(file(inpath), total = nb_lines_of(inpath)):
        _, obj = line.split('\t')
        info = json.loads(obj)['info']
        values = info.get(predicate, [])
        for value in values:
            if not value in cnt_map:
                cnt_map[value] = 1
            else:
                cnt_map[value] += 1
    outf = file(outpath, 'w')
    for key in sorted(cnt_map.keys(), key = lambda x: cnt_map[x], reverse = True):
        if is_chinese(key):
            outf.write("%s\t%s\n" %(key, cnt_map[key]))
    outf.close()
            

if __name__ == "__main__":
    base_dir = os.path.join(rel_ext_dir, 'infobox_count')
    predicates = [u'职业', u'国籍']
    infobox_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    for predicate in predicates:
        Print("process predicate %s" %predicate)
        outpath = os.path.join(base_dir, '%s_cnt.tsv' %(predicate))
        count_predicate(infobox_path, outpath, predicate)
