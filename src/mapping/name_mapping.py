#encoding:utf-8
from ..IOUtil import load_json_dict, result_dir, Print
from ..util import add_to_dict_list
import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def extract_str(attrs, name):
    if name in attrs:
        value_list = attrs[name]
        value_list = [value.split("@")[0].strip('"').encode('utf-8') for value in value_list]
        return value_list
    else:
        return []




def extract_name_mapping(attrs_path):
    Print("extract name mapping from %s" %attrs_path)
    name_mapping = {}
    for cnt, line in enumerate(file(attrs_path), start = 1):
        if cnt % 1000000 == 0:
            Print("\textract cnt = %d" %cnt)
        
        p = line.split('\t')
        assert len(p) == 2
        key = p[0]
        attrs = json.loads(p[1])
        for name in extract_str(attrs, 'fb:type.object.name'):
            tag = key + "##0"
            add_to_dict_list(name_mapping, name, tag)

        for name in extract_str(attrs, 'fb:common.topic.alias'):
            tag = key + "##1"
            add_to_dict_list(name_mapping, name, tag)
    
    return name_mapping


if __name__ == "__main__":
    fb_attrs_path = os.path.join(result_dir, 'freebase/entity_attr.json')
    baike_attrs_path = os.path.join(result_dir, 'freebase/360_entity_info.json')

    # debug
    fb_attrs_path = os.path.join(result_dir, 'test/fb_attr.json')
    baike_attrs_path = os.path.join(result_dir, 'test/baike_attr.json')

    name_mapping = extract_name_mapping(fb_attrs_path)
    print name_mapping['人口指標，茅根']