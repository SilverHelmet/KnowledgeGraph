
class StrEntity:
    def __init__(self, st, ed):
        self.st = st
        self.ed = ed

class BaikeEntity:
    def __init__(self, str_entity, baike_url, pop, types):
        self.st = str_entity.st
        self.ed = str_entity.ed
        self.baike_url = baike_url
        self.pop = pop
        self.types = types

class StrRelation:
    def __init__(self, st, ed):
        self.st = st
        self.ed = ed

class FBRelation:
    def __init__(self, str_rel, fb_prop, prob):
        self.st = str_rel.st
        self.ed = str_rel.ed
        self.fb_prop = fb_prop
        self.prob = prob

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
        self.rel = str_rel
        self.e2 = str_e2

class LinkedTriple:
    def __init__(self, baike_subj, fb_rel, baike_obj):
        self.baike_subj = baike_subj
        self.fb_rel = fb_rel
        self.baike_obj = baike_obj

    def check_type(self, schema):
        schema_type = schema.schema_type(self.fb_rel.fb_prop)
        expected_type =schema.expected_type(self.fb_rel.fb_prop)
        return schema_type in self.baike_subj.types and expected_type in self.baike_obj.types

    def score(self):
        return (self.baike_subj.pop + self.baike_obj.pop) * self.fb_rel.prob * self. position_coef()

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
        rel = ltp_result.text(self.fb_rel.st, self.fb_rel.ed)
        fb_prop = self.fb_rel.fb_prop
        score = self.score()
        return  "%s:%s\t%s:%s\t%s:%s %f" %(subj, subj_url, rel, fb_prop, obj, obj_url, score)

