import json
from ..extract.extract_util import get_type

class Predicate:
    def __init__(self, predicate):
        self.subj = None
        self.predicate = predicate
        self.obj = None

    def set_object(self, obj):
        if self.obj:
            assert self.obj == obj
        else:
            self.obj = obj
    
    def set_subject(self, subj):
        if self.subj:
            assert self.subj == subj
        else:
            self.subj = subj

    def check_reverse_predicate(self, other):
        assert self.subj == other.obj
        assert self.obj == other.subj


def check_properties_uri():
    filepath = 'result/old_freebase/queried_type_attrs.json'
    for line in file(filepath):
        p = line.split('\t')
        type = p[0]
        attrs = json.loads(p[1])
        properties = attrs['fb:type.type.properties']
        for property in properties:
            assert get_type(property) == type

def check_properties_schema():
    filepath = 'result/old_freebase/queried_property_attrs.json'
    predicate_map = {}
    for line in file(filepath):
        p = line.split("\t")
        predicate = p[0]
        attrs = json.loads(p[1])
        if not predicate in predicate_map:
            predicate_map[predicate] = Predicate(predicate)
        predicate = predicate_map[predicate]
        if 'fb:type.property.schema' in attrs:
            predicate.set_subject(attrs['fb:type.property.schema'][0])
        if 'fb:type.property.expected_type' in attrs:
            predicate.set_object(attrs['fb:type.property.expected_type'][0])

    for line in file(filepath):
        p = line.split('\t')
        predicate = predicate_map[p[0]]
        attrs = json.loads(p[1])
        if 'fb:type.property.reverse_property' in attrs:
            reverse_predicate = attrs['fb:type.property.reverse_property'][0]
            if reverse_predicate in predicate_map:
                reverse_predicate = predicate_map[reverse_predicate]
                predicate.check_reverse_predicate(reverse_predicate)
        if 'fb:type.property.master_property' in attrs:
            reverse_predicate = attrs['fb:type.property.master_property'][0]
            if reverse_predicate in predicate_map:
                reverse_predicate = predicate_map[reverse_predicate]
                predicate.check_reverse_predicate(reverse_predicate)
            

    

    

if __name__ == "__main__":
    # check_properties_uri()
    check_properties_schema()