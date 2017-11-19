#encoding: utf-8
from src.IOUtil import infobox_cnt_dir, dict_dir, load_file, Print
import os
from src.extractor.resource import Resource
from src.util import is_chinese
from src.extractor.util import get_domain
import commands

if __name__ == "__main__":
    prof_cnt_path = os.path.join(infobox_cnt_dir, '职业_cnt.tsv')
    prof_cnt_threshold = 10
    
    prof_dict_path = os.path.join(dict_dir, 'profession.txt')
    prof_dict = set(load_file(prof_dict_path))

    candidate_profs = set()
    for line in file(prof_cnt_path):
        p = line.split('\t')
        if len(p) == 2:
            prof = p[0]
            cnt = int(p[1])
            if cnt >= prof_cnt_threshold and is_chinese(prof) and prof not in prof_dict and len(prof.decode('utf-8')) >= 2:
                candidate_profs.add(prof)

    Print("#candidate name = %d" %len(candidate_profs))
    resource = Resource.get_singleton()
    baike_ename_title_map = resource.get_baike_ename_title()
    prof2bk = {}
    for bk_url in baike_ename_title_map:
        enames = baike_ename_title_map[bk_url]
        for ename in enames:
            if ename in candidate_profs:
                if not ename in prof2bk:
                    prof2bk[ename] = set()
                prof2bk[ename].add(bk_url)

    Print("#hit candidate name = %d" %len(prof2bk))
    extra_prof_out_path = os.path.join(dict_dir, 'extra_profession.txt')
    prof_outf = file(extra_prof_out_path, 'w')
    prof_type_outf = file(os.path.join(dict_dir, 'extra_profession_types.tsv'), 'w')
    baike_info_map = resource.get_baike_info()
    error_types = ['fb:people.person', 'fb:film.film', 'fb:book.book', 'fb:book.written_work', 'fb:cvg.computer_videogame', 'fb:tv.tv_program', 'fb:book.periodical', 'fb:comic_books.comic_book_series']
    error_domains = set([get_domain(bk_type) for bk_type in error_types])
    error_domains.add('fb:award')
    for prof in prof2bk:
        bk_urls = prof2bk[prof]
        valid_bk_urls = []
        for bk_url in bk_urls:
            valid = True
            info = baike_info_map[bk_url]
            types = info.types
            for bk_type in types:
                if get_domain(bk_type) in error_domains:
                    valid = False
            if valid:
                valid_bk_urls.append(bk_url)
        if len(valid_bk_urls) == 1:
            prof_outf.write("%s\n" %(prof))
            prof_type_outf.write("%s\t%s\n" %(valid_bk_urls[0], "fb:people.profession"))
            

    prof_outf.close()
    prof_type_outf.close()

    
    full_out_path = os.path.join(dict_dir, 'full_profession.txt')
    commands.getstatus('cat %s %s > %s' %(prof_dict_path, extra_prof_out_path, os.path.join(full_out_path) ))