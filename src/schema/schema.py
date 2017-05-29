#encode:utf-8
from ..fb_process.extract_util import get_domain
from ..IOUtil import doc_dir, result_dir
import sys
import os
import json

class Schema:
    def __init__(self):
        pass
    
    def init(self):
        self.property_attrs = load_property_attrs()
        self.type_attrs = load_type_attrs()
        self.reverse_prop_map = self.get_reverse_property_map(self.property_attrs)
    
    def get_reverse_property_map(self, property_attrs):
        reverse_map = {}
        reverse_property = 'fb:type.property.reverse_property'
        for fb_property in property_attrs:
            attr = property_attrs[fb_property]
            if reverse_property in attr:
                reverse_fb_prop = attr[reverse_property]
                assert fb_property not in reverse_map and reverse_fb_prop not in reverse_map
                reverse_map[fb_property] = reverse_fb_prop
                reverse_map[reverse_fb_prop] = fb_property


    def is_mediator(self, fb_type):
        if fb_type in self.property_attrs:
            return bool(self.property_attrs[fb_type].get('fb:freebase.type_hints.mediator', False))
        else:
            return False
    
    def reverse_property(self, fb_property):
        return self.reverse_prop_map.get(fb_property, None)

    def expected_type(self, fb_property):
        return self.property_attrs[fb_property]['fb:type.property.expected_type']

def load_entity():
    total = 56490649
    entities = set()
    cnt = 0
    chunk = total / 100
    next_percent_cnt = 0
    percent = 0
    for line in file(os.path.join(result_dir, 'freebase/entity_type.json'), 'r'):
        cnt += 1
        if cnt >= next_percent_cnt:
            sys.stdout.write("\rload entity %d%%" %percent)
            percent += 1
            next_percent_cnt += chunk
        uri = line.split('\t')[0]
        entities.add(uri)
    print "\nload entity finished"
    return entities


def load_types():
    types = set()
    for line in file(os.path.join(doc_dir, 'final_type_attrs.json'), 'r'):
        types.add(line.strip().split("\t")[0])
    return types

def load_type_attrs():
    attrs_map = {}
    for line in file(os.path.join(doc_dir, 'final_type_attrs.json'), 'r'):
        key, obj = line.split('\t')
        attrs_map[key] = json.loads(obj)
    return attrs_map

def load_predicates():
    pres = set()
    for line in file(os.path.join(doc_dir, 'final_property_attrs.json'), 'r'):
        pres.add(line.strip().split('\t')[0])
    return pres

def load_property_attrs():
    attrs_map = {}
    for line in file(os.path.join(doc_dir, 'final_property_attrs.json'), 'r'):
        key, obj = line.split('\t')
        attrs_map[key] = json.loads(obj)
    return attrs_map

def is_zh_en_literal(uri):
    p = uri.strip().split("@")
    if len(p) == 2 and p[0].startswith('"') and p[0].endswith('"'):
        return p[1] in ['zh', 'en']
    return False

def add_attr(dict, id, name, value):
    if not id in dict:
        dict[id] = {}
    attr = dict[id]
    if not name in attr:
        attr[name] = []
    attr[name].append(value)
        
        

if __name__ == "__main__":
    pass