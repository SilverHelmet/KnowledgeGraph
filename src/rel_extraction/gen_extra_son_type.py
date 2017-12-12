#encoding: utf-8
from src.IOUtil import extra_type_dir
from src.extractor.resource import Resource
import os
from .extract_son_name_map import is_art_work
from src.util import add_to_dict_list
import json

def extract_type_info(son_name_map_path, bk_type_info_path):
    if os.path.exists(bk_type_info_path):
        return
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

def infer_name_group(urls, info_map, group_types):
    scores = [0] * len(group_types)
    for url in urls:
        info = info_map[url]
        if info['fb'] == 'None':
            power = 1
        else:
            power = 10
        types = info['type']

        for idx, group_type in enumerate(group_types):
            if group_type in types:
                scores[idx] += power

    max_score_idx = 0
    occur_cnt = 0
    for idx, score in enumerate(scores):
        if score > scores[max_score_idx]:
            max_score_idx = idx
        if score > 0:
            occur_cnt += 1
    return max_score_idx, scores[max_score_idx]


def infer_group(parent, sons, parent_types, son_types, name2url, info_map):
    scores = [0] * len(parent_son_types)
    idx, score = infer_name_group(name2url[parent], info_map, parent_types)
    score = score * 10

    scores[idx] += score
    

    for son in sons:
        idx, score = infer_name_group(name2url[son], info_map, son_types)
        scores[idx] += score

    max_score_idx = 0
    for idx, score in enumerate(scores):
        if score > scores[max_score_idx]:
            max_score_idx = idx
    if scores[max_score_idx] > 0:
        return parent_types[max_score_idx]
    else:
        return None

def choose_parent_urls(urls, info_map, parent_type, all_son_names):
    scores = []
    for url in urls:
        types = info_map[url]['type']
        score = 0
        names = info_map[url]['name']
        is_son = False
        for name in names:
            if name in all_son_names:
                is_son = True
        if parent_type in types:
            score = 1

        if info_map[url]['fb'] == "None":
            pass
        else:
            score = score * 10 + 0.01
        if is_son:
            score = -1
        scores.append(score)
    
    max_score = reduce(max, scores, 0)
    

    parent_urls = []
    for url, score in zip(urls, scores):
        if score == max_score:
            parent_urls.append(url)
    # if max_score == 0:
    #     print len(parent_urls)
    # if len(parent_urls) == 0:
    #     print 'error', urls
    return parent_urls    

def choose_son_urls(name2url, son_names, son_group):
    urls = []
    for son_name in son_names:
        son_urls = name2url[son_name]
        urls.extend(son_urls)
    return urls

def gen_extra_type(son_name_map_path, bk_info_path, parent_son_types, ends_to_types, outpath):
    parent_types = [x[0] for x in parent_son_types]
    son_types = [x[1] for x in parent_son_types]
    info_map = {}
    name2url = {}
    for line in file(bk_info_path):
        bk_url, info = line.split('\t')
        info = json.loads(info)
        info_map[bk_url] = info
        for name in info['name']:
            add_to_dict_list(name2url, name, bk_url)

    all_son_names = set()
    for line in file(son_name_map_path):
        names = line.strip().split('\t')
        names = [x.decode('utf-8') for x in names]
        parent = names[0]
        sons = names[1:]
        all_son_names.update(sons)

    extra_type_map = {}
    for line in file(son_name_map_path):
        names = line.strip().split('\t')
        names = [x.decode('utf-8') for x in names]
        parent = names[0]
        sons = names[1:]
        group = infer_group(parent, sons, parent_types, son_types, name2url, info_map)
        if group:
            pass
        else:
            for end, end_group in ends_to_types:
                if parent.endswith(end):
                    group = end_group   

        if not group:
            continue
        
        parent_urls = choose_parent_urls(name2url[parent], info_map, group, all_son_names)
        for url in parent_urls:
            add_to_dict_list(extra_type_map, url, group)

        son_group = None
        for parent_type, son_type in parent_son_types:
            if parent_type == group:
                son_group = son_type

        assert son_group

        son_urls = choose_son_urls(name2url, sons, son_group)
        for url in son_urls:
            add_to_dict_list(extra_type_map, url, son_group)

    outf = file(outpath, 'w')
    for url in sorted(extra_type_map.keys()):
        ori_types = info_map[url]['type']
        extra_types = set(extra_type_map[url])
        extra_types = [x for x in extra_types if not x in ori_types]
        if len(extra_types) > 1:
            print " ".join(info_map[url]['name']), url, extra_types
        if len(extra_types) > 0:
            outf.write('%s\t%s\n' %(url, "\t".join(extra_types)))
    outf.close()

if __name__ == "__main__":
    parent_son_types = [
        ('fb:film.film_festival', 'fb:film.film_festival_event'),
        ('fb:award.award', 'fb:award.award_ceremony'),
        ('fb:sports.sports_league', 'fb:sports.sports_league_season'),
        ('fb:sports.sports_championship', 'fb:sports.sports_championship_event'),
    ]
    ends_to_types = [
        (u'杯', 'fb:sports.sports_championship'),
        (u'联赛', 'fb:sports.sports_league'),
        (u'奥运会', 'fb:sports.sports_championship'),
        (u'电影节', 'fb:film.film_festival'),
        (u'奖', 'fb:award.award'),
        (u'赛', 'fb:sports.sports_championship'),
        (u'运动会', 'fb:sports.sports_championship'),
        (u'艺术节', 'fb:award.award'),
    ]
    son_name_map_path = os.path.join(extra_type_dir, 'son_name_map.tsv')
    bk_info_path = os.path.join(extra_type_dir, 'local_info.json')
    extra_type_path = os.path.join(extra_type_dir, 'extra_type.tsv')
    extract_type_info(son_name_map_path, bk_info_path)

    gen_extra_type(son_name_map_path, bk_info_path, parent_son_types, ends_to_types, extra_type_path)