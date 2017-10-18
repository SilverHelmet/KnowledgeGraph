#encoding: utf-8
import os
from ..IOUtil import result_dir, rel_ext_dir, data_dir, cache_dir
from ..rel_extraction.util import load_bk_entity_pop, load_bk_types
from ..rel_extraction.parse_baike_entity import split_sentences
from .structure import *
from .dataset import load_name2bk
from .util import load_predicate_map
from ..schema.schema import Schema
from .ltp import LTP
from entity.naive_ner import NaiveNer
from dependency.relation_extractors import RelTagExtractor
from dependency.verb_relation_simple_extractor import VerbRelationExtractor
from .entity.linkers import SeparatedLinker, MatchRelLinker, TopPopEntityLinker, TopRelatedEntityLinker
from .entity.ner import NamedEntityReg
from .mst import perform_MST, Edge
import json

    
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
    def __init__(self, ner, rel_extractor, linker, ltp, link_map_out = False):
        self.ltp = ltp
        self.ner = ner
        self.rel_extractor = rel_extractor
        self.linker = linker
        if link_map_out:
            self.link_map_outf = file(os.path.join(cache_dir, 'link_map.json'), 'w')
        else:
            self.link_map_outf = None
        # self.ner = NaiveNer()
        # self.rel_extractor = RelTagRelation()
        # entity_linker = PopularityEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
        # rel_linker = MatchRelLinker()
        # self.linker = SeparatedLinker(entity_linker, rel_linker)


    def parse_triples(self, ltp_result, baike_entities, entity_pool):
        triples = []
        for e1 in baike_entities:
            for e2 in baike_entities:
                if e1.st == e2.st:
                    continue
                rels = self.rel_extractor.find_relation(ltp_result, e1, e2 , entity_pool)
                for rel_st, rel_ed in rels:
                    triples.append(HalfLinkedTriple(e1, StrRelation(rel_st, rel_ed), e2))
        return triples


    def parse_sentence(self, sentence, page_info, stf_result, out_link_map = None, debug = False):
        ltp_result = self.ltp.parse(sentence)

        if out_link_map:
            sentence_link_map = out_link_map[sentence]

        str_entites = self.ner.recognize(sentence, ltp_result, page_info, stf_result)
        baike_entities = []
        link_map = {}
        for str_entity in str_entites:
            if out_link_map:
                baike_entity = sentence_link_map.get(ltp_result.text(str_entity.st, str_entity.ed), None)
                if baike_entity:
                    baike_entities.append(baike_entity)
            else:
                baike_entity_list = self.linker.entity_linker.link(ltp_result, str_entity, page_info)
                if len(baike_entity_list) > 0:
                    baike_entity = baike_entity_list[0]
                    baike_entities.append(baike_entity)
                    link_map[ltp_result.text(str_entity.st, str_entity.ed)] = baike_entity.to_obj()

        if debug:
            print "#str entities:", len(str_entites)
            print "#baike entities:", len(baike_entities)
        

        entity_pool = fill_entity_pool(ltp_result.length, str_entites)

        
        half_linked_triples = self.parse_triples(ltp_result, baike_entities, entity_pool)


        linked_triples = []
        for half_linked_triple in half_linked_triples:
            linked_triples.extend(self.linker.only_link_rel(ltp_result, half_linked_triple, page_info))        

        if debug:
            print "#linked triples", len(linked_triples)

        if self.link_map_outf:
            self.link_map_outf.write('%s\t%s\n' %(sentence, json.dumps(link_map, ensure_ascii = False)))

        mst_triples = mst_select_triple(linked_triples)
        return mst_triples, half_linked_triples, ltp_result

    def finish(self):
        if self.link_map_outf:
            self.link_map_outf.close()


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
    s = '赛后，梅西力压德国诸将，获得金球奖。'
    s = '1996年，刘德华相继发行了《相思成灾》和《因为爱》两张国语唱片。'

    page_info = PageInfo('刘德华')

    from .util import load_stanford_result
    
    base_dir = os.path.join(data_dir, '标注数据')
    stf_results_map = load_stanford_result(os.path.join(base_dir, 'sentences.txt'), os.path.join(base_dir, 'sentences_stanf_nlp.json'))

    # ner = NaiveNer()    
    ner = NamedEntityReg()

    # rel_extractor = RelTagExtractor()
    rel_extractor = VerbRelationExtractor()

    # entity_linker = TopPopEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    entity_linker = TopRelatedEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))

    rel_linker = MatchRelLinker()
    linker = SeparatedLinker(entity_linker, rel_linker)
    ltp_extractor = SimpleLTPExtractor(ner, rel_extractor, linker)

    triples, ltp_result = ltp_extractor.parse_sentence(s, page_info, stf_results_map[s], True)

    for triple in triples:
        print triple.info(ltp_result)


    # knowledges = extractor.parse_sentence(s)
    # for kl in knowledges:
    #     print kl

    
        
    