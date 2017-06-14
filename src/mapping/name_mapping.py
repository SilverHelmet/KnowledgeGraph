#encoding:utf-8
from ..IOUtil import load_json_dict, result_dir, Print
from ..util import add_to_dict_list
import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def del_space(text):
    return text.replace(u'\xa0', '').strip()

def extract_str(attrs, name):
    if name in attrs:
        value_list = attrs[name]
        value_list = [value.split("@")[0].strip('"') for value in value_list]
        return value_list
    else:
        return []

def extract_name_mapping(attrs_path):
    Print("extract name mapping from %s" %attrs_path)
    name_mapping = {}
    lower_name_mapping = {}
    for cnt, line in enumerate(file(attrs_path), start = 1):
        if cnt % 1000000 == 0:
            Print("\textract cnt = %d" %cnt)
        
        p = line.split('\t')
        assert len(p) == 2
        key = p[0]
        attrs = json.loads(p[1])
        for name in extract_str(attrs, 'fb:type.object.name'):
            add_to_dict_list(name_mapping, name, key + "#name")
            add_to_dict_list(lower_name_mapping, name.lower(), key + '#name_l')

        for name in extract_str(attrs, 'fb:common.topic.alias'):
            add_to_dict_list(name_mapping, name, key + "#alias")
            add_to_dict_list(lower_name_mapping, name.lower(), key + "#alias_l")
    
    return name_mapping, lower_name_mapping

def mapping(name_mapping, name, res, key):
    if name is None:
        return
        
    if name in name_mapping:
        if not key in res:
            res[key] = []
        res[key].extend(name_mapping[name])

        

def do_mapping(name_mapping, baike_path, out_path):
    Print('mapping from %s' %baike_path)
    Print("do mapping, write to %s" %out_path)
    outf = file(out_path, 'w')

    for cnt, line in enumerate(file(baike_path), start = 1):
        if cnt % 100000 == 0:
            Print("mapping cnt = %d" %cnt)
        p = line.split("\t")
        baike_uri = p[0]

        res = {}
        attrs = json.loads(p[1])
        ename = attrs.get('ename', None).strip()
        mapping(name_mapping, ename, res, 'ename')
        
        title = attrs.get('title', None).strip()
        mapping(name_mapping, title, res, 'title')

        if 'info' in attrs:
            info = attrs['info']
            for key in info:
                values = info[key]
                key = del_space(key)
                for value in values:
                    value = value.strip()
                    mapping(name_mapping, value, res, key)
        
        if len(res) > 0:
            outf.write("%s\t%s\n" %(baike_uri, json.dumps(res, ensure_ascii = False)))
    outf.close()




if __name__ == "__main__":
    fb_attrs_path = os.path.join(result_dir, 'freebase/entity_attr.json')
    baike_attrs_path = os.path.join(result_dir, '360/360_entity_info_processed.json')

    # debug
    # fb_attrs_path = os.path.join(result_dir, 'test/fb_attr.json')
    # baike_attrs_path = os.path.join(result_dir, 'test/baike_attr.json')
    # out_path = os.path.join(result_dir, "test/mapping_result.json")

    name_mapping, lower_name_mapping = extract_name_mapping(fb_attrs_path)
    do_mapping(name_mapping, baike_attrs_path, os.path.join(result_dir, '360/360_mapping.json'))
    do_mapping(lower_name_mapping, baike_attrs_path, os.path.join(result_dir, '360/360_mapping_lowercase.json'))

