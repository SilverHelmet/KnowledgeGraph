from src.rel_extraction.extract_baike_names import person_extra_names

class PageInfo:
    person_types = ['fb:people.person', 'fb:fictional_universe.fictional_character', 'fb:fictional_universe.person_in_fiction']
    def __init__(self, ename, names, url, domains, types):
        self.ename = ename
        self.names = names[:]
        self.url = url
        self.domains = domains
        if PageInfo.is_person(types):
            new_names = []
            for name in names:
                extra_names = person_extra_names(name)
                new_names.extend(extra_names)
            self.names.extend(new_names)
            self.names = list(set(self.names))



    @staticmethod
    def is_person(types):
        for p_type in PageInfo.person_types:
            if p_type in types:
                return True
        return False

class StrEntity:
    def __init__(self, st, ed, etype):
        self.st = st
        self.ed = ed
        self.etype = etype
        self.extra_names = []
        self.obj = None

    def add_name(self, name):
        self.extra_names.append(name)

    def add_time_obj(self, obj):
        self.obj = obj


class BaikeEntity:
    def __init__(self, str_entity, baike_url, pop, types):
        self.st = str_entity.st
        self.ed = str_entity.ed
        self.baike_url = baike_url
        self.pop = pop
        if types is not None:
            self.types = types[:]
        else:
            self.types = None

    def to_obj(self):
        return {
            'st': self.st,
            'ed': self.ed,
            "baike_url": self.baike_url,
            'pop': self.pop,
            'types': self.types
        }

    @staticmethod
    def load_from_obj(obj):
        str_entity = StrEntity(obj['st'], obj['ed'], None)
        return BaikeEntity(str_entity, obj['baike_url'], obj['pop'], obj['types'])

class StrRelation:
    def __init__(self, st, ed, env = None):
        self.st = st
        self.ed = ed
        self.env = env

class FBRelation:
    def __init__(self, str_rel, fb_prop, prob):
        if type(str_rel) is str:
            self.str_rel = str_rel
            self.st = -1
            self.ed = -1
        else: 
            self.st = str_rel.st
            self.ed = str_rel.ed
        self.fb_prop = fb_prop
        self.prob = prob

    @staticmethod
    def null_relation(str_rel):
        return FBRelation(str_rel, 'None', 0.0001)
    

class SPO:
    def __init__(self, e1, rel, e2, score, type):
        self.e1 = e1
        self.rel = rel
        self.e2 = e2
        self.score = score
        self.type = type

    def __cmp__(self, other):
        if self.score < other.score:
            return -1
        elif self.score > other.score:
            return 1
        else:
            return 0

    def __str__(self):
        return "%s\t%s\t%s\t%f" %(self.e1.baike_url, self.rel.fb_prop, self.e2.baike_url, self.score)

class Knowledge:
    def __init__(self, subj, prop, obj, subj_url, prop_uri, obj_url, score = 0):
        self.subj = subj
        self.prop = prop
        self.obj = obj
        
        self.subj_url = subj_url
        self.prop_uri = prop_uri
        self.obj_url = obj_url

        self.score = score

    def __str__(self):
        return "%s\t%s %s\t%s" %(self.subj, self.prop, self.prop_uri, self.obj)

    def triple(self):
        return "%s\t%s\t%s" %(self.subj, self.prop, self.obj)

    def knowledge(self):
        return "%s\t%s\t%s" %(self.subj_url, self.prop_uri, self.obj_url)

    def info(self):
        return "%s:%s\t%s:%s\t%s:%s" %(self.subj, self.subj_url, self.prop, self.prop_uri, self.obj, self.obj_url)


    @staticmethod
    def from_spo(spo, words):
        args = ["".join(words[spo.e1.st:spo.e1.ed]),  "".join(words[spo.rel.st:spo.rel.ed]), 
            "".join(words[spo.e2.st:spo.e2.ed]), spo.e1.baike_url,
            spo.rel.fb_prop, spo.e2.baike_url, spo.score]
        kl = Knowledge(*args)
        return kl
    

class ChapterInfo:
    def __init__(self,baike_url, ename, chapt_title):
        self.baike_url = baike_url
        self.chapt_title = chapt_title
        self.ename = ename

class Triple:
    def __init__(self, str_e1, str_rel, str_e2):
        self.e1 = str_e1
        self.str_rel = str_rel
        self.e2 = str_e2

class HalfLinkedTriple:
    def __init__(self,baike_subj, str_rel, baike_obj):
        self.baike_subj = baike_subj
        self.str_rel = str_rel
        self.baike_obj = baike_obj       

class LinkedTriple:
    def __init__(self, baike_subj, fb_rel, baike_obj):
        self.baike_subj = baike_subj
        self.fb_rel = fb_rel
        self.baike_obj = baike_obj

    def check_type(self, schema):
        schema_type = schema.schema_type(self.fb_rel.fb_prop)
        expected_type =schema.expected_type(self.fb_rel.fb_prop)
        return schema.check_spo(self.baike_subj.types, self.fb_rel.fb_prop, self.baike_obj.types, True)
        # return schema_type in self.baike_subj.types and expected_type in self.baike_obj.types

    def score(self):
        # return (self.baike_subj.pop + self.baike_obj.pop) * self.fb_rel.prob * self. position_coef()
        # return (self.baike_subj.pop + self.baike_obj.pop) / 2.0 * self.fb_rel.prob
        return self.fb_rel.prob

    def position_coef(self):
        pos_diff = min(abs(self.baike_subj.st - self.baike_obj.ed), abs(self.baike_obj.st - self.baike_subj.ed) )
        if pos_diff < 9:
            return 1 - pos_diff / 10
        else:
            return 0.2

    def info(self, ltp_result):
        subj = ltp_result.text(self.baike_subj.st, self.baike_subj.ed)
        subj_url = self.baike_subj.baike_url
        obj = ltp_result.text(self.baike_obj.st, self.baike_obj.ed)
        obj_url = self.baike_obj.baike_url
        if self.fb_rel.st == -1:
            rel = self.fb_rel.str_rel
        else:
            rel = ltp_result.text(self.fb_rel.st, self.fb_rel.ed)
        fb_prop = self.fb_rel.fb_prop
        score = self.score()
        return  "%s:%s\t%s:%s\t%s:%s\t%f" %(subj, subj_url, rel, fb_prop, obj, obj_url, score)

    def knowledge(self):
        return "%s\t%s\t%s" %(self.baike_subj.baike_url, self.fb_rel.fb_prop, self.baike_obj.baike_url)

