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
        return reverse_map

    def is_mediator_prop(self, fb_property):
        expected_type = self.expected_type(fb_property)
        return self.is_mediator(expected_type)

    def is_mediator(self, fb_type):
        if fb_type in self.type_attrs:
            return get_bool(self.type_attrs[fb_type].get('fb:freebase.type_hints.mediator', '0'))
        else:
            return False
    
    def reverse_property(self, fb_property):
        return self.reverse_prop_map.get(fb_property, None)

    def expected_type(self, fb_property):
        return self.property_attrs[fb_property.split("^")[-1]]['fb:type.property.expected_type']
    
    def schema_type(self, fb_property):
        return self.property_attrs[fb_property.split("^")[0]]['fb:type.property.schema']

    def complement_type(self, fb_types):
        while True:
            new_types = set(fb_types)
            for fb_type in fb_types:
                if not fb_type in self.type_attrs:
                    continue
                child_types = self.type_attrs[fb_type].get('fb:freebase.type_hints.included_types', [])
                for child_type in child_types:
                    if child_type != "fb:common.topic":
                        new_types.add(child_type)
                    
            if len(new_types) == len(fb_types):
                return list(new_types)
            else:
                fb_types = new_types

    def check_spo(self, subj_types, prob, obj_types):
        subj_type = self.schema_type(prob)
        obj_type = self.expected_type(prob)
        return subj_type in subj_types and obj_type in obj_types



def get_bool(value):
    if value == "1":
        return True
    elif value == "0":
        return False
    elif value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    return value

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
    for line in file(os.path.join(doc_dir, 'human_add_type_attr.json'), 'r'):
        key, obj = line.split('\t')
        obj = json.loads(obj)
        for name in obj:
            attrs_map[key][name] = obj[name]
    return attrs_map

def load_predicates():
    pres = set()
    for line in file(os.path.join(doc_dir, 'final_property_attrs.json'), 'r'):
        pres.add(line.strip().split('\t')[0])
    return pres

def load_mediator_predicates():
    type_attrs = load_type_attrs()
    pres = set()
    for line in file(os.path.join(doc_dir, 'final_property_attrs.json'), 'r'):
        key, attrs = line.strip().split('\t')
        attrs = json.loads(attrs)
        schema_type = attrs['fb:type.property.schema']
        if not schema_type in type_attrs:
            continue
        if get_bool(type_attrs[schema_type].get('fb:freebase.type_hints.mediator', '0')):
            pres.add(key)
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
    # schema = Schema()
    # schema.init()
    # print schema.is_mediator('fb:geography.mountain_age')
    # print schema.is_mediator('fb:location.dated_location')
    # print schema.is_mediator('fb:location.cotermination')

    # pres = load_mediator_predicates()
    # print "fb:location.country.calling_code" in pres
    # print "fb:book.book_subject.works" in pres 
    # print "fb:education.education.student" in pres
    keys = set()
    schema = Schema()
    schema.init()
    for fb_type in schema.property_attrs:
        keys.update(schema.property_attrs[fb_type].keys())
    print list(keys)

