#encoding: utf-8
from src.IOUtil import Print, rel_ext_dir, nb_lines_of, extra_name_dir
from src.extractor.resource import Resource
from  src.extractor.entity.ner import NamedEntityReg
from src.baike_process.process_page import split_sentences
import os
from tqdm import tqdm
import json
from .dict.collect_team_suffix import load_team_suffix, try_get_suffix
from .extract_summary_extra_name import has_strange_punc
import re

org_types = set([
    'fb:organization.organization', 
    'fb:fictional_universe.fictional_organization', 
    'fb:sports.sports_team'
    ])

def is_org(types):
    global org_types
    for org_type in org_types:
        if org_type in types:
            return True
    return False

re_eng_digit = re.compile(ur'[0-9a-zA-Z]')
def has_eng_digit(name):
    global re_eng_digit
    return re_eng_digit.search(name) is not None

location_ends = ['城','市','','州','洲','省']
def is_location(name, location_dict):
    global location_ends
    if type(name) is unicode:
        name = name.encode('utf-8')
    for end in location_ends:
        if name + end in location_dict:
            return True
    return False

def parse_entity(sentence, ltp, ner, location_dict):
    if type(sentence) is unicode:
        sentence = sentence.encode('utf-8')

    ltp_result = ltp.parse(sentence)
    str_entities = ner.recognize(sentence, ltp_result, None, None)
    names = []
    for str_entity in str_entities:
        if str_entity.etype in ['Ns', 'Ns-ATT']:
            continue
        name = ltp_result.text(str_entity.st, str_entity.ed)
        if is_location(name, location_dict):
            continue
        names.append(name.decode('utf-8'))

    j_names = []
    for i in range(ltp_result.length):
        if ltp_result.tags[i] == 'j':
            j_names.append(ltp_result.words[i].decode('utf-8'))
    return names, j_names

def is_good_sub_seq(parsed_name, ename, suffix):
    suffix_pos = len(ename) - len(suffix)
    p_pos = 0
    e_pos = 0
    in_suffix_cnt = 0
    while p_pos < len(parsed_name):
        while e_pos < len(ename) and ename[e_pos] != parsed_name[p_pos]:
            e_pos += 1
        
        if e_pos == len(ename):
            break

        if e_pos >= suffix_pos:
            in_suffix_cnt += 1
        e_pos += 1
        p_pos += 1
    
    if p_pos != len(parsed_name):
        return False

    if in_suffix_cnt >= 2:
        return False

    if len(parsed_name) - in_suffix_cnt < 2:
        return False

    return True

def extract_org_extra_name_from_summary(summary_path, out_path):

    resource = Resource().get_singleton()
    url2names = resource.get_url2names()
    ename_title_map = resource.get_baike_ename_title()
    baike_info_map = resource.get_baike_info()
    location_dict = resource.get_location_dict()
    ltp = resource.get_ltp()

    ner = NamedEntityReg()
    team_suffixes = load_team_suffix()
    team_suffixes = [x.decode('utf-8') for x in team_suffixes]

    Print('extract org\'s extra name from summary [%s]' %summary_path)
    Print("result write to [%s]" %out_path)
    outf = file(out_path, 'w')
    for line in tqdm(file(summary_path), total = nb_lines_of(summary_path)):
        bk_url, summary = line.split('\t')
        types = baike_info_map[bk_url].types
        if not is_org(types):
            continue  

        enames = ename_title_map[bk_url]
        enames = [x.decode('utf-8') for x in enames]  
        ori_names = url2names[bk_url]
        ori_names = set([x.decode('utf-8') for x in ori_names])

        summary = json.loads(summary)['summary']
        sentences = split_sentences(summary)


        parsed_names = []
        j_names_cnt = {}
        for sentence in sentences:
            names, j_names = parse_entity(sentence, ltp, ner, location_dict)
            parsed_names.extend(names)
            for j_name in j_names:
                if not j_name in j_names_cnt:
                    j_names_cnt[j_name] = 0
                j_names_cnt[j_name] += 1

        
        succeed_names = set()
        suffixes = []
        for ename in enames:
            if "fb:sports.sports_team" in types:
                suffix = try_get_suffix(ename, team_suffixes)
            else:
                suffix = u''
            suffixes.append(suffix)

            if has_eng_digit(ename):
                continue

            if len(suffix) > 0:
                new_name = ename[:len(ename) - len(suffix)]
                if not is_location(new_name, location_dict):
                    succeed_names.add(new_name)
                    succeed_names.add(new_name + u"队")


        parsed_names = set(parsed_names)
        for parsed_name in parsed_names:
            valid = False
            
            for ename, suffix in zip(enames, suffixes):
                if has_eng_digit(ename):
                    continue
                if is_good_sub_seq(parsed_name, ename, suffix):
                    valid = True
            if valid:
                succeed_names.add(parsed_name)

        for j_name in j_names_cnt:
            if j_names_cnt[j_name] >= 2:
                valid = False
                for ename, suffix in zip(enames, suffixes):
                    if has_eng_digit(ename):
                        continue
                    if j_name not in ename and is_good_sub_seq(j_name, ename, suffix):
                        valid = True
                if valid:
                    succeed_names.add(j_name)

        succeed_names = [new_name for new_name in succeed_names if not new_name in ori_names]
        succeed_names = [new_name for new_name in succeed_names if not has_strange_punc(new_name)]
        if len(succeed_names) > 0:
            succeed_names = set(succeed_names)
            outf.write('%s\t%s\n' %(bk_url, "\t".join(succeed_names)))

    outf.close()


            




if __name__ == "__main__":
    summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary.json')
    extra_org_out_path = os.path.join(extra_name_dir, 'extra_org_name.tsv')
    extract_org_extra_name_from_summary(summary_path, extra_org_out_path)

    

