#encoding: utf-8
import os
from ..IOUtil import result_dir, rel_ext_dir, data_dir, cache_dir
from src.baike_process.process_page import split_sentences
from .structure import *
from dependency.verb_title_relation_extractor import VerbRelationExtractor
from .mst import perform_MST, Edge
from src.extractor.resource import Resource
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
    def __init__(self, doc_processor, rel_extractor, linker, link_map_out = False):
        self.ltp = Resource.get_singleton().get_ltp()
        self.doc_processor = doc_processor
        self.ner = doc_processor.ner
        self.rel_extractor = rel_extractor 
        self.linker = linker
        self.title2url = Resource.get_singleton().get_title2url()
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
            name1 = ltp_result.text(e1.st, e1.ed)
            for e2 in baike_entities:
                if e1.st == e2.st:
                    continue
                name2 = ltp_result.text(e2.st, e2.ed)
                if name1 == name2:
                    continue
                rels = self.rel_extractor.find_relation(ltp_result, e1, e2 , entity_pool)
                for rel_st, rel_ed in rels:
                    triples.append(HalfLinkedTriple(e1, StrRelation(rel_st, rel_ed), e2))
        return triples


    def parse_sentence(self, ltp_result, str_entites, page_info, out_link_map = None, debug = False):
        sentence = ltp_result.sentence
        if out_link_map:
            sentence_link_map = out_link_map[ltp_result.sentence]

        baike_entities = []
        link_map = {}
        
        for str_entity in str_entites:
            if out_link_map:
                baike_entity = sentence_link_map.get(ltp_result.text(str_entity.st, str_entity.ed), None)
                if baike_entity:
                    new_baike_entity = BaikeEntity(str_entity, baike_entity.baike_url, baike_entity.pop, baike_entity.types)
                    baike_entities.append(new_baike_entity)
                else:
                    baike_entities.append(None)
            else:
                baike_entity_list = self.linker.entity_linker.link(ltp_result, str_entity, page_info)
                if len(baike_entity_list) > 0:
                    baike_entity = baike_entity_list[0]
                    baike_entities.append(baike_entity)
                    link_map[ltp_result.text(str_entity.st, str_entity.ed)] = baike_entity.to_obj()
                else:
                    baike_entities.append(None)

        if debug:
            print "#str entities:", len(str_entites)
            print "#baike entities:", len(baike_entities)

        self.linker.entity_linker.add_sentence(ltp_result, str_entites, baike_entities)
        local_link_map = {}
        for i in range(len(str_entites)):
            baike_entity = baike_entities[i]
            if baike_entity is None:
                continue
            e = str_entites[i]
            local_link_map[e.st * 10000 + e.ed] = baike_entity
         
        

        rels = self.rel_extractor.find_tripple(ltp_result, str_entites)
        
        rels = [rel for rel in rels if rel[-1] != 'not_entity' and type(rel[2]) is not int ]


        half_linked_triples = []
        for e1, pred, e2, env, rel_type in rels:
            if rel_type == 'title':
                title = e1
                title_url = self.title2url[title]
                idx = ltp_result.search_token(title)
                title_str_entity = StrEntity(idx, idx + 1, 'title')
                e1 = BaikeEntity(title_str_entity, title_url, 10, 'title')
                
                e2 = local_link_map.get(e2.st * 10000 + e2.ed, None)
                env = None
                if e1 and e2:
                    half_linked_triples.append(HalfLinkedTriple(e2, pred, e1))
            else:
                e1 = local_link_map.get(e1.st * 10000 + e1.ed, None)
                e2 = local_link_map.get(e2.st * 10000 + e2.ed, None)
                if type(env) is int:
                    env = ltp_result.text(env, env+1)
                else:
                    env = None
                if e1 and e2:
                    half_linked_triples.append(HalfLinkedTriple(e1, StrRelation(pred, pred+1, env), e2))
        
        # half_linked_triples = self.parse_triples(ltp_result, baike_entities, entity_pool)
        # for half_linked_triple in half_linked_triples:
        #     subj = ltp_result.text(half_linked_triple.baike_subj.st, half_linked_triple.baike_subj.ed)
        #     obj = ltp_result.text(half_linked_triple.baike_obj.st, half_linked_triple.baike_obj.ed)
        #     rel = ltp_result.text(half_linked_triple.str_rel.st, half_linked_triple.str_rel.ed)

        linked_triples = []
        for half_linked_triple in half_linked_triples:
            linked_triples.extend(self.linker.only_link_rel(ltp_result, half_linked_triple, page_info))        

        if debug:
            print "#linked triples", len(linked_triples)

        if self.link_map_outf:
            self.link_map_outf.write('%s\t%s\n' %(sentence, json.dumps(link_map, ensure_ascii = False)))

        mst_triples = mst_select_triple(linked_triples)
        return mst_triples, ltp_result

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
    pass
    # s = u'刘德华出生于1966年，是知名演员、歌手。'
    # s = '赛后，梅西力压德国诸将，获得金球奖。'
    # s = '1996年，刘德华相继发行了《相思成灾》和《因为爱》两张国语唱片。'

    # page_info = PageInfo('刘德华')

    # from .util import load_stanford_result
    
    # base_dir = os.path.join(data_dir, '标注数据')
    # stf_results_map = load_stanford_result(os.path.join(base_dir, 'sentences.txt'), os.path.join(base_dir, 'sentences_stanf_nlp.json'))

    # # ner = NaiveNer()    
    # ner = NamedEntityReg()

    # # rel_extractor = RelTagExtractor()
    # rel_extractor = VerbRelationExtractor()

    # # entity_linker = TopPopEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    # entity_linker = TopRelatedEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))

    # rel_linker = MatchRelLinker()
    # linker = SeparatedLinker(entity_linker, rel_linker)
    # ltp_extractor = SimpleLTPExtractor(ner, rel_extractor, linker)

    # triples, ltp_result = ltp_extractor.parse_sentence(s, page_info, stf_results_map[s], True)

    # for triple in triples:
    #     print triple.info(ltp_result)


    # knowledges = extractor.parse_sentence(s)
    # for kl in knowledges:
    #     print kl

    
        
    