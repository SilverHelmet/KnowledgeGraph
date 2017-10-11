import json
import os

from tqdm import tqdm

from ...IOUtil import result_dir, load_json_map, Print
from ..predicate_mapping import load_baike_info, load_name_attr, load_ttl2map, extend_fb_ttls
from .gen_fb_property import load_mapping_pairs
from ..one2one_mapping_cnt import load_baike_name_attrs
from ..predicate_mapping import map_time
from ..fb_date import FBDatetime, BaikeDatetime
from ..name_mapping import del_space
from ...baike_process.process_entity_info import del_book_bracket, ignore_baike_name_attr
import units_transfer_table

def units_transfer(s):
    start = 0
    end = 0
    if s[0].isnumeric() or (s[0] == '+' and s[1].isnumeric()) or (s[0] == '-' and s[1].isnumeric()):
        end = 1
        for i in range(1, len(s)):
            if s[end].isdigit() or s[end] == '+' or s[end] == '-':
                print("num")
                end += 1
            elif s[end] == ',' or s[end] == '，' or s[end] == '.':
                if s[end + 1].isnumeric():
                    end += 1
                else:
                    break
            elif s[end] == 'e':
                if s[end + 1] == '+' or s[end + 1] == '-':
                    end += 1
                else:
                    break
            else:
                break
        tmp = s[start:end].replace(',', '')
        tmp = tmp.replace('，', '')
        num = float(tmp)
        units = s[end:len(s)]
        if units in units_transfer_table.transfer_table:
            new_num = num * units_transfer_table.transfer_table[units][0][0]
            new_s = str(new_num)
            return new_s
        else:
            return str(num) + units
    elif s[len(s) - 1].isnumeric():
        end = len(s)
        start = len(s) - 2
        for i in range(1, len(s)):
            if s[start].isnumeric() or s[start] == '+' or s[start] == '-':
                start -= 1
            elif s[start] == ',' or s[start] == '，' or s[start] == '.':
                if s[start + 1].isnumeric():
                    start -= 1
                else:
                    break
            elif s[start] == 'e':
                if s[start + 1] == '+' or s[start + 1] == '-':
                    start -= 1
                else:
                    break
            else:
                break
        tmp = s[start + 1:end].replace(',', '')
        tmp = tmp.replace('，', '')
        num = float(tmp)
        units = s[0:start + 1]
        if units in units_transfer_table.transfer_table:
            new_num = num * units_transfer_table.transfer_table[units][0][0]
            new_s = str(new_num)
            return new_s
        else:
            return str(num) + units
    else:
        return s

def extend_name(fb_info, name_map):
    value_names = []
    for name, value in fb_info:
        if value in name_map:
            values = name_map[value]
        else:
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            values = [value]
        value_names.append((name, values))
    return value_names

def extract_info_value(info):
    str_values = []
    time_values = []
    for name, fb_values in info:
        for fb_value in fb_values:
            fb_value = del_space(fb_value)
            str_values.append(fb_value)
    str_values = list(set(str_values))
    for str_value in str_values:
        fb_time = FBDatetime.parse_fb_datetime(str_value)
        if fb_time is not None:
            time_values.append(fb_time)
    return str_values, time_values



def extend_name_onece(fb_entity_info, name_map):
    new_entity_info = {}
    Print("extend fb entity info's name")
    for e in tqdm(fb_entity_info, total = len(fb_entity_info)):
        new_info = extend_name(fb_entity_info[e], name_map)
        str_values, time_values = extract_info_value(new_info)
        new_entity_info[e] = (str_values, time_values)
    return new_entity_info

def load_processed_entity_info(in_path, total):
    Print("load processed entity info from [%s]" %in_path)
    info = {}
    for line in tqdm(file(in_path), total = total):
        p = line.split('\t')
        key = p[0]
        str_values = json.loads(p[1])
        time_values = []
        for str_value in str_values:
            time_value = FBDatetime.parse_fb_datetime(str_value)
            if time_value is not None:
                time_values.append(time_value)
        info[key] = (str_values, time_values)
    return info


def find_match(baike_date, fb_time_values):
    for fb_date in fb_time_values:
        if map_time(fb_date, baike_date):
            return True
    return False

def calc_infobox_mapping_score(baike2fb_map, baike_entity_info, fb_entity_info, baike_name_attrs, outf):
    baike_name_attrs = set(baike_name_attrs)
    Print('calc mapping score')
    for baike_url in tqdm(baike2fb_map, total = len(baike2fb_map)):
        fb_uris = baike2fb_map[baike_url]
        baike_info = ignore_baike_name_attr(baike_entity_info, baike_name_attrs, baike_url)
        nb_baike_info = len(baike_info)

        str2date_cache = {}
        for fb_uri in fb_uris:
            fb_str_values, fb_time_values = fb_entity_info.get(fb_uri, ([], []))
            nb_fb_info = len(fb_str_values)
            nb_fb_time_info = len(fb_time_values)

            match_cnt = 0
            time_match_cnt = 0 
            nb_baike_time_info = 0
            nb_baike_info = 0
            

            for baike_info_name in baike_info:
                baike_values = baike_info[baike_info_name]
                match = False

                for baike_value in baike_values:
                    nb_baike_info += 1
                    if del_book_bracket(baike_value) in fb_str_values:
                        match = True
                    else:
                        if not baike_value in str2date_cache:
                            str2date_cache[baike_value] = BaikeDatetime.parse(baike_value)
                        baike_date = str2date_cache[baike_value]
                        if baike_date is not None:
                            nb_baike_time_info += 1
                            match = find_match(baike_date, fb_time_values)
                            if match:
                                time_match_cnt += 1
                        baike_number = units_transfer(baike_value)
                        if str(baike_number) in fb_str_values:
                        	match = True
                    if match:
                        break

                if match:
                    match_cnt += 1
            map_obj = {
                'baike_url': baike_url,
                'fb_uri': fb_uri,
                '#baike_info': nb_baike_info,
                '#baike_time_info': nb_baike_time_info,
                "#fb_info": nb_fb_info,
                '#fb_time_info': nb_fb_time_info, 
                "#match": match_cnt,
                '#time_match': time_match_cnt,
            }
            outf.write(json.dumps(map_obj) + '\n')
            # outf.flush()
            # maps.append(map_obj)
    # return maps


if __name__ == "__main__":
    mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    out_dir = os.path.join(result_dir, '360/mapping/classify')
    baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)
    print "baike2fb_map", len(baike2fb_map)
    print "baike_entities", len(baike_entities)
    print "fb_entities", len(fb_entities)

    baike_name_attrs = load_baike_name_attrs()

    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    baike_entity_info = load_baike_info(baike_entity_info_path, total = 21710208, entities = set(baike_entities))

    print "baike_entitiy_info", len(baike_entity_info)


    # fb_entity_info_path = os.path.join(result_dir, '360/mapping/classify/mapped_fb_entity_info.json')
    # fb_entity_info = load_json_map(fb_entity_info_path, total = 6282988)


    # name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
    #         os.path.join(result_dir, 'freebase/entity_alias.json')]
    # totals = [39345270, 2197095]
    # name_map = load_name_attr(name_files, totals)

    # fb_entity_info = extend_name_onece(fb_entity_info, name_map)

    # del  name_map

    fb_entity_info = load_processed_entity_info(os.path.join(out_dir, 'mapped_fb_entity_info_processed.json'), total = 6282988)

    out_path = os.path.join(out_dir, 'map_scores.json')
    outf = file(out_path, 'w')
    calc_infobox_mapping_score(baike2fb_map, baike_entity_info, fb_entity_info, baike_name_attrs, outf)
    outf.close()

    # Print("other name attr count")
    # for o_name in sorted(o_name_cnt.keys(), key = lambda x: o_name_cnt[x], reverse = True):
    #     print o_name, o_name_cnt[o_name]
    # outf = file(out_path, 'w')
    # for map_obj in map_scores:
    #     outf.write(json.dumps(map_obj) + '\n')
    # outf.close()
    
    # print "name_map", len(name_map)
    # description_map = load_name_attr([os.path.join(result_dir, 'freebase/entity_description.json')], totals = [6426977], fb_entities = set(fb_entities))
    





    