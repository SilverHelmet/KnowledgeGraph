from src.extractor.resource import Resource
import os
from src.IOUtil import Print, rel_ext_dir, result_dir, nb_lines_of
from tqdm import tqdm
import json

def load_baike_ename_title():
    path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    Print('load baike\'s ename and title from [%s]' %path)
    ename_title_map = {}
    for line in tqdm(file(path), total = nb_lines_of(path)):
        bk_url, obj = line.split('\t')
        obj = json.loads(obj)
        ename, title = obj['ename'].encode('utf-8'), obj['title'].encode('utf-8')
        if title != ename:
            ename_title_map[bk_url] = [ename, title]
        else:
            ename_title_map[bk_url] = [ename]
    return ename_title_map


if __name__ == "__main__":
    ename_title_map = load_baike_ename_title()
    out_path = os.path.join(rel_ext_dir, 'baike_ename_title.tsv')
    Print("write to [%s]" %out_path)
    outf = file(out_path, 'w')
    for bk_url in tqdm(sorted(ename_title_map.keys()), total = len(ename_title_map)):
        outf.write('%s\t%s\n' %(bk_url, "\t".join(ename_title_map[bk_url])))
    outf.close()
    

    