#encoding: utf-8
from src.IOUtil import dict_dir, Print
from src.extractor.resource import Resource
from src.extractor.util import get_domain
from tqdm import tqdm
import os
from src.util import is_chinese
from extra_profession_dict import get_error_domains


def gen_province_dict():
    Print('generate province dict')
    resource = Resource.get_singleton()
    baike_info_map = resource.get_baike_info()
    ename_title_map = resource.get_baike_ename_title()
    out_path = os.path.join(dict_dir, 'province.txt')
    province_names = set()
    error_domains =  get_error_domains()
    for bk_url in tqdm(ename_title_map, total = len(ename_title_map)):
        enames = ename_title_map[bk_url]
        if not bk_url in baike_info_map:
            continue
        bk_info = baike_info_map[bk_url]
        bk_types = bk_info.types
        if not "fb:location.location" in bk_types:
            continue

        is_province = False
        for bk_type in bk_types:
            if get_domain(bk_type) == 'fb:location' and ('state' in bk_type or "province" in bk_type):
                print "province bk_type: %s" %bk_url
                is_province = True
        
        for ename in enames:
            ename = ename.decode('utf-8')
            if len(ename) > 2 and (ename.endswith(u'省') or ename.endswith(u"州")):
                print "province ename: %s %s" %(ename, bk_url)
                is_province = True

        if is_province:
            for bk_type in bk_types:
                if get_domain(bk_type) in error_domains:
                    is_province = False
                    print "province error type: %s" %(bk_url)

        if is_province:
            province_names.update(enames)

    outf = file(out_path, 'w')
    for name in province_names:
        if not is_chinese(name):
            continue
        outf.write("%s\n" %(name))
    outf.close()

def gen_citytown_dict():
    Print('generate citytown dict')
    resource = Resource.get_singleton()
    baike_info_map = resource.get_baike_info()
    ename_title_map = resource.get_baike_ename_title()

    citydown_names = set()
    
    for bk_url in tqdm(baike_info_map, total = len(baike_info_map)):
        if not bk_url in baike_info_map or not bk_url in ename_title_map:
            continue
        bk_types = baike_info_map[bk_url].types
        if not 'fb:location.location' in bk_types:
            continue
        if not "fb:location.citytown" in bk_types:
            continue

        if 'fb:people.person' in bk_types:
            continue

        enames = ename_title_map[bk_url]
        # is_error_name = False
        # error_suffix = ['乡', "镇", '村', '街道', '道路']
        # for ename in enames:
        #     for suffix in error_suffix:
        #         if ename.endswith(error_suffix):
        #             is_error_name = True
        # if is_error_name:
        #     continue
        
        citydown_names.update(enames)

    out_path = os.path.join(dict_dir, 'citytown.txt')
    outf = file(out_path, 'w')
    for name in citydown_names:
        if not is_chinese(name):
            continue
        outf.write("%s\n" %name)
    outf.close()
    
if __name__ == "__main__":
    gen_province_dict()
    gen_citytown_dict()
