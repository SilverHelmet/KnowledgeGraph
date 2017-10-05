
class StrEntity:
    def __init__(self, st, ed):
        self.st = st
        self.ed = ed

class BaikeEntity:
    def __init__(self, str_entity, baike_url, pop):
        self.st = str_entity.st
        self.ed = str_entity.ed
        self.baike_url = baike_url
        self.pop = pop

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
    def __init__(self, subj, prop, obj, subj_url, prop_uri, obj_url, score = 0 ):
        self.subj = subj
        self.prop = prop
        self.obj = obj
        
        self.subj_url = subj_url
        self.prop_uri = prop_uri
        self.obj_url = obj_url

        self.score = score

    def __str__(self):
        return "%s\t%s %s\t%s" %(self.subj, self.prop, self.prop_uri, self.obj)

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



