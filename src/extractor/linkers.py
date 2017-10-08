#encoding: utf-8
from ..rel_extraction.util import load_name2baike, load_bk_static_info
from ..IOUtil import rel_ext_dir, doc_dir
from .structure import BaikeEntity, FBRelation, LinkedTriple
from .util import load_predicate_map
import os
from ..schema.schema import Schema

class SeparatedLinker:
    def __init__(self, entity_linker, rel_linker):
        self.entity_linker = entity_linker
        self.rel_linker = rel_linker
        self.schema = Schema()
        self.schema.init()

    def link(self, ltp_result, triple, page_info = None):
        e1_entities = self.entity_linker.link(ltp_result, triple.e1)
        e2_entities = self.entity_linker.link(ltp_result, triple.e2)

        fb_rels = self.rel_linker.link(ltp_result, triple.rel)
        linked_triples = []
        for e1 in e1_entities:
            for e2 in e2_entities:
                for rel in fb_rels:
                    ltriple = LinkedTriple(e1, rel, e2)
                    if ltriple.check_type(self.schema):
                        linked_triples.append(ltriple)
                        
        return linked_triples

class PopularityEntityLinker:
    def __init__(self, static_info_path):
        self.bk_info_map = load_bk_static_info(filepath = static_info_path)
        self.name2bk = load_name2baike(filepath = os.path.join(rel_ext_dir, 'baike_names.tsv'))

    def link(self, ltp_result, str_entity):
        name = ltp_result.text(str_entity.st, str_entity.ed).decode('utf-8')
        baike_urls = self.name2bk.get(name, [])
        baike_entities = []

        for bk_url in baike_urls:
            bk_info = self.bk_info_map[bk_url]
            baike_entities.append(BaikeEntity(str_entity, bk_url, bk_info.pop, bk_info.types))
        return baike_entities

class MatchRelLinker:
    def __init__(self):
        self.predicate_map = load_predicate_map(extra_path = os.path.join(doc_dir, 'human_add_predicate_map.json'))

    def link(self, ltp_result, rel):
        predicate = ltp_result.text(rel.st, rel.ed).decode('utf-8')
        fb_rels = []
        if predicate in self.predicate_map:
            probs = self.predicate_map[predicate]
        else:
            probs = self.link_partial_match_predicate(predicate)
        for fb_prop in probs:
            fb_rels.append(FBRelation(rel, fb_prop, probs[fb_prop]))
        return fb_rels

    def link_partial_match_predicate(self, predicate):
        mapped_probs = {}
        for infobox_pred in self.predicate_map:
            if infobox_pred.find(predicate) == -1:
                continue
            match_ratio = len(predicate) / float(len(infobox_pred))
            probs = self.predicate_map[infobox_pred]
            for fb_prop in probs:
                prob = probs[fb_prop] * match_ratio
                if mapped_probs.get(fb_prop, 0) < prob:
                    mapped_probs[fb_prop] = prob
        return mapped_probs

if __name__ == "__main__":
    rel_linker = MatchRelLinker()
    probs = rel_linker.link_partial_match_predicate(u'出生时')
    for fb_prop in probs:
        print fb_prop, probs[fb_prop]




    

