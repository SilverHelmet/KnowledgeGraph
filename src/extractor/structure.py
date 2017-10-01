
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
