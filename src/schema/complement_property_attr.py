from ..IOUtil import result_dir
from ..extract.extract_util import get_type, encode, get_domain
from ..queryKG.query_util import get_unique_attr
import os
import json


def boolean_of(value):
    if type(value) == int:
        return value == 1
    elif type(value) == str or type(value) == unicode: 
        return value == 'true' or value == 'True' or value == '1'
    else:
        print type(value)
        print "error"
        return None


def check_compatiable(name, value1, value2):
    if name == "fb:type.property.unique":
        return boolean_of(value1) == boolean_of(value2)
    else:
        return value1 == value2

def load_valid_types(filepath):
    ret = set()
    for line in file(filepath):
        p = line.split('\t')
        fb_type = p[0]
        attrs = json.loads(p[1])
        if attrs['count'] > 0:
            ret.add(fb_type)
    return ret

def check_valid_type(type):
    global valid_types
    domain = get_domain(type)
    if domain in ['fb:type']:
        return True
    # if domain in ['fb:type', 'fb:common', 'fb:user', 'fb:freebase', 'fb:base']:
        # return True
    return type in valid_types

class Property:
    def __init__(self, property_uri):
        self.uri = encode(property_uri)
        self.attrs = {}
        self.attrs['fb:type.property.schema'] = get_type(property_uri)

    def set_attr(self, name, value):
        name = name.encode('utf-8')
        if type(value) == list:
            value = [encode(x) for x in value]
        else:
            value = encode(value)
        if name in self.attrs:
            assert self.attrs[name] == value
        else:
            self.attrs[name] = value

    def fusion(self, attrs):
        for name in attrs:
            if name in self.attrs:
                if not check_compatiable(name, attrs[name], self.attrs[name]):
                    print 'conflict ', self.uri, name, self.attrs[name], attrs[name]
                # assert check_compatiable(name, attrs[name], self.attrs[name])
            else:
                if name not in ['fb:common.topic.description', 'fb:type.property.master_property', 'fb:freebase.property_hints.inverse_description', 'fb:freebase.property_hints.enumeration'] and self.attrs['count'] > 0:
                    print 'add ', self.uri, name, attrs[name]
                self.attrs[name] = attrs[name]

    def check_complete(self):
        assert self.attrs['fb:type.property.schema']
        assert self.attrs['count'] <= 20 or 'fb:type.property.expected_type' in self.attrs
        if 'fb:type.property.expected_type' in self.attrs:
            flag =  check_valid_type(self.attrs['fb:type.property.expected_type'])
            if not flag:
                print self.uri, self.attrs['fb:type.property.expected_type']

def init_property(attrs_path):
    unique_attrs = get_unique_attr()
    p_map = {}
    for line in file(attrs_path, 'r'):
        p = line.split('\t')
        property_uri = p[0]
        attrs = json.loads(p[1])
        if attrs['count']  == 0:
            continue
        fb_property = Property(property_uri)
        for name in attrs: 
            value = attrs[name]
            if name in unique_attrs:
                assert len(value) == 1
                value = value[0]
            fb_property.set_attr(name, value)

            
        p_map[property_uri] = fb_property
    return p_map

def check_complete(property_map):
    for fb_property in property_map.values():
        fb_property.check_complete()

def squeeze(attrs):
    uniq_attrs = get_unique_attr()
    for name in attrs:
        if name in uniq_attrs:
            value = attrs[name]
            assert len(value) == 1
            attrs[name] = value[0]

def complement(property_map, attrs_path):
    cnt = 0
    for line in file(attrs_path):
        p = line.split("\t")
        uri = p[0]
        attrs = json.loads(p[1])
        squeeze(attrs)
        if uri in property_map:
            cnt += 1
            property_map[uri].fusion(attrs)
    print "complement check cnt = %d" %cnt

if __name__ == "__main__":
    data_dir = os.path.join(result_dir, 'freebase_merged')
    
    
    type_attrs_path = os.path.join(data_dir, 'type_attrs.json')
    valid_types = load_valid_types(type_attrs_path)

    attrs_path = os.path.join(data_dir, 'property_attrs.json')
    property_map = init_property(attrs_path)

    check_complete(property_map)

    # old_attrs_path = os.path.join(result_dir, 'old_freebase/queried_property_attrs.json')    
    # complement(property_map, old_attrs_path)
    # check_complete(propery_map)
    # load()