#encode:utf-8
from ..fb_process.extract_util import get_domain
from ..IOUtil import doc_dir, result_dir
import sys
import os
import json

class Schema:
    def __init__(self):
        pass
    
    def init(self, init_type_neighbor = False):
        self.datetime_properties = None
        self.property_attrs = load_property_attrs()
        self.type_attrs = load_type_attrs()
        self.reverse_prop_map = self.get_reverse_property_map(self.property_attrs)

        if init_type_neighbor:
            self.type_neighbors = self.init_type_neighbor()

    # def init_type_neighbor(self):
    #     type_neighbors = {}

    #     for fb_prop in self.property_attrs:
    #         schema_type = self.schema_type(fb_prop)
    #         expected_type = self.expected_type(fb_prop)

    #         if not schema_type in type_neighbors:
    #             type_neighbors[schema_type] = set()
    #         type_neighbors[schema_type].add(expected_type)

    #         if not expected_type in type_neighbors:
    #             type_neighbors[expected_type] = set()
    #         type_neighbors[expected_type].add(schema_type)

    #     return type_neighbors

    def init_type_neighbor(self):
        type_neighbors = {
            'fb:tv.tv_program': 'fb:tv.tv_series_episode',
            # 'fb:music.composition': 'fb:music.recording',
            # 'fb:music.composition': 'fb:music.album',
            'fb:sports.sports_league': 'fb:sports.sports_championship_event',
            "fb:sports.sports_league_season": "fb:sports.sports_championship_event",
            'fb:sports.sports_championship': 'fb:sports.sports_championship_event',
            'fb:award.award': 'fb:award.award_category',
            'fb:award.award_ceremony': 'fb:award.award_category',
            'fb:film.film_festival' :'fb:award.award_category',
            "fb:film.film_festival_event": 'fb:award.award_category',
            'fb:cvg.game_series': 'fb:cvg.computer_videogame',
            'fb:location.administrative_division': 'fb:location.mailing_address',
        }
        return type_neighbors

            
    
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

    def is_uniq_prop(self, fb_property):
        return get_bool(self.property_attrs[fb_property].get('fb:type.property.unique', '0'))

    def is_mediator(self, fb_type):
        if fb_type in self.type_attrs:
            return get_bool(self.type_attrs[fb_type].get('fb:freebase.type_hints.mediator', '0'))
        else:
            return False


    
    def reverse_property(self, fb_property):
        props = fb_property.split('^')
        props.reverse()
        reverse_props = []
        
        for prop in props:
            reverse_prop = self.reverse_prop_map.get(prop, None)
            if reverse_prop is None:
                return None
            reverse_props.append(reverse_prop)
        return "^".join(reverse_props)

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

    def check_in_neightbor(self, prop_type, obj_types):
        neighbors = self.type_neighbors[prop_type]
        for obj_type in obj_types:
            if obj_type in neighbors:
                return True
        return False

    def check_spo(self, subj_types, prop, obj_types, use_neighbor):
        subj_type = self.schema_type(prop)
        obj_type = self.expected_type(prop)
        
        subj_ok = subj_type in subj_types
        obj_ok = obj_type in obj_types

        if obj_type == 'fb:type.rawstring':
            obj_ok = True
        if subj_ok and obj_ok:
            return True
        else:
            if use_neighbor:
                if not obj_ok:
                    for cand_type in obj_types:
                        if self.type_neighbors.get(cand_type, "") == obj_type:
                            obj_ok = True

                if not subj_ok:
                    for cand_type in subj_types:
                        if self.type_neighbors.get(cand_type, "") == subj_type:
                            subj_ok = True
                return subj_ok and obj_ok
            return False

    def get_datetime_properties(self):
        if self.datetime_properties is None:

            self.datetime_properties = set()
            for fb_property in self.property_attrs:
                if self.expected_type(fb_property) == 'fb:type.datetime':
                    self.datetime_properties.add(fb_property)
        return self.datetime_properties

    

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
        if line.startswith("#"):
            continue
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
    # keys = set()

    schema = Schema()
    schema.init()
    subj = [u'fb:media_common.netflix_title', u'fb:award.award_winning_work', u'fb:tv.tv_program', u'fb:award.award_nominated_work']
    obj = [u'fb:people.person', u'fb:tv.tv_program_creator', u'fb:influence.influence_node', u'fb:film.producer', u'fb:award.award_nominee', u'fb:tv.tv_writer', u'fb:fictional_universe.fictional_character_creator', u'fb:music.artist', u'fb:music.composer', u'fb:tv.tv_director', u'fb:tv.tv_producer', u'fb:film.writer', u'fb:award.award_winner', u'fb:tv.tv_actor', u'fb:music.lyricist']
    prop = u'fb:tv.tv_program.program_creator'
    # print schema.check_spo(subj, prop, obj, True)
    # datetime_props = schema.datetime_property()
    # print len(datetime_props)
    # print 'fb:people.person.date_of_birth' in datetime_props