#encoding: utf-8
import os
import jieba
import jieba.posseg as pseg
from .util import load_bk_entity_pop, load_name2baike
from ..IOUtil import rel_ext_dir, Print
from tqdm import tqdm
import re
from ..mapping.fb_date import BaikeDatetime
from ..baike_process.parse import html_unescape

def has_punc_eng(name):
    for _, flag in pseg.cut(name):
        if flag == 'x':
            return True
        if flag == "eng":
            return True
    return False


if __name__ == "__main__":
    pop_map = load_bk_entity_pop()
    name2bk = load_name2baike()
    
    keys = sorted(name2bk)
    out_path = os.path.join(rel_ext_dir, 'baike_dict.txt')
    outf = file(out_path, 'w')
    Print('write dict to %s' %out_path)
    year_pattern = re.compile(ur'(公元前|公元)?\d{1,4}年$')
    re_digit = re.compile(r'^[0-9+\-=!?]+$')
    re_eng = re.compile(r"^[a-zA-Z]+$")
    for name in tqdm(keys, total = len(keys)):
        name = name.strip()
        if name == "":
            continue
        if name.find(" ") != -1:
            continue
        if year_pattern.match(name):
            print 'time name', name
            continue
        if re_digit.match(name):
            print "digit name", name
        if BaikeDatetime.parse(name, strict = True) is not None:
            print 'time name', name
            continue
        if re_eng.match(name):
            continue
        if has_punc_eng(name):
            continue
        
        bks = name2bk[name]
        pop = 0
        for bk_url in bks:
            pop = max(pop, pop_map.get(bk_url, 0))
        outf.write('%s %d baike\n' %(name, pop * 2 + 1))
    outf.close()


    
