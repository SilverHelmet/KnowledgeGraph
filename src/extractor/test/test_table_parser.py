#encoding: utf-8
import os
from src.extractor.entity.linkers import PageMemoryEntityLinker
from src.extractor.table.table_parser import parse_tables_from_html
from src.extractor.table.table_rule_parser import sorted_table, encode_table
from src.extractor.resource import Resource
from src.extractor.structure import PageInfo
from src.IOUtil import load_html_file, cache_dir
from src.extractor.util import get_url_domains
from src.extractor.entity.ner import NamedEntityReg

def debug():
    url = 'baike.so.com/doc/1287918-1361771.html'
    ner = NamedEntityReg()
    entity_linker = PageMemoryEntityLinker()
    
    table_parser = Resource.get_singleton().get_table_parser(entity_linker, ner)
    important_doains = Resource.get_singleton().get_important_domains()

    path = os.path.join(cache_dir, 'tables/刘德华.html')
    entity_types = entity_linker.bk_info_map[url].types
    names = entity_linker.url2names[url]
    page_info = PageInfo(names[-1], names, url, get_url_domains(entity_types, important_doains), entity_types)
    html = load_html_file(path)
    tables = parse_tables_from_html(html)
    tables = [encode_table(table) for table in tables]
    for table in tables:
        kns = table_parser.parse(table, page_info, entity_types)
        for kn in kns:
            print kn.info()





if __name__ == "__main__":
    debug()
