#encoding: utf-8
from ..structure import BaikeEntity, FBRelation, LinkedTriple, StrEntity
from ..util import  get_domain
from src.rel_extraction.extract_baike_names import person_extra_names
import os
import json
from src.extractor.resource import Resource
from src.IOUtil import Print
from tqdm import tqdm
import re

class SeparatedLinker:
    def __init__(self, entity_linker, rel_linker):
        self.entity_linker = entity_linker
        self.rel_linker = rel_linker
        self.schema = Resource.get_singleton().get_schema()

    def link(self, ltp_result, triple, page_info):
        e1_entities = self.entity_linker.link(ltp_result, triple.e1, page_info)
        e2_entities = self.entity_linker.link(ltp_result, triple.e2, page_info)

        fb_rels = self.rel_linker.link(ltp_result, triple.str_rel)
    
        linked_triples = []
        for e1 in e1_entities:
            for e2 in e2_entities:
                for rel in fb_rels:
                    ltriple = LinkedTriple(e1, rel, e2)
                    if ltriple.check_type(self.schema):
                        linked_triples.append(ltriple)
        if len(linked_triples) == 0:
            triple = LinkedTriple(e1, FBRelation.null_relation(triple.str_rel), e2)
            linked_triples.append(triple)
        return linked_triples

    def only_link_rel(self, ltp_result, half_linked_triple, page_info):
        fb_rels = self.rel_linker.link(ltp_result, half_linked_triple.str_rel)
    
        linked_triples = []
        e1 = half_linked_triple.baike_subj
        e2 = half_linked_triple.baike_obj
        for rel in fb_rels:
            ltriple = LinkedTriple(e1, rel, e2)
            if self.schema.check_spo(ltriple.baike_subj.types, ltriple.fb_rel.fb_prop, ltriple.baike_obj.types, True):
                ltriple.fb_rel.prob += 0.01
                linked_triples.append(ltriple)

            ltriple = LinkedTriple(e2, rel, e1)
            if self.schema.check_spo(ltriple.baike_subj.types, ltriple.fb_rel.fb_prop, ltriple.baike_obj.types, True):
                linked_triples.append(ltriple)
        
        if len(linked_triples) == 0:
            triple = LinkedTriple(e1, FBRelation.null_relation(half_linked_triple.str_rel), e2)
            linked_triples.append(triple)
        return linked_triples

# class PopularityEntityLinker:
#     def __init__(self, static_info_path):
#         self.bk_info_map = load_bk_static_info(filepath = static_info_path)
#         self.name2bk = load_name2baike(filepath = os.path.join(rel_ext_dir, 'baike_names.tsv'))

#     def link(self, ltp_result, str_entity):
#         name = ltp_result.text(str_entity.st, str_entity.ed).decode('utf-8')
#         baike_urls = self.name2bk.get(name, [])
#         baike_entities = []

#         for bk_url in baike_urls:
#             bk_info = self.bk_info_map[bk_url]
#             baike_entities.append(BaikeEntity(str_entity, bk_url, bk_info.pop, bk_info.types))
#         return baike_entities

# class TopPopEntityLinker:
#     def __init__(self, static_info_path):
#         self.bk_info_map = load_bk_static_info(filepath = static_info_path)
#         self.name2bk = load_name2baike(filepath = os.path.join(rel_ext_dir, 'baike_names.tsv'))

#     def link(self, ltp_result, str_entity):
#         name = ltp_result.text(str_entity.st, str_entity.ed)
#         baike_urls = self.name2bk.get(name, [])
#         baike_entities = []

        
#         for bk_url in baike_urls:
#             bk_info = self.bk_info_map[bk_url]
#             baike_entities.append(BaikeEntity(str_entity, bk_url, bk_info.pop, bk_info.types))

#         if len(baike_entities) == 0:
#             return []

#         baike_entities.sort(key = lambda x: x.pop, reverse = True)
#         total_score = 0.000
#         for e in baike_entities:
#             total_score += e.pop

#         top_entity = baike_entities[0]
#         if total_score > 0:
#             top_entity.pop /= (total_score)
#         return [top_entity]

def summary_related_score(summary, page_info):
    max_cnt = 0
    for name in page_info.names:
        # flag = True
        # for summary_name in summary_names:
        #     if summary_name.find(name) != -1:
        #         flag = False
        # if not flag:
        #     continue
        if summary.find(name) != -1:
            max_cnt = 1
            break
        # max_cnt = max(max_cnt, len(re.findall(name, summary)))

    
    score = max_cnt * 2
    if max_cnt >= 1:
        score += 60
    return score

def page_type_related_score(etype, types, page_info):               
    # if etype in ['Ns']:
    #     return 0
    if 'fb:location.location' in types:
        return 0
    domains = page_info.domains
    related_domains = set()
    for fb_type in types:
        domain = get_domain(fb_type)
        if domain in domains and \
            domain not in ["fb:organization", "fb:people", "fb:location" ,'fb:award']:
            related_domains.add(domain)

    if len(related_domains) > 0:
        if 'fb:sports' in related_domains:
            return min(len(related_domains) * 10 + 20, 40)
        else:
            return 30
    else:
        return 0

etype_match_map = {
    'Nh': ['fb:people.person', 'fb:fictional_universe.fictional_character', 'fb:fictional_universe.person_in_fiction'],
    'Ns': ['fb:location.location', 'fb:fictional_universe.fictional_setting'],
    "Ni": ['fb:organization.organization', 'fb:fictional_universe.fictional_organization', 'fb:sports.sports_team'],
    "Nb": ['fb:film.film', 'fb:book.written_work', 'fb:tv.tv_program', 'fb:cvg.computer_videogame', 'fb:cvg.game_series', 'fb:music.recording', "fb:music.album"],
    "Nz": [],
    "Nf": [],
    "Nm": [],
    "Ns-ATT": [],
    'Nt': [],
}

def entity_type_related_score(etype, types):
    global etype_match_map
    
    if etype != "Nb":
        matched_types = etype_match_map['Nb']
        for bk_type in types:
            if bk_type in matched_types:
                return -20
    if "fb:location:location" in types and etype != "Ns":
        return -20

    matched_types = etype_match_map[etype]
    for bk_type in types:
        if bk_type in matched_types:
            return 30
    return 0



# class TopRelatedEntityLinker:
#     def __init__(self, static_info_path, lowercase = False):
#         self.bk_info_map = load_bk_static_info(filepath = static_info_path)
#         self.name2bk = load_name2baike(filepath = os.path.join(rel_ext_dir, 'baike_names.tsv'))
#         self.url2name = load
#         if lowercase:
#             self.lower_name2bk = gen_lowercase_name(self.name2bk)
#         self.summary_map = load_summary_and_infobox(summary_path = os.path.join(rel_ext_dir, 'baike_summary.json'),
#                                                 infobox_path = os.path.join(result_dir, '360/360_entity_info_processed.json'),
#                                                 lowercase = False)

#         self.lowercase = lowercase

    

#     def link(self, ltp_result, str_entity, page_info):
#         name = ltp_result.text(str_entity.st, str_entity.ed)

#         baike_urls = self.name2bk.get(name, [])
#         if len(baike_urls) == 0 and self.lowercase:
#             baike_urls = self.lower_name2bk.get(name.lower(), [])

#         baike_entities = []

#         for bk_url in baike_urls:
#             bk_info = self.bk_info_map[bk_url]
#             pop = bk_info.pop
#             summary = self.summary_map.get(bk_url, "")
#             summary_score = summary_related_score(summary, page_info)
#             baike_entities.append(BaikeEntity(str_entity, bk_url, bk_info.pop + summary_score, bk_info.types))

#         if len(baike_entities) == 0:
#             return []

#         baike_entities.sort(key = lambda x: x.pop, reverse = True)
#         total_score = 0.000
#         for e in baike_entities:
#             total_score += e.pop

#         top_entity = baike_entities[0]
#         if total_score > 0:
#             top_entity.pop /= (total_score)
#         return [top_entity]

class PageMemory:
    def __init__(self):
        self.link_map = {}
        # self.url2names = Resource.get_singleton().get_url2names()

    def refresh(self):
        self.link_map.clear()

    # def find_link(self, text):
    #     return self.link_map.get(text, None)

    def add(self, ltp_result, str_entity, baike_entity):
        text = ltp_result.text(str_entity.st, str_entity.ed)
        self.link_map[text] = baike_entity
        etype = str_entity.etype
        for name in str_entity.extra_names:
            self.add_map(name, etype, baike_entity)
        # if baike_entity:
        #     for name in self.url2names[baike_entity.baike_url]:
        #         self.link_map[name] = baike_entity
        if str_entity.etype == 'Nh' or str_entity.etype == 'Nf':
            self.add_person(text, str_entity.etype, baike_entity)
        # if str_entity.etype == 'Ni':
            # self.add_organzition(ltp_result, str_entity, baike_entity)

    def add_person(self, text, etype, baike_entity):
        person_names = person_extra_names(text)
        for name in person_names:
            if type(name) is unicode:
                name = name.encode('utf-8')
            self.add_map(name, etype, baike_entity)

    def add_organzition(self, ltp_result, str_entity, baike_entity): 
        if baike_entity is None:
            return
        st = str_entity.st
        for ed in range(st + 1, str_entity.ed):
            text = ltp_result.text(st, ed)
            self.add_map(text, str_entity.etype, baike_entity)

    def add_map(self, text, etype, baike_entity):
        # self.link_map[text + "#" + etype] = baike_entity
        self.link_map[text] = baike_entity

    def had_link(self, name, etype):
        # text = name + '#' + etype
        # return text in self.link_map
        return name in self.link_map

    def find_link(self, name, etype):
        # text = name + '#' + etype
        # return self.link_map[text]
        return self.link_map[name]

def top_cnt_keys(keys_cnt):
    if len(keys_cnt) == 0:
        return [], {}
    max_cnt = reduce(max, keys_cnt.values())
    top_keys = []
    mapping_scores = {}
    for key in keys_cnt:
        if keys_cnt[key] >= max_cnt - 1:
            top_keys.append(key)
            mapping_scores[key] = 15 * (1 - max_cnt + keys_cnt[key])
    return top_keys, mapping_scores

class PageMemoryEntityLinker:
    def __init__(self, lowercase = True):
        resource = Resource.get_singleton()
        resource.load_baike_names(lowercase = lowercase)
        self.bk_info_map = resource.get_baike_info()
        self.name2bk = resource.get_name2bk(lowercase)
        self.url2names = resource.get_url2names(lowercase)
        self.team_suffix_dict = resource.get_team_suffix_dict()
        if lowercase:
            self.lower_name2bk = resource.get_lower_name2bk()
        self.summary_map = resource.get_summary_with_infobox()

        self.location_dict = resource.get_location_dict()

        self.lowercase = lowercase
        self.memory = PageMemory()


        self.adjust_pop_by_summary()

    def adjust_pop_by_summary(self):
        Print('adjust entity popularity according to its summary length')
        for bk_url in tqdm(self.bk_info_map, total = len(self.bk_info_map)):
            summary_length = len(self.summary_map.get(bk_url, "")) / 100
            self.bk_info_map[bk_url].pop += min(summary_length * 2, 10)


    def get_candidate_urls(self, names):
        baike_urls_cnt = {}
        for name, score in names: 
            baike_urls = self.name2bk.get(name, [])            
            for url in baike_urls:
                if url not in baike_urls_cnt:
                    baike_urls_cnt[url] = 0
                baike_urls_cnt[url] += score

            team_baike_urls = self.team_suffix_dict.search_name(name)
            for url in team_baike_urls:
                if url not in baike_urls_cnt:
                    baike_urls_cnt[url] = 0
                baike_urls_cnt[url] += score + 1
        if len(baike_urls_cnt) != 0:
            return top_cnt_keys(baike_urls_cnt)
        
        if not self.lowercase:
            return [], {}

        for name, score in names:
            name = name.lower()
            baike_urls = self.lower_name2bk.get(name, [])
            for url in baike_urls:
                if url not in baike_urls_cnt:
                    baike_urls_cnt[url] = 0
                baike_urls_cnt[url] += score
        return top_cnt_keys(baike_urls_cnt)
            
    def check_is_location(self, ltp_result, str_entity):
        st = str_entity.st
        ed =str_entity.ed
        if ed - st == 1:
            return False
        for i in range(st, ed):
            if not ltp_result.words[i] in self.location_dict:
                return False
        return True

    def link(self, ltp_result, str_entity, page_info):
        if str_entity.etype == "Nt":
            return [BaikeEntity(str_entity, None, 1, ['fb:type.datetime'])]

        name = ltp_result.text(str_entity.st, str_entity.ed)

        if self.check_is_location(ltp_result, str_entity):
            name = ltp_result.text(str_entity.ed - 1, str_entity.ed)
            str_entity.etype = "Ns"

        if self.memory.had_link(name, str_entity.etype):
            baike_entity = self.memory.find_link(name, str_entity.etype)
            if baike_entity is None:
                return []
            else:
                new_bk_entity = BaikeEntity(str_entity, baike_entity.baike_url, baike_entity.pop, baike_entity.types) 
                return [new_bk_entity]

        names = [(name, 2)]
        for extra_name in str_entity.extra_names:
            names.append((extra_name, 1))


        # baike_urls = self.name2bk.get(name, [])
        # if len(baike_urls) == 0 and self.lowercase:
        #     baike_urls = self.lower_name2bk.get(name.lower(), [])

        baike_urls, mapping_scores = self.get_candidate_urls(names)
        baike_entities = []
        for bk_url in baike_urls:
            # if not bk_url in self.bk_info_map:
            #     continue
            bk_info = self.bk_info_map[bk_url]
            pop = bk_info.pop
            # url_names = self.url2names[bk_url]
            summary = self.summary_map.get(bk_url, "")
            mapping_score = mapping_scores[bk_url]
            if page_info.url == bk_url and name == page_info.ename:
                summary_score = 200
            else:
                # summary_score = summary_related_score(summary, page_info, url_names)
                summary_score = summary_related_score(summary, page_info)
            page_type_score = page_type_related_score(str_entity.etype, bk_info.types, page_info)
            entity_type_score = entity_type_related_score(str_entity.etype, bk_info.types)
            
            
            # if True:
            #     print name, str_entity.etype, bk_url, pop, summary_score, page_type_score, entity_type_score, mapping_score
            baike_entities.append(BaikeEntity(str_entity, bk_url, bk_info.pop + summary_score + page_type_score + entity_type_score + mapping_score, bk_info.types))


        if len(baike_entities) == 0:
            return []

        baike_entities.sort(key = lambda x: x.pop, reverse = True)
        total_score = 0.000
        for e in baike_entities:
            total_score += max(e.pop, 0)

        top_entity = baike_entities[0]
        if total_score > 0:
            top_entity.pop /= (total_score)
        # self.memory.add(ltp_result, str_entity, top_entity)
        return [top_entity]

    
    def start_new_page(self, baike_url):
        self.memory.refresh()
        self.team_suffix_dict.refresh()
        self.team_suffix_dict.meet_url(baike_url)
        types = self.bk_info_map[baike_url].types
        if 'fb:people.person' in types:
            baike_entity = BaikeEntity(StrEntity(0, 0, "Nh"), baike_url, 200, types)
            names = self.url2names[baike_url]
            for name in names:
                self.memory.add_map(name, "Nh", baike_entity)
                self.memory.add_person(name, "Nh", baike_entity)
                self.memory.add_map(name, "Nf", baike_entity)
                self.memory.add_person(name, "Nf", baike_entity)

    def add_sentence(self, ltp_result, str_entities, baike_entities):
        for i in range(len(str_entities)):
            str_entity = str_entities[i]
            baike_entity = baike_entities[i]
            self.memory.add(ltp_result, str_entity, baike_entity)
            if baike_entity:
                self.team_suffix_dict.meet_url(baike_entity.baike_url)

            
class MatchRelLinker:
    def __init__(self):
        resource = Resource.get_singleton()
        self.predicate_map = resource.get_predicate_map()

    def link(self, ltp_result, rel):
        predicate = ltp_result.text(rel.st, rel.ed)
        fb_rels = []
        if predicate in self.predicate_map:
            probs = self.predicate_map[predicate]
        else:
            probs = []
        # else:
        #     probs = self.link_partial_match_predicate(predicate)
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
    # rel_linker = MatchRelLinker()
    # probs = rel_linker.link_partial_match_predicate(u'出版')

    resource = Resource.get_singleton()
    predicate_map = resource.get_predicate_map()

    probs = predicate_map['生于']
    for prop in probs:
        print prop, probs[prop]




    

