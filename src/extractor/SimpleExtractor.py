#encoding: utf-8
import jieba
import jieba.posseg as pseg
import os
from ..IOUtil import result_dir
from ..rel_extraction.util import load_bk_entity_pop, load_bk_types
from ..rel_extraction.parse_baike_entity import split_sentences
from .structure import *
from .dataset import load_name2bk
from .util import load_predicate_map
from ..schema.schema import Schema


entity_flags = set(['baike', 'ns', 'nt', 'nr', 'nz', 'nrt', 'nrfg'])
rel_flags = set(['v', 'vd', 'vg', 'vi', 'vn', 'vq'])
time_flags = set([''])
class SimpleExtractor:
    def __init__(self):
        self.sentence_splitter = split_sentences
        self.init()
    
    def init(self):
        self.schema = Schema()
        self.schema.init()

        self.name2baike = load_name2bk()
        self.baike_pop_map = load_bk_entity_pop()
        self.baike_type_map = load_bk_types()
        self.predicate_map = load_predicate_map()

    def parse(self, paragraph):
        if type(paragraph) is str:
            paragraph = paragraph.decode('utf-8')

        sentences = self.sentence_splitter(paragraph)
        ret = {}
        for sentence in sentences:
            result = self.parse_sentence(sentence)
            if result:
                ret[sentence] = ret

    def parse_str_entity(self, words, flags):
        global entity_flags
        str_entites = []
        st = 0
        length = len(words)
        while st < length:
            ed = st
            while ed < length and flags[ed] in entity_flags:
                ed += 1
            if ed > st:
                str_entites.append(StrEntity(st, ed))
            st = ed + 1
        return str_entites

    def link_to_baike(self, words, flags, str_entites):
        baike_entities = []
        for str_entity in str_entites:
            st = str_entity.st
            ed = str_entity.ed
            name = "".join(words[st:ed])
            baike_urls = self.name2baike.get(name, [])
            for bk_url in baike_urls:
                baike_entities.append(BaikeEntity(str_entity, bk_url, self.baike_pop_map[bk_url]))
        return baike_entities

    def parse_str_relatiaons(self, words, flags):
        global rel_flags
        st = 0
        length = len(flags)
        str_rels = []
        while st < length:
            if flags[st] == 'n':
                str_rels.append(StrRelation(st, st+1))
                st += 1
            ed = st
            while ed < length and flags[ed] in rel_flags:
                ed += 1
            if ed > st:
                str_rels.append(StrRelation(st, ed))
                st = ed
            else:
                st = ed + 1
        return str_rels

    def link_to_fb_prop(self, words, flags, str_rels):
        fb_rels = []
        for str_rel in str_rels:       
            st, ed = str_rel.st, str_rel.ed
            rel = "".join(words[st:ed])
            rel_prop_probs = {}
            for infobox_name in self.predicate_map:
                if rel.find(infobox_name) == -1:
                    continue
                fb_prop_probs = self.predicate_map[infobox_name]
                for fb_prop, prob in fb_prop_probs.iteritems():
                    if not fb_prop in rel_prop_probs:
                        rel_prop_probs[fb_prop] = 0
                    rel_prop_probs[fb_prop] += prob
            for fb_prop, prob in rel_prop_probs.iteritems():
                fb_rels.append(FBRelation(str_rel, fb_prop, prob))
        return fb_rels

    def parse_entity_relations(self, words, flags, baike_entities, fb_relations):
        spos = []
        for e1 in baike_entities:
            e1_types = self.baike_type_map[e1.baike_url]
            for e2 in baike_entities:
                if e1.st == e2.st and e1.ed == e2.ed:
                    continue
                e2_types = self.baike_type_map[e2.baike_url]
                for fb_rel in fb_relations:
                    if not self.schema.check_spo(e1_types, fb_rel.fb_prop, e2_types):
                        continue
                    score = fb_rel.prob
                    spos.append(SPO(e1, fb_rel, e2, score, 'entity'))
        return spos



    def parse_sentence(self, sentence):
        res = pseg.cut(sentence)
        words = []
        flags = []
        for word, flag in res:
            words.append(word)
            flags.append(flag)

        str_entites = self.parse_str_entity(words, flags)
        baike_entities = self.link_to_baike(words, flags, str_entites)

        # time_entities = self.parse_time_entity(words, flags)

        str_relations = self.parse_str_relatiaons(words, flags)
        fb_relations = self.link_to_fb_prop(words, flags, str_relations)


        spos = []
        spos.extend(self.parse_entity_relations(words, flags, baike_entities, fb_relations))
        
        if len(spos) == 0:
            return None
       
        spos.sort(reverse = True)
        spo = spos[0]
        knowledge = Knowledge.from_spo(spo, words)
        return [knowledge]


        
        
            


if __name__ == "__main__":
    jieba.add_word("投奔怒海", freq = 5, tag = "baike")
    s = u'刘德华出生于1966年，是知名演员、歌手。'
    s = u'刘德华，1999年，参演电影了《投奔怒海》'
    res = pseg.cut(s)
    words = []
    flags = []
    for word, flag in res:
        words.append(word)
        flags.append(flag)

    extractor = SimpleExtractor()
    knowledges = extractor.parse_sentence(s)
    for kl in knowledges:
        print kl

    
        
    