from src.IOUtil import dict_dir
from src.extractor.resource import Resource
from src.extractor.util import get_domain
import os

def gen_province_location():
    resource = Resource.get_singleton()
    baike_info_map = resource.get_baike_info()
    ename_title_map = resource.get_baike_ename_title()
    out_path = os.path.join(dict_dir, 'province.txt')
    province_names = set()
    for bk_url in ename_title_map:
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
                is_province = True
        
        for ename in enames:
            ename = ename.decode('utf-8')
            if len(ename) >= 2 and (ename.endswith(u'省') or ename.endswith(u"州")) and 'fb:location.administrative_division' in bk_types:
                is_province = True

        if is_province:
            province_names.update(enames)

    outf = file(out_path, 'w')
    for name in province_names:
        outf.write("%s\n" %(name))
    outf.close()

if __name__ == "__main__":
    gen_province_location()
