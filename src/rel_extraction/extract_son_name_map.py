#encoding: utf-8
from src.extractor.resource import Resource
import re
from tqdm import tqdm
from src.IOUtil import extra_type_dir, Print
from src.mapping.fb_date import BaikeDatetime
import os


re_order = re.compile(ur'^第[一二三四五六七八九十零百千0-9]+[届]')
re_year = re.compile(ur'^\d{1,4}年')
art_work_types = set(['fb:film.film', 'fb:book.book', 'fb:book.written_work', 'fb:cvg.computer_videogame', 'fb:tv.tv_program'])

def is_art_work(types):
    global art_work_types
    for fb_type in types:
        if fb_type in art_work_types:
            return True
    return False

def extract_name(name):
    global re_order
    global re_year
    if type(name) is str:
        name = name.decode('utf-8')
    if BaikeDatetime.parse(name, strict = True) is not None:
        return None
    res = re_order.match(name)
    if res:
        return name[len(res.group()):]
    res = re_year.match(name)
    if res:
        return name[len(res.group()):]
    return None

class NameExtractor:
    def __init__(self, parent_ext_func):
        self.parent_ext_func = parent_ext_func

    def try_extract_parent_name(self, ename):
        return self.parent_ext_func(ename)

def add_to_dict_list(d, key, value):
    if not key in d:
        d[key] = []
    d[key].append(value)

def del_loc_prefix(name, location_dict):
    ed = len(name)
    while ed > 0:
        if name[:ed] in location_dict:
            return name[ed:]
        ed -= 1

    return None
    

def gen_name_map(extractor):
    baike_ename_title = Resource.get_singleton().get_baike_ename_title()
    url2names = Resource.get_singleton().get_url2names()
    bk_static_info = Resource.get_singleton().get_baike_info()
    location_dict = Resource.get_singleton().get_location_dict()
    
    location_dict = set([x.decode('utf-8') for x in location_dict])
    all_names = set()

    for bk_url in url2names:
        if not bk_url in bk_static_info:
            continue
        bk_types = bk_static_info[bk_url].types
        if is_art_work(bk_types):
            continue
        enames = url2names[bk_url]
        for ename in enames:
            all_names.add(ename)

    name_map = {}
    Print("extract parent name")
    for bk_url in tqdm(baike_ename_title, total = len(baike_ename_title)):
        if not bk_url in bk_static_info:
            continue
        bk_types = bk_static_info[bk_url].types
        if is_art_work(bk_types):
            continue

        enames = baike_ename_title[bk_url]
        for ename in enames:
            parent_name = extractor.try_extract_parent_name(ename) # return unicode or None
            if not parent_name:
                continue
            if parent_name.encode('utf-8') in all_names:
                add_to_dict_list(name_map, parent_name, ename.decode('utf-8'))
            second_parent_name = del_loc_prefix(parent_name, location_dict)
            if second_parent_name and second_parent_name.encode('utf-8') in all_names:
                add_to_dict_list(name_map, second_parent_name, ename.decode('utf-8'))

    return name_map


if __name__ == '__main__':
    award_extor = NameExtractor(extract_name)
    name_map = gen_name_map(award_extor)

    outf = file(os.path.join(extra_type_dir, 'son_name_map.tsv'), 'w')
    out_names = set()
    for name in sorted(name_map.keys(), key = lambda x: len(x), reverse = True):
        son_names = name_map[name]
        son_names = [x for x in son_names if not x in out_names]
        son_names = set(son_names)
        if len(son_names) < 3:
            continue
        for x in son_names:
            out_names.add(x)
        outf.write("%s\t%s\n" %(name, "\t".join(sorted(son_names))))
    outf.close()



