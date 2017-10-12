#encoding: utf-8
from ...rel_extraction.util import load_name2baike, load_bk_static_info
from ...IOUtil import rel_ext_dir, doc_dir, Print, nb_lines_of, result_dir
from ..structure import BaikeEntity, FBRelation, LinkedTriple
from ..util import load_predicate_map
import os
import json
from ...schema.schema import Schema
from tqdm import tqdm
import re

class SeparatedLinker:
    def __init__(self, entity_linker, rel_linker):
        self.entity_linker = entity_linker
        self.rel_linker = rel_linker
        self.schema = Schema()
        self.schema.init()

    def link(self, ltp_result, triple, page_info):
        e1_entities = self.entity_linker.link(ltp_result, triple.e1, page_info)
        e2_entities = self.entity_linker.link(ltp_result, triple.e2, page_info)

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

class TopPopEntityLinker:
    def __init__(self, static_info_path):
        self.bk_info_map = load_bk_static_info(filepath = static_info_path)
        self.name2bk = load_name2baike(filepath = os.path.join(rel_ext_dir, 'baike_names.tsv'))

    def link(self, ltp_result, str_entity):
        name = ltp_result.text(str_entity.st, str_entity.ed)
        baike_urls = self.name2bk.get(name, [])
        baike_entities = []

        
        for bk_url in baike_urls:
            bk_info = self.bk_info_map[bk_url]
            baike_entities.append(BaikeEntity(str_entity, bk_url, bk_info.pop, bk_info.types))

        if len(baike_entities) == 0:
            return []

        baike_entities.sort(key = lambda x: x.pop, reverse = True)
        total_score = 0.000
        for e in baike_entities:
            total_score += e.pop

        top_entity = baike_entities[0]
        if total_score > 0:
            top_entity.pop /= (total_score)
        return [top_entity]

def load_summary_and_infobox(summary_path, infobox_path):
    Print("load summary from [%s]" %summary_path)
    summary_map = {}
    for line in tqdm(file(summary_path, 'r'), total = nb_lines_of(summary_path)):
        p = line.split('\t')
        key = p[0]
        summary_map[key] = json.loads(p[1])['summary'].encode('utf-8')

    Print('add infobox value to summary, path is [%s]' %infobox_path)
    for line in tqdm(file(infobox_path), total = nb_lines_of(infobox_path)):
        p = line.split('\t')
        key = p[0]
        info_values = list()
        info = json.loads(p[1])['info']
        for value_list in info.values():
            for value in value_list:
                info_values.append(value)
        if len(info_values) == 0:
            continue
        text = u"。" + u"#".join(info_values)
        text = text.encode('utf-8')
        if not key in summary_map:
            summary_map[key] = text
        else:
            summary_map[key] = summary_map[key] + text

    return summary_map


def summary_related_score(summary, page_info):
    cnt = len(re.findall(page_info.ename, summary))
    score = cnt * 2
    if cnt >= 1:
        score += 50
    return score



class TopRelatedEntityLinker:
    def __init__(self, static_info_path):
        self.bk_info_map = load_bk_static_info(filepath = static_info_path)
        self.name2bk = load_name2baike(filepath = os.path.join(rel_ext_dir, 'baike_names.tsv'))
        self.summary_map = load_summary_and_infobox(summary_path = os.path.join(rel_ext_dir, 'baike_summary.json'),
                                                infobox_path = os.path.join(result_dir, '360/360_entity_info_processed.json'))

    def link(self, ltp_result, str_entity, page_info):
        name = ltp_result.text(str_entity.st, str_entity.ed)
        baike_urls = self.name2bk.get(name, [])
        baike_entities = []

        
        for bk_url in baike_urls:
            bk_info = self.bk_info_map[bk_url]
            pop = bk_info.pop
            summary = self.summary_map.get(bk_url, "")
            summary_score = summary_related_score(summary, page_info)
            baike_entities.append(BaikeEntity(str_entity, bk_url, bk_info.pop + summary_score, bk_info.types))

        if len(baike_entities) == 0:
            return []

        baike_entities.sort(key = lambda x: x.pop, reverse = True)
        total_score = 0.000
        for e in baike_entities:
            total_score += e.pop

        top_entity = baike_entities[0]
        if total_score > 0:
            top_entity.pop /= (total_score)
        return [top_entity]




class MatchRelLinker:
    def __init__(self):
        self.predicate_map = load_predicate_map(extra_path = os.path.join(doc_dir, 'human_add_predicate_map.json'))

    def link(self, ltp_result, rel):
        predicate = ltp_result.text(rel.st, rel.ed)
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
            match_ratio = len(predicate.decode('utf-8')) / float(len(infobox_pred.decode('utf-8')))
            if match_ratio < 0.5:
                continue
            probs = self.predicate_map[infobox_pred]
            for fb_prop in probs:
                prob = probs[fb_prop] * match_ratio
                if prob < 0.1:
                    continue
                if mapped_probs.get(fb_prop, 0) < prob:
                    mapped_probs[fb_prop] = prob
        return mapped_probs

if __name__ == "__main__":
    rel_linker = MatchRelLinker()
    probs = rel_linker.link_partial_match_predicate(u'出生时')
    for fb_prop in probs:
        print fb_prop, probs[fb_prop]




    

