#encoding: utf-8
import os
from .util import load_bk_entity_pop, load_name2baike
from ..IOUtil import rel_ext_dir, Print
from tqdm import tqdm
import re
from ..mapping.fb_date import BaikeDatetime

if __name__ == "__main__":
    pop_map = load_bk_entity_pop()
    name2bk = load_name2baike()
    keys = sorted(name2bk)
    out_path = os.path.join(rel_ext_dir, 'baike_dict.txt')
    outf = file(out_path, 'w')
    Print('write dict to %s' %out_path)
    year_pattern = re.compile(ur'(公元前|公元)?\d{1,4}年$')

    for name in tqdm(keys, total = len(keys)):
        if year_pattern.match(name):
            print 'time name', name
            continue
        if BaikeDatetime.parse(name) is not None:
            print 'time name', name
            continue
        bks = name2bk[name]
        pop = 0
        for bk_url in bks:
            pop = max(pop, pop_map.get(bk_url, 0))
        outf.write('%s %d baike' %(name, pop))
    outf.close()


    
