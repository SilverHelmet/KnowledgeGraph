#encoding: utf-8
import os
import json
from src.extractor.entity.linkers import PageMemoryEntityLinker
from src.extractor.table.table_parser import parse_tables_from_html
from src.extractor.table.table_rule_parser import sorted_table, encode_table
from src.extractor.resource import Resource
from src.extractor.structure import PageInfo
from src.IOUtil import load_html_file, cache_dir, rel_ext_dir
from src.extractor.util import get_url_domains
from src.extractor.entity.ner import NamedEntityReg


def test_path():
    ner = NamedEntityReg()
    entity_linker = PageMemoryEntityLinker()

    baike_ename_title_map = Resource.get_singleton().get_baike_ename_title()
    
    table_parser = Resource.get_singleton().get_table_parser(entity_linker, ner)
    important_doains = Resource.get_singleton().get_important_domains()

    doc_path = os.path.join(rel_ext_dir, 'baike_doc.json')
    for line in file(doc_path, 'r'):
        url, doc = line.split('\t')
        if not url in entity_linker.bk_info_map:
            print 'error url', url
        entity_types = entity_linker.bk_info_map[url].types
        names = entity_linker.url2names[url]
        page_info = PageInfo(baike_ename_title_map[url][0], names, url, get_url_domains(entity_types, important_doains), entity_types)

        entity_linker.start_new_page(url)
        doc = json.loads(doc)
        for chapter_title, html in doc:

            if not type(html) is unicode:
                continue
            
            tables = parse_tables_from_html(html)

            for table in tables:
                table = encode_table(table)
                
                table_kns = table_parser.parse(table, page_info, entity_types)
                if len(table_kns) > 0:
                    print chapter_title, table['columns']
                    for line, row_kns in table_kns:
                        print "\t%s" %line
                        for kn in row_kns:
                            print "\t\t%s" %kn.info()

def debug():
    
    ner = NamedEntityReg()
    entity_linker = PageMemoryEntityLinker()

    baike_ename_title_map = Resource.get_singleton().get_baike_ename_title()
    
    table_parser = Resource.get_singleton().get_table_parser(entity_linker, ner)
    important_doains = Resource.get_singleton().get_important_domains()

    url = 'baike.so.com/doc/8342332-8659322.html'
    path = os.path.join(cache_dir, 'tables/兰萨法姆.html')
    entity_types = entity_linker.bk_info_map[url].types
    names = entity_linker.url2names[url]
    page_info = PageInfo(baike_ename_title_map[url][0], names, url, get_url_domains(entity_types, important_doains), entity_types)
    html = load_html_file(path)
    entity_linker.start_new_page(url)
    entity_linker.team_suffix_dict.meet_url('baike.so.com/doc/6644091-6857906.html')

    tables = parse_tables_from_html(html)
    tables = [encode_table(table) for table in tables]
    
    for table in tables:
        print table['columns']
        kns = table_parser.parse(table, page_info, entity_types)
        for kn in kns:
            print kn.info()





if __name__ == "__main__":
    test_path()
    # debug()
