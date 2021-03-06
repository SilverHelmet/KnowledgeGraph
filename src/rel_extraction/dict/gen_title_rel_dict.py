#encoding: utf-8
from src.IOUtil import rel_ext_dir, Print, result_dir, doc_dir
from tqdm import tqdm
import os 
from src.util import is_chinese
from src.extractor.resource import Resource

def gen_title_rel_dict(fb_type, count_filepath, out_path, cnt_threshold, extra_name_filepath = None, error_func = None, url_path = None):
    Print('gen dict by type [%s]' %fb_type)
    candidate_urls = set()
    resource = Resource.get_singleton()
    baike_static_info_map = resource.get_baike_info()
    Print("gen candidate baike_url")
    for bk_url in tqdm(baike_static_info_map, total = len(baike_static_info_map)):
        types = baike_static_info_map[bk_url].types
        if fb_type in types:
            candidate_urls.add(bk_url)

    candidate_names = set()
    if count_filepath is not None:
        for line in file(count_filepath):
            p = line.strip().split('\t')
            if len(p) == 2:
                name, cnt = p
                cnt = int(cnt)
                if cnt >= cnt_threshold:
                    candidate_names.add(name)
    Print('#candidate urls = %d, #candidate names = %d' %(len(candidate_urls), len(candidate_names)))
    # ename_title_map = resource.get_baike_ename_title()
    url2names = resource.get_url2names()

    title_names = set()
    title2url = {}
    for candidate_url in candidate_urls:
        enames = url2names[candidate_url]
        for ename in enames:
            if ename in candidate_names or count_filepath is None:
                # assert ename not in title_names
                title_names.add(ename)
                if ename in title2url:
                    pre_pop = baike_static_info_map[title2url[ename]].pop
                    pop = baike_static_info_map[candidate_url].pop
                    if pre_pop > pop:
                        title_url = title2url[ename]
                    else:
                        title_url = candidate_url
                else:
                    title_url = candidate_url
                title2url[ename] = title_url
            else:
                print "%s: miss name: %s" %(fb_type, ename)
    
    if extra_name_filepath is not None:
        Print("add extra name from [%s]" %extra_name_filepath)
        for line in file(extra_name_filepath):
            title_names.add(line.rstrip())

    outf = file(out_path, 'w')
    if url_path:
        url_outf = file(url_path, 'w')

    for title_name in sorted(title_names):
        if title_name == '无':
            continue
        if error_func is not None and error_func(title_name):
            print "%s: error func name: %s" %(fb_type, title_name)
            continue
        if len(title_name.decode('utf-8')) < 2:
            print "%s: short name: %s" %(fb_type, title_name)
            continue
        if is_chinese(title_name):
            outf.write(title_name + '\n')
            if url_path:

                url_outf.write("%s\t%s\n" %(title_name, title2url[title_name]))
    outf.close()

    if url_path:
        url_outf.close()

    
if __name__ == "__main__":
    count_dir = os.path.join(rel_ext_dir, "infobox_count")
    base_dir = os.path.join(rel_ext_dir, 'dict')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    gen_title_rel_dict("fb:location.country", os.path.join(count_dir, '国籍_cnt.tsv'), os.path.join(base_dir, 'nationality.txt'), 5, None, None, os.path.join(base_dir, 'nationality_url.txt'))
    gen_title_rel_dict("fb:people.profession", os.path.join(count_dir, '职业_cnt.tsv'), os.path.join(base_dir, 'profession.txt'), 10, None, None, os.path.join(base_dir, 'profession_url.txt'))
    gen_title_rel_dict("fb:language.human_language", None, os.path.join(base_dir, 'langauge.txt'), 0, os.path.join(doc_dir, 'human_add_language.txt'), error_func = lambda x:x.endswith('人'))


