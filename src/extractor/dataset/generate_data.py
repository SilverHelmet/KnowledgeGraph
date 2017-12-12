#encoding: utf-8
from src.IOUtil import rel_ext_dir, nb_lines_of, Print, dataset_dir
from src.extractor.entity.ner import NamedEntityReg
from src.extractor.docprocessor import DocProcessor
from src.extractor.dependency.verb_title_relation_extractor import VerbRelationExtractor
from src.extractor.entity.linkers import PageMemoryEntityLinker
from src.rel_extraction.util import load_mappings
from src.extractor.resource import Resource
from src.extractor.structure import PageInfo
from src.extractor.util import get_url_domains
from src.util import add_values_to_dict_list
import os
from tqdm import tqdm
import json

def make_str_entity_key(str_entity):
    return str_entity.st * 1000 + str_entity.ed

def map_predicate(fb_rels, obj_name):
    if type(obj_name) is str:
        obj_name = obj_name.decode('utf-8')
    if obj_name not in fb_rels['total']:
        return []
    properties = []
    for prop in fb_rels:
        if prop == 'total':
            continue
        values = fb_rels[prop]
        if obj_name in values:
            properties.append(prop)
    return properties


# def try_map_triple(subj, obj, ltp_result, fb_rels):
#     try:
#         obj_name = ltp_result.text(obj.st, obj.ed).decode('utf-8')
#     except Exception, e:
#         return []
#     maps = map_predicate(fb_rels, obj_name)
#     if len(maps) >= 3:
#         return []
#     else:
#                 return maps
#     return []

def try_map_triple(obj_names, fb_rels, is_time, schema):
    maps = []

    for obj_name in obj_names:
        maps.extend(map_predicate(fb_rels, obj_name))
    if is_time:
        time_props = schema.get_datetime_properties()
        maps = [mapped_prop for mapped_prop in maps if mapped_prop in time_props]

    maps_set = list(set(maps))
    if len(maps_set) >= 3:
        return []
    else:
        return maps

def generate_data_from_chapter(title, paragraphs, page_info, doc_processor, fb_rels, rel_extractor, outf, e_linker, schema):
    results = doc_processor.parse_chapter(title, paragraphs, page_info, parse_ner = True)
    for ltp_result, str_entities, _ in results:
        try:
            if ltp_result is None:
                continue
            # Print(ltp_result.sentence)
            rels = rel_extractor.find_tripple(ltp_result, str_entities)

            link_map = {}
            baike_entities = []
            for str_entity in str_entities:
                baike_entity = e_linker.link(ltp_result, str_entity, page_info)
                if len(baike_entity) > 0:
                    baike_entity = baike_entity[0]
                    baike_entities.append(baike_entity)
                    link_map[make_str_entity_key(str_entity)] = baike_entity
                else:
                    baike_entities.append(None)
                    link_map[make_str_entity_key(str_entity)] = None
            e_linker.add_sentence(ltp_result, str_entities, baike_entities)

            new_rels = []
            for subj, pred, obj, enviroment, rel_type  in rels:
                if rel_type not in ['coo_noun_type', 'entity']:
                    continue
                if type(subj) is int or type(obj) is int:
                    continue
                if type(subj) is str or type(obj) is str:
                    continue
                if pred is None or type(pred) is str:
                    continue

                pred = ltp_result.text(pred, pred+1)
                # if pred == '是':
                #     continue
                new_rels.append((subj, pred, obj, enviroment))

            rels = new_rels
            predicate_map = {}
            
            # for subj, pred, obj, env in rels:
            #     subj_name = ltp_result.text(subj.st, subj.ed)
            #     obj_name = ltp_result.text(obj.st, obj.ed)
            #     # print ltp_result.text(subj.st, subj.ed), pred, ltp_result.text(obj.st, obj.ed)
            #     mapped_predicate = []
            #     if subj_name in page_info.names:
            #         mapped_predicate.extend(try_map_triple(subj, obj, ltp_result, fb_rels))
            #     if obj_name in page_info.names:
            #         mapped_predicate.extend(try_map_triple(obj, subj, ltp_result, fb_rels))
            
            #     if len(mapped_predicate) > 0:
            #         if not pred in predicate_map:
            #             predicate_map[pred] = []
            #         predicate_map[pred].extend(mapped_predicate)
            # if len(predicate_map) > 0:
            #     outf.write("%s\n" %(ltp_result.sentence))
            #     for pred in predicate_map:
            #         outf.write("\t%s\t%s\n" %(pred, "\t".join(predicate_map[pred])))


            for subj, pred, obj, env in rels:
                subj_name = ltp_result.text(subj.st, subj.ed)
                obj_name = ltp_result.text(obj.st, obj.ed)

                if obj_name in page_info.names:
                    tmp = subj
                    subj = obj
                    obj = tmp

                bk_subj = link_map[make_str_entity_key(subj)]
                

                if subj_name in page_info.names:
                    if obj.etype == "Nt":
                        obj_names = [str(obj.obj)]
                        is_time = True
                    else:
                        bk_obj = link_map[make_str_entity_key(obj)]
                        is_time = False
                        if bk_obj:        
                            obj_names = e_linker.url2names[bk_obj.baike_url]
                        else:
                            obj_names = [obj_name]
                    mapped_props = try_map_triple(obj_names, fb_rels, is_time, schema)
                    mapped_props = set(list(mapped_props))
                    if len(mapped_props) > 0:
                        if type(env) is int:
                            env = ltp_result.text(env, env + 1)
                        else:
                            env = None

                        if env:
                            key = pred + "#" + env
                        else:
                            key = pred
                        
                        add_values_to_dict_list(predicate_map, key, mapped_props)
            if len(predicate_map) > 0:
                outf.write("%s\n" %(ltp_result.sentence))
                for pred in predicate_map:
                    outf.write("\t%s\t%s\n" %(pred, "\t".join(predicate_map[pred])))

        except Exception, e:
            print '\nerror in parsing %s' %ltp_result.sentence




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
    schema = resource.get_schema()

    Print('generate data from [%s]' %os.path.basename(summary_path))
    outf = file(outpath, 'w')
    cnt = 0
    for line in tqdm(file(summary_path), total = nb_lines_of(summary_path)):
        bk_url, summary = line.split('\t')
        if bk_url not in bk2fb:
            continue
        fb_uri = bk2fb[bk_url]
        if fb_uri not in fb_rels_map:
            continue
        fb_rels = fb_rels_map[fb_uri]
        cnt += 1
        if cnt % 100 == 0:
            Print('\ncnt = %d' %cnt)

        # outf.write('##start parsing %s\n' %(bk_url))


        bk_info = bk_info_map[bk_url]
        if bk_info.pop < 4 + 5:
            continue
        types = bk_info.types
        names = url2names[bk_url]
        page_info = PageInfo(names[-1], names, bk_url, get_url_domains(types, important_domains), types)

        e_linker.start_new_page(bk_url)
        
        summary = [json.loads(summary)['summary']]
        chapter_title = 'intro_summary'

        generate_data_from_chapter(chapter_title, summary, page_info, doc_processor, 
            fb_rels, rel_extracotr, outf, e_linker, schema)

    outf.close()

def generate_data_from_doc(doc_path, bk2fb, fb_uris, outpath):
    resource = Resource.get_singleton()
    fb_rels_map = resource.get_half_named_fb_info()
    ner = NamedEntityReg()
    e_linker = PageMemoryEntityLinker()
    doc_processor = DocProcessor(ner)
    url2names = resource.get_url2names()
    bk_info_map = resource.get_baike_info()
    important_domains = resource.get_important_domains()
    rel_extracotr = VerbRelationExtractor()
    schema = resource.get_schema()

    Print('generate data from [%s]' %os.path.basename(doc_path))
    outf = file(outpath, 'w')
    cnt = 0
    for line in tqdm(file(doc_path), total = nb_lines_of(doc_path)):
        bk_url, doc = line.split('\t')
        if bk_url not in bk2fb:
            continue
        fb_uri = bk2fb[bk_url]
        if fb_uri not in fb_rels_map:
            continue
        fb_rels = fb_rels_map[fb_uri]
        cnt += 1
        if cnt % 100 == 0:
            Print('\ncnt = %d' %cnt)

        # outf.write('##start parsing %s\n' %(bk_url))


        bk_info = bk_info_map[bk_url]
        if bk_info.pop < 4 + 5:
            continue
        types = bk_info.types
        names = url2names[bk_url]        
        page_info = PageInfo(names[-1], names, bk_url, get_url_domains(types, important_domains), types)

        e_linker.start_new_page(bk_url)
        
        # summary = [json.loads(summary)['summary']]
        # chapter_title = 'intro_summary'

        doc = json.loads(doc)
        for chapter_title, chapter in doc:
            chapter = [para for para in chapter if para.find('</table>') == -1]
            if len(chapter) == 0:
                continue
            generate_data_from_chapter(chapter_title, chapter, page_info, doc_processor, 
                fb_rels, rel_extracotr, outf, e_linker, schema)

    outf.close()


if __name__ == "__main__":
    
    bk2fb = load_mappings()
    fb_uris = set(bk2fb.values())
    # fb_entity_info_path = os.path.join(rel_ext_dir, 'mapped_fb_entity_info_processed.json')

    # summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary.json')
    # outpath = os.path.join(dataset_dir, 'summary_dataset.tsv')
    # generate_data_from_summary(summary_path, bk2fb, fb_uris, outpath)

    doc_path = os.path.join(rel_ext_dir, 'baike_doc.json')
    outpath = os.path.join(dataset_dir, 'doc_dataset.tsv')
    generate_data_from_doc(doc_path, bk2fb, fb_uris, outpath)
    

