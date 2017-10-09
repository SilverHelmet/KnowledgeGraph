#encoding: utf-8
import os
from ..IOUtil import result_dir, rel_ext_dir
from ..rel_extraction.util import load_bk_entity_pop, load_bk_types
from ..rel_extraction.parse_baike_entity import split_sentences
from .structure import *
from .dataset import load_name2bk
from .util import load_predicate_map
from ..schema.schema import Schema
from .ltp import LTP
from entity.naive_ner import NaiveNer
from dependency.relation_extractors import RelTagExtractor
from .linkers import SeparatedLinker, PopularityEntityLinker, MatchRelLinker
from .mst import perform_MST, Edge
    
def parse_str_relations_by_ltp_tag(ltr_result, entity_pool):
    str_relations = []
    for idx, tag in enumerate(ltp_result.tags):
        if tag == 'v' or tag == 'n':
            str_relations.append(StrRelation(idx, idx + 1))
    return str_relations
        

def fill_entity_pool(length, str_entites):
    pool = [False] * length
    for entity in str_entites:
        st = entity.st
        ed = entity.ed
        for i in range(st, ed):
            pool[i] = True
    return pool

class SimpleLTPExtractor:
    def __init__(self, ner, rel_extractor, linker):
        self.ltp = LTP(None)
        self.ner = ner
        self.rel_extractor = rel_extractor
        self.linker = linker
        # self.ner = NaiveNer()
        # self.rel_extractor = RelTagRelation()
        # entity_linker = PopularityEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
        # rel_linker = MatchRelLinker()
        # self.linker = SeparatedLinker(entity_linker, rel_linker)


    def parse_triples(self, ltp_result, str_entites, entity_pool):
        triples = []
        for e1 in str_entites:
            for e2 in str_entites:
                if e1.st == e2.st:
                    continue
                rels = self.rel_extractor.parse_relation(ltp_result, e1, e2 , entity_pool)
                for str_rel in rels:
                    triples.append(Triple(e1, str_rel, e2))
        return triples

    def parse_sentence(self, sentence, page_info):
        print "sentense is:" sentence 
        if type(sentence) is unicode:
            sentence = sentence.encode('utf-8')
        ltp_result = self.ltp.parse(sentence)

        str_entites = self.ner.recognize(sentence, ltp_result, page_info)
        str_entites = [ StrEntity(st, ed) for st, ed in str_entites]
        str_entites.append(StrEntity(9, 11))

        entity_pool = fill_entity_pool(ltp_result.length, str_entites)

        
        triples = self.parse_triples(ltp_result, str_entites, entity_pool)

        for triple in triples:
            subj = ltp_result.text(triple.e1.st, triple.e1.ed)
            rel = ltp_result.text(triple.rel.st, triple.rel.ed)
            obj = ltp_result.text(triple.e2.st, triple.e2.ed)

        linked_triples = []
        for triple in triples:
            linked_triples.extend(self.linker.link(ltp_result, triple, page_info))        

        mst_triples = mst_select_triple(linked_triples)
        return mst_triples, ltp_result


def mst_select_triple(linked_triples):
    edges = []
    for idx, l_triple in enumerate(linked_triples):
        u = l_triple.baike_subj.st
        v = l_triple.baike_obj.st
        w = l_triple.score()
        edges.append(Edge(u, v, w, idx))
    mst_edges = perform_MST(edges)

    mst_triples = [linked_triples[edge.eid] for edge in mst_edges]
    return mst_triples

if __name__ == "__main__":
    s = u'刘德华出生于1966年，是知名演员、歌手。'
    s = '刘德华，1999年，周杰伦参演电影了《投奔怒海》'
    # s = u'《青花瓷》是方文山作词，周杰伦作曲并演唱的歌曲，收录于2007年11月2日周杰伦制作发行音乐专辑《我很忙》中。'

    ner = NaiveNer()    
    rel_extractor = RelTagExtractor()
    entity_linker = PopularityEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    rel_linker = MatchRelLinker()
    linker = SeparatedLinker(entity_linker, rel_linker)

    ltp_extractor = SimpleLTPExtractor(ner, rel_extractor, linker)

    triples, ltp_result = ltp_extractor.parse_sentence(s, None)

    for triple in triples:
        print triple.info(ltp_result)


    # knowledges = extractor.parse_sentence(s)
    # for kl in knowledges:
    #     print kl

    
        
    