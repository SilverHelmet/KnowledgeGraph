#encoding: utf-8
import os
import jieba
import jieba.posseg as pseg
from src.IOUtil import rel_ext_dir, Print, dict_dir
from tqdm import tqdm
import re
from src.mapping.fb_date import BaikeDatetime
from src.baike_process.parse import html_unescape
import sys
from src.extractor.resource import Resource

def has_punc_eng(name):
    for word, flag in pseg.cut(name):
        if word == '·':
            continue
        if flag == 'x':
            return True
        if flag == "eng":
            return True
    return False

year_pattern = re.compile(ur'(公元前|公元)?\d{1,4}年$')
re_digit = re.compile(r'^[0-9+\-=!?]+$')
re_eng = re.compile(r"^[a-zA-Z]+$")
def is_valid_dict_name(name):
    global year_pattern, re_digit, re_eng
    if name == "":
        return False
    # if name.find(" ") != -1:
    #     return False
    if year_pattern.match(name):
        return False
    if re_digit.match(name):
        # print "digit name", name
        return False
    # if re_eng.match(name):
    #     return False
    # if has_punc_eng(name):
    #     return False
    if BaikeDatetime.parse(name, strict = True) is not None:
        return False
    return True

def get_domain(fb_type):
    return fb_type.split('.')[0]

valid_domains = set(['fb:film', 'fb:tv', 'fb:soccer', 'fb:sports', 'fb:astronomy', 'fb:music', 'fb:book', 'fb:award'])
def is_vertical_domain(types):
    global valid_domains
    for fb_type in types:
        if get_domain(fb_type) in valid_domains:
            return True
    return False



if __name__ == "__main__":
    name2bk = Resource.get_singleton().get_name2bk()
    
    keys = sorted(name2bk)
    
    
    year_pattern = re.compile(ur'(公元前|公元)?\d{1,4}年$')
    re_digit = re.compile(r'^[0-9+\-=!?]+$')
    re_eng = re.compile(r"^[a-zA-Z]+$")

    
    valid_func = is_vertical_domain
    out_path = os.path.join(dict_dir, 'vertical_domain_baike_dict.txt')
    Print('use valid_func: valic_domains')
        
        
    outf = file(out_path, 'w')
    Print('write dict to %s' %out_path)
    for name in tqdm(keys, total = len(keys)):
        name = name.strip()
        
        if not is_valid_dict_name(name):
            continue
        # if has_punc_eng(name):
        #     continue
        bks = name2bk[name]

        # pop = 0
        valid = False
        for bk_url in bks:
            if valid_func(bk_type_map[bk_url]):
                valid = True

        if BaikeDatetime.parse(name, strict = True) is not None:
            continue
        if valid:
            outf.write('%s\n' %(name))
            # outf.write('%s %d baike\n' %(name, pop * 2 + 1))
    outf.close()


    
