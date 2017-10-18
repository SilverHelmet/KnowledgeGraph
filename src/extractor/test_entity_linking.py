#encoding: utf-8
from entity.linkers import TopRelatedEntityLinker
from .test_ner import read_data
from entity.linkers import SeparatedLinker, MatchRelLinker, TopRelatedEntityLinker, PageMemoryEntityLinker
from .entity.ner import NamedEntityReg
from ..IOUtil import data_dir, rel_ext_dir, Print
from .structure import *
from .ltp import LTP
from .util import load_stanford_result, load_important_domains, get_url_domains
from .test_extractor import load_same_linkings, load_url_map
from ..rel_extraction.util import load_url2names
import os


class EntityLinkingTestor:
    def __init__(self, ner, linker, ltp): 
        self.linker = linker
        self.ner = ner
        self.ltp = ltp

    def test(self, sentence, page_info, stf_result):
        ltp_result = self.ltp.parse(sentence)
        stf_result = stf_results_map[sentence]

        str_entites = self.ner.recognize(sentence, ltp_result, page_info, stf_result)
        # str_entites = [StrEntity(st, ed, etype) for st, ed, etype in str_entites]
        names = set()
        for str_entity in str_entites:
            names.add(ltp_result.text(str_entity.st, str_entity.ed))
            names.update(str_entity.extra_names)



        link_map = {}
        baike_entities = []
        for str_entity in str_entites:
            baike_entity = self.linker.link(ltp_result, str_entity, page_info)
            if len(baike_entity) > 0:
                baike_entity = baike_entity[0]
            else:
                baike_entity = None
            baike_entities.append(baike_entity)
            if baike_entity:
                link_map[ltp_result.text(str_entity.st, str_entity.ed)] = baike_entity.baike_url
                for extra_name in str_entity.extra_names:
                    link_map[extra_name] = baike_entity.baike_url

        self.linker.add_sentence(ltp_result, str_entites, baike_entities)

        return link_map, names

if __name__ == "__main__":
    datas_map = read_data(os.path.join(data_dir, '实体标注'), ignore_miss = True)

    ltp = LTP(None)
    ner = NamedEntityReg(ltp)    
    # entity_linker = TopRelatedEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'), lowercase = True)
    entity_linker = PageMemoryEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'), lowercase = True)

    base_dir = os.path.join(data_dir, '实体标注')
    stf_results_map = load_stanford_result(os.path.join(base_dir, 'sentences.txt'), os.path.join(base_dir, 'sentences_stanf_nlp.json'))

    testor = EntityLinkingTestor(ner, entity_linker, ltp)
    important_domains = load_important_domains()

    same_link_map = load_same_linkings()
    url_map = load_url_map()

    estimation = {
        "total": 0,
        'linking miss': 0,
        'ner miss': 0,
        'error': 0,
        'right': 0
    }

    for ename in datas_map:
        datas = datas_map[ename]
        entity_linker.start_new_page()
        
        url = url_map[ename]
        names = entity_linker.url2names[url]
        types = entity_linker.bk_info_map[url].types
        domains = get_url_domains(types, important_domains)
        page_info = PageInfo(names, url, domains)
        # page_info = PageInfo(ename)
        # if ename != "冰与火之歌":
            # continue
        for data in datas:
            entities = data.entities
            bk_urls = data.bk_urls
            sentence = data.sentence.encode('utf-8')
            if sentence != "任天堂株式会社(日文:任天堂株式会社，平假名:にんてんどうかぶしきがいしゃ)于1947年11月20日成立 。电子游戏业三巨头之一，是具有全球影响力的游戏生产商。":
                continue
            print domains
            link_map, ner_names = testor.test(sentence, page_info, stf_results_map[sentence])


            print sentence
            for entity, url in zip(data.entities, data.bk_urls):
                estimation['total'] += 1
                if entity in link_map:
                    linked_url = link_map[entity]
                    if linked_url in same_link_map:
                        linked_url = same_link_map[linked_url]
                    if linked_url == url :
                        estimation['right'] += 1
                        print '\t%s\t%s\t%s\t%s' %(entity, url, link_map[entity], 'right')
                    else:
                        estimation['error'] += 1
                        print '\t%s\t%s\t%s\t%s' %(entity, url, linked_url, 'error')
                elif entity in ner_names:
                    estimation['linking miss'] += 1 
                    print '\t%s\t%s\t%s' %(entity, url, 'linking miss')
                else:
                    estimation['ner miss'] += 1 
                    print '\t%s\t%s\t%s' %(entity, url, 'ner miss')
    Print(str(estimation))


            









