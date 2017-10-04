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
import sys
from ..fb_process.extract_util import get_domain
from ..rel_extraction.util import load_bk_types

def has_punc_eng(name):
    for _, flag in pseg.cut(name):
        if flag == 'x':
            return True
        if flag == "eng":
            return True
    return False

valid_domains = set(['fb:film', 'fb:tv', 'fb:soccer', 'fb:sports', 'fb:astronomy', 'fb:music', 'fb:book'])
def is_vertical_domain(types):
    global valid_domains
    for fb_type in types:
        print get_domain(fb_type)
        if get_domain(fb_type) in valid_domains:
            print 'return true'
            return True
        else:
            return False


        


 

if __name__ == "__main__":
    # pop_map = load_bk_entity_pop()
    name2bk = load_name2baike(os.path.join(rel_ext_dir, 'baike_names.tsv.sample'))

    
    keys = sorted(name2bk)
    out_path = os.path.join(rel_ext_dir, 'baike_dict.txt')
    
    year_pattern = re.compile(ur'(公元前|公元)?\d{1,4}年$')
    re_digit = re.compile(r'^[0-9+\-=!?]+$')
    re_eng = re.compile(r"^[a-zA-Z]+$")

    valid_func = None
    if len(sys.argv) >= 2 and sys.argv[1] == "vertical":
        valid_func = is_vertical_domain
        out_path = os.path.join(rel_ext_dir, 'baike_dict_vertical_domain.txt')
        Print('use valid_func: valic_domains')
        bk_type_map = load_bk_types(os.path.join(rel_ext_dir, 'baike_static_info.tsv.sample'))
        
        
    outf = file(out_path, 'w')
    Print('write dict to %s' %out_path)
    for name in tqdm(keys, total = len(keys)):
        name = name.strip()
        if name == "":
            continue
        if name.find(" ") != -1:
            continue
        if year_pattern.match(name):
            # print 'time name', name
            continue
        if re_digit.match(name):
            # print "digit name", name
            continue
        if re_eng.match(name):
            continue
        if has_punc_eng(name):
            continue
        bks = name2bk[name]

        
        print name
        # pop = 0
        valid = False
        for bk_url in bks:
            # pop = max(pop, pop_map.get(bk_url, 0))
            # print bk_url, bk_type_map[bk_url], valid_func(bk_type_map[bk_url])
            if valid_func is None or valid_func(bk_type_map[bk_url]):
                valid = True

        if BaikeDatetime.parse(name, strict = True) is not None:
            continue
        print valid
        if valid:
            outf.write('%s\n' %(name))
            # outf.write('%s %d baike\n' %(name, pop * 2 + 1))
    outf.close()


    
