from ..IOUtil import result_dir, base_dir
from ..fb_process.extract_util import get_type, encode, get_domain
from ..queryKG.query_util import get_unique_attr
from .complement_property_attr import check_compatiable, squeeze, write_json_map
import os
import json

class Type:
    def __init__(self, uri):
        self.uri = uri
        self.attrs = {}

    def set_attr(self, name, value):
        if name in self.attrs:
            assert self.attrs[name] == value
        else:
            self.attrs[name] = value

    def fusion(self, attrs, valid_types):
        for name in attrs:
            value = attrs[name]
            if name == "fb:type.type.properties":
                continue
            if name in self.attrs:
                if name in ['fb:type.object.name']:
                    continue
                if not check_compatiable(name, attrs[name], self.attrs[name]):
                    print 'conflict ', self.uri, name, self.attrs[name], attrs[name]
            else:
                if name == "fb:freebase.type_hints.included_types":
                    suc_types = []
                    for included_type in value:
                        if not included_type in valid_types:
                            print "error types", included_type
                        else:
                            suc_types.append(included_type)
                    value = suc_types
                if not name in ['fb:common.topic.description', 'fb:freebase.type_hints.included_types', 'fb:freebase.type_hints.enumeration', 'fb:freebase.type_hints.mediator']:
                    print 'add ', self.uri, name, attrs[name]
                self.attrs[name] = value

        
def init_type(filepath):
    unique_attrs = get_unique_attr()
    t_map = {}
    for line in file(filepath):
        p = line.split('\t')
        type_uri = p[0]
        attrs = json.loads(p[1])
        if attrs['count']  == 0:
            continue
        fb_type = Type(type_uri)
        for name in attrs:
            value = attrs[name]
            if name in unique_attrs:
                assert len(value) == 1
                value = value[0]
            fb_type.set_attr(name, value)
        t_map[type_uri] = fb_type
    return t_map

def complement(type_map, filepath):
    cnt = 0
    valid_types = set(type_map.keys())
    valid_types.add("fb:freebase.unit_profile")
    print "-------- complement ---------"
    for line in file(filepath):
        p = line.split('\t')
        uri = p[0]
        attrs = json.loads(p[1])
        squeeze(attrs)
        if uri in type_map:
            cnt += 1
            type_map[uri].fusion(attrs, valid_types)
    print "complement cnt = %d" %cnt
    

        

if __name__ == "__main__":
    type_attrs_path = os.path.join(result_dir, "freebase_merged/type_attrs.json")
    old_attrs_path = os.path.join(result_dir, "old_freebase/queried_type_attrs.json")

    type_map = init_type(type_attrs_path)
    complement(type_map, old_attrs_path)
    print "add manually written attrs"
    complement(type_map, os.path.join(base_dir, 'docs/human_add_prop_attr.json'))

    print len(type_map)
    write_json_map(type_map, os.path.join(result_dir, 'final_type_attrs.json'))



