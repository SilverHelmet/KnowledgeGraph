#encoding: utf-8
from ..IOUtil import rel_ext_dir, Print, result_dir
from ..mapping.predicate_mapping import load_name_attr
from ..baike_process.parse import html_unescape
from util import load_mappings, load_bk_types
import json
import os
from tqdm import tqdm
from ..mapping.one2one_mapping_cnt import load_baike_name_attrs
from src.baike_process.process_entity_info import unfold

def load_mapping_names(bk2fb):
    fb_uris = set(bk2fb.values())
    Print('#fb uris is %d' %len(fb_uris))
    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
                os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]

    fb_name_map = load_name_attr(name_files, totals, fb_uris)
    Print("#fb name map is %d" %len(fb_name_map))

    bk_name_map = {}
    for bk_url in bk2fb:
        fb_uri = bk2fb[bk_url]
        names = fb_name_map.get(fb_uri, [])
        if len(names) > 0:
            bk_name_map[bk_url] = names
    return bk_name_map

def person_extra_names(name):
    tokens = name.split(u"·")
    names = []
    if len(tokens) >= 2:
        names.append(tokens[-1])
        names.append(tokens[0])
    if len(tokens) >= 3:
        names.append(tokens[0] + u"·" + tokens[-1])

    return names

def load_and_write_baike_name(bk_name_map, out_path):
    bk_types_map = load_bk_types()
    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    total = 21710208
    Print('load and write baike name to [%s]' %out_path)
    baike_name_attrs = load_baike_name_attrs()
    outf = file(out_path, 'w')
    for line in tqdm(file(baike_entity_info_path), total = total):
        p = line.split('\t')
        bk_url = p[0].decode('utf-8')
        
        names = bk_name_map.get(bk_url, [])
        obj = json.loads(p[1])
        names.append(obj['ename'])
        names.append(obj['title'])

        info = obj.get('info', {})
        for attr in info:
            if attr in baike_name_attrs:
                names.extend(info[attr])

        
        names = [html_unescape(x.replace('\n',"")).strip() for x in names]

        is_person = "fb:people.person" in bk_types_map[bk_url]
        if is_person:
            extra_names = []
            for name in names:
                extra_names = person_extra_names(name)
            names.extend(extra_names)
        names = list(set(names))

        outf.write("%s\t%s\n" %(bk_url, "\t".join(names)))
    outf.close()

def count_bracket_names():
    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info.json')
    total = 21710208
    Print('count names in bracket from [%s]' %baike_entity_info_path)
    baike_name_attrs = load_baike_name_attrs()
    bracket_value_cnt = {}
    for line in tqdm(file(baike_entity_info_path), total = total):
        url, obj = line.split('\t')
        obj = json.loads(obj)
        names = set([obj['ename'], obj['title']])
        info = obj['info']
        bracket_values = []
        for baike_name in baike_name_attrs:
            if not baike_name in info:
                continue
            info_values = info[baike_name]
            for info_value in info_values:
                if info_value in names:
                    continue
                unfold(info_value, bracket_values)

        bracket_values = set(bracket_values)
        for bracket_value in bracket_values:
            if not bracket_value in bracket_value_cnt:
                bracket_value_cnt[bracket_value] = 0
            bracket_value_cnt[bracket_value] += 1
    return bracket_value_cnt

def process_bracket_names(outpath):
    bracket_value_cnt = count_bracket_names()
    outf = file(outpath, 'w')
    for key in sorted(bracket_value_cnt.keys(), key = lambda x: bracket_value_cnt[x], reverse = True):
        outf.write("%s\t%s\n" %(key, bracket_value_cnt[key]))
    outf.close()


if __name__ == "__main__":
    process_bracket_names(outpath = os.path.join(rel_ext_dir, 'bracket_names_cnt.tsv'))


    # bk2fb = load_mappings()
    # bk_name_map = load_mapping_names(bk2fb)

    # out_path = os.path.join(rel_ext_dir, 'baike_names.tsv')
    # load_and_write_baike_name(bk_name_map, out_path)