#encoding: utf-8
from src.IOUtil import rel_ext_dir, nb_lines_of, Print
from src.extractor.entity.ner import NamedEntityReg
from src.extractor.docprocessor import DocProcessor
from src.extractor.dependency.verb_title_relation_extractor import VerbRelationExtractor
from src.extractor.entity.linkers import PageMemoryEntityLinker
from src.rel_extraction.util import load_mappings
from src.extractor.resource import Resource
from src.extractor.structure import PageInfo
from src.extractor.util import get_url_domains
import os
from tqdm import tqdm
import json

def make_str_entity_key(str_entity):
    return str_entity.st * 1000 + str_entity.ed

def map_predicate(fb_rels, obj_name):
    
    properties = []
    for prop in fb_rels:
        values = fb_rels[prop]
        if obj_name in values:
            properties.append(prop)
    return properties


def try_map_triple(subj, predicate, obj, ltp_result, link_map, bk2fb, fb_rels_map):
    subj_key = make_str_entity_key(subj)
    if subj_key in link_map:
        baike_entity = link_map[subj_key]
        bk_url = baike_entity.baike_url
        if bk_url in bk2fb:
            fb_uri = bk2fb[bk_url]
            if fb_uri in fb_rels_map:
                fb_rels = fb_rels_map[fb_uri]
                try:
                    obj_name = ltp_result.text(obj.st, obj.ed).decode('utf-8')
                except Exception, e:
                    return []
                maps = map_predicate(fb_rels, obj_name)
                if len(maps) >= 3:
                    return []
                else:
                    return maps
    return []

def generate_data_from_chapter(title, paragraphs, page_info, doc_processor, e_linker, fb_rels_map, rel_extractor, outf, bk2fb):
    results = doc_processor.parse_chapter(title, paragraphs, page_info, parse_ner = True)
    for ltp_result, str_entities, _ in results:
        rels = rel_extractor.find_tripple(ltp_result, str_entities)
        link_map = {}
        for str_entity in str_entities:
            baike_entity = e_linker.link(ltp_result, str_entity, page_info)
            if len(baike_entity) > 0:
                baike_entity = baike_entity[0]
                link_map[make_str_entity_key(str_entity)] = baike_entity

        new_rels = []
        for subj, pred, obj in rels:
            if type(subj) is int or type(obj) is int:
                continue
            if pred is None or type(pred) is str:
                continue
            pred = ltp_result.text(pred, pred+1)
            # if pred == '是':
            #     continue
            new_rels.append((subj, pred, obj))
        rels = new_rels

        predicate_map = {}
        for subj, pred, obj in rels:
            # print ltp_result.text(subj.st, subj.ed), pred, ltp_result.text(obj.st, obj.ed)
            mapped_predicate = []
            mapped_predicate.extend(try_map_triple(subj, pred, obj, ltp_result, link_map, bk2fb, fb_rels_map))
            mapped_predicate.extend(try_map_triple(obj, pred, subj, ltp_result, link_map, bk2fb, fb_rels_map))
        
            if len(mapped_predicate) > 0:
                if not pred in predicate_map:
                    predicate_map[pred] = []
                predicate_map[pred].extend(mapped_predicate)
        if len(predicate_map) > 0:
            outf.write("%s\n" %(ltp_result.sentence))
            for pred in predicate_map:
                outf.write("\t%s\t%s\n" %(pred, "\t".join(predicate_map[pred])))




def generate_data_from_summary(summary_path, bk2fb, fb_uris, outpath):
    resource = Resource.get_singleton()
    fb_rels_map = resource.get_half_named_fb_info()
    ner = NamedEntityReg()
    e_linker = PageMemoryEntityLinker()
    doc_processor = DocProcessor(ner)
    url2names = resource.get_url2names()
    bk_info_map = resource.get_baike_info()
    important_domains = resource.get_important_domains()
    rel_extracotr = VerbRelationExtractor()

    Print('generate data from [%s]' %os.path.basename(summary_path))
    outf = file(outpath, 'w')
    for line in tqdm(file(summary_path), total = nb_lines_of(summary_path)):
        bk_url, summary = line.split('\t')
        if bk_url not in bk2fb:
            continue
        if not bk_url in bk2fb:
            continue
        fb_uri = bk2fb[bk_url]
        if fb_uri not in fb_rels_map:
            continue
        outf.write('##start parsing %s\n' %(bk_url))
        names = url2names[bk_url]
        types = bk_info_map[bk_url].types
        page_info = PageInfo(names[-1], names, bk_url, get_url_domains(types, important_domains), types)

        e_linker.start_new_page(bk_url)
        
        summary = [json.loads(summary)['summary']]
        chapter_title = 'intro_summary'

        generate_data_from_chapter(chapter_title, summary, page_info, doc_processor, e_linker, 
            fb_rels_map, rel_extracotr, outf, bk2fb)

    outf.close()


if __name__ == "__main__":
    summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary.json')
    bk2fb = load_mappings()
    fb_uris = set(bk2fb.values())
    # fb_entity_info_path = os.path.join(rel_ext_dir, 'mapped_fb_entity_info_processed.json')

    outpath = os.path.join(rel_ext_dir, 'dataset/summary_dataset.tsv')
    generate_data_from_summary(summary_path, bk2fb, fb_uris, outpath)




    


