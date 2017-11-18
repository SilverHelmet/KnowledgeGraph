#encoding: utf-8
from ..IOUtil import rel_ext_dir, Print, result_dir
from tqdm import tqdm
import os 
from src.extractor.resource import Resource

def gen_title_rel_dict(fb_type, count_filepath, out_path, cnt_threshold):
    Print('gen dict by type %s' %fb_type)
    candidate_urls = set()
    resource = Resource.get_singleton()
    baike_static_info_map = resource.get_baike_info()
    Print("gen candidate profession entity")
    for bk_url in tqdm(baike_static_info_map, total = len(baike_static_info_map)):
        types = baike_static_info_map[bk_url].types
        if fb_type in types:
            candidate_urls.add(bk_url)

    candidate_names = set()
    for line in file(count_filepath):
        p = line.strip().split('\t')
        if len(p) == 2:
            name, cnt = p
            cnt = int(cnt)
            if cnt >= cnt_threshold:
                candidate_names.add(name)
    Print('#candidate urls = %d, #candidate names = %d' %(len(candidate_urls), len(candidate_names)))
    ename_title_map = resource.get_baike_ename_title()

    title_names = set()
    for candidate_url in candidate_urls:
        enames = ename_title_map[candidate_url]
        for ename in enames:
            if ename in candidate_names:
                if ename in title_names:
                    print "duplicate title name:", ename
                assert ename not in title_names
                title_names.add(ename)
    
    outf = file(out_path, 'w')
    for title_name in sorted(title_names):
        outf.write(title_name + '\n')
    outf.close()
        


    

   
        
    
       
if __name__ == "__main__":
    count_dir = os.path.join(rel_ext_dir, "infobox_count")
    base_dir = os.path.join(rel_ext_dir, 'dict')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    gen_title_rel_dict("fb.location.country", os.path.join(count_dir, '国籍_cnt.tsv'), os.path.join(base_dir, 'nationality.txt'), 10)
    gen_title_rel_dict("fb:people.profession", os.path.join(count_dir, '职业_cnt.tsv'), os.path.join(base_dir, 'profession.txt'), 10)


