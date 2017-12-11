#encoding: utf-8
from src.extractor.resource import Resource
import re
from tqdm import tqdm
from src.IOUtil import extra_type_dir
import os

re_order = re.compile(ur'^第[一二三四五六七八九十零百千0-9]+[届次]')
re_year = re.compile(ur'^\d{1,4}年')
def extract_name(name):
    global re_order
    global re_year
    if type(name) is str:
        name = name.decode('utf-8')
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

def gen_name_map(extractor):
    baike_ename_title = Resource.get_singleton().get_baike_ename_title()
    name_map = {}
    for bk_url in tqdm(baike_ename_title, total = len(baike_ename_title)):
        enames = baike_ename_title[bk_url]
        for ename in enames:
            parent_name = extractor.try_extract_parent_name(ename) # return unicode or None
            if parent_name:
                add_to_dict_list(name_map, parent_name, ename.decode('utf-8'))

    return name_map


if __name__ == '__main__':
    award_extor = NameExtractor(extract_name)
    name_map = gen_name_map(award_extor)
    outf = file(os.path.join(extra_type_dir, 'son_name_map.tsv'), 'w')
    for name in sorted(name_map.keys()):
        son_names = set(name_map[name])
        if len(son_names) < 3:
            continue
        outf.write("%s\t%s\n" %(name, "\t".join(sorted(son_names))))
    outf.close()



