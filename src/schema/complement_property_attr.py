from ..IOUtil import result_dir, base_dir
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
    if name in ["fb:type.property.unique"]:
        return boolean_of(value1) == boolean_of(value2)
    else:
        return value1 == value2

def load_valid_types(filepath):
    ret = set()
    for line in file(filepath):
        p = line.split('\t')
        fb_type = p[0]
        attrs = json.loads(p[1])
        if attrs['count'] > 0 or get_domain(fb_type) == "fb:type":
            ret.add(fb_type)
    return ret

def check_valid_type(type):
    global valid_types
    domain = get_domain(type)
    # if domain in ['fb:type', 'fb:common']:
        # return True
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
            if name in ['fb:type.property.master_property', 'fb:type.property.expected_type', 'fb:type.property.reverse_property']:
                continue
            if name in self.attrs:
                if not check_compatiable(name, attrs[name], self.attrs[name]):
                    print 'conflict ', self.uri, name, self.attrs[name], attrs[name]
                # assert check_compatiable(name, attrs[name], self.attrs[name])
            else:
                if name not in ['fb:common.topic.description', 'fb:freebase.property_hints.inverse_description', 'fb:freebase.property_hints.enumeration']:
                    print 'add ', self.uri, name, atrs[name]
                self.attrs[name] = attrs[name]

    def check_complete(self):
        assert self.attrs['fb:type.property.schema']
        assert self.attrs['count'] <= 20 or 'fb:type.property.expected_type' in self.attrs
        if 'fb:type.property.expected_type' in self.attrs:
            flag =  check_valid_type(self.attrs['fb:type.property.expected_type'])
            if not flag:
                return False
                print self.uri, self.attrs['count'], self.attrs['fb:type.property.expected_type']
        return True

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
            if name == "fb:type.property.reverse_property" and get_domain(value) == "fb:m":
                print "delete attr %s fb:type.property.reverse_property %s" %(property_uri, value)
                continue
            fb_property.set_attr(name, value)

            
        p_map[property_uri] = fb_property
    return p_map

def check_complete(property_map):
    error_uris = []
    for uri, fb_property in property_map.iteritems():
        if not fb_property.check_complete():
            error_uris.append(uri)
    for uri in error_uris:
        print "drop at check_complete: %s" %uri
        property_map.pop(uri)

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
    print "complement cnt = %d" %cnt

def check_expected_type(property_map):
    error_uris = []
    for uri, fb_property in property_map.iteritems():
        if not "fb:type.property.expected_type" in fb_property.attrs:
            print "miss expected_type: %s" %(uri) 
            error_uris.append(uri)
    for uri in error_uris:
        property_map.pop(uri)

def check_reverse_property(property_map):
    schema = 'fb:type.property.schema'
    expected = "fb:type.property.expected_type"
    for uri, fb_property in property_map.iteritems():
        if "fb:type.property.reverse_property" in fb_property.attrs:
            other_uri = fb_property.attrs['fb:type.property.reverse_property']
            if not other_uri in property_map:
                print "miss reverse property", uri, other_uri
            else:
                other = property_map[other_uri]
                assert fb_property.attrs[schema] == other.attrs[expected]
                assert fb_property.attrs[expected] == other.attrs[schema]

            # other = property_map[fb_property.attrs['fb:type.property.reverse_property']]

def write_json_map(map, outpath):
    f = file(outpath, 'w')
    for name in sorted(map.keys()):
        value = map[name]
        f.write(name + "\t" + json.dumps(value.attrs) + "\n")
    f.close()


if __name__ == "__main__":
    data_dir = os.path.join(result_dir, 'freebase_merged')
    
    
    type_attrs_path = os.path.join(data_dir, 'type_attrs.json')
    valid_types = load_valid_types(type_attrs_path)

    attrs_path = os.path.join(data_dir, 'property_attrs.json')
    property_map = init_property(attrs_path)

    print len(property_map)
    check_complete(property_map)
    print len(property_map)

    old_attrs_path = os.path.join(result_dir, 'old_freebase/queried_property_attrs.json')    
    complement(property_map, old_attrs_path)
    
    

    check_expected_type(property_map)
    print len(property_map)

    check_reverse_property(property_map)

    write_json_map(property_map, os.path.join(result_dir, 'final_property_attrs.json'))
