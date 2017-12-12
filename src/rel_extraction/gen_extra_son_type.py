from src.IOUtil import extra_type_dir
from src.extractor.resource import Resource
import os
from .extract_son_name_map import is_art_work
import json

def extract_type_info(son_name_map_path, bk_type_info_path):
    # if os.path.exists(bk_type_info_path):
    #     return
    resource = Resource.get_singleton()
    baike_ename_title = resource.get_baike_ename_title()
    name2bk = resource.get_name2bk()
    baike_info_map = resource.get_baike_info()

    ename2bk = {}
    for bk_url in baike_ename_title:
        if not bk_url in baike_info_map:
            continue
        types = baike_info_map[bk_url].types
        if is_art_work(types):
            continue
            
        enames = baike_ename_title[bk_url]
        for ename in enames:
            if not ename in ename2bk:
                ename2bk[ename] = []
            ename2bk[ename].append(bk_url)
    

    local_info_map = {}
    for line in file(son_name_map_path, 'r'):
        names = line.strip().split('\t')
        parent_name = names[0]
        son_names = names[1:]
        parent_urls = name2bk[parent_name]
        for parent_url in parent_urls:
            types = baike_info_map[parent_url].types
            if is_art_work(types):
                continue
            
            if not parent_url in local_info_map:
                local_info_map[parent_url] = {}
            info = local_info_map[parent_url]
            info['type'] = types
            info['fb'] = baike_info_map[parent_url].fb_uri
            if not 'name' in info:
                info['name'] = []
            info['name'].append(parent_name)

        for son_name in son_names:
            son_urls = ename2bk[son_name]
            
            for son_url in son_urls:
                if not son_url in local_info_map:
                    local_info_map[son_url] = {}
                types = baike_info_map[son_url].types
                info = local_info_map[son_url]
                info['type'] = types
                info['fb'] = baike_info_map[parent_url].fb_uri
                if not 'name' in info:
                    info['name'] = []
                info['name'].append(son_name)
            
    outf = file(bk_type_info_path, 'w')
    for url in local_info_map:
        outf.write('%s\t%s\n' %(url, json.dumps(local_info_map[url], ensure_ascii = False)))
    outf.close()

if __name__ == "__main__":
    parent_son_types = [
        ('fb:film.film_festival', 'fb:film.film_festival_event'),
        ('fb:award.award', 'fb:award.award_ceremony'),
        ('fb:sports.sports_championship', 'fb:sports.sports_championship_event'),
        ('fb:sports.sports_league', 'fb:sports.sports_league_season')
    ]
    son_name_map_path = os.path.join(extra_type_dir, 'son_name_map.tsv')
    bk_info_path = os.path.join(extra_type_dir, 'local_info.json')
    extract_type_info(son_name_map_path, bk_info_path)