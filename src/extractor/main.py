from .simple_extractors import SimpleLTPExtractor
from src.extractor.table.table_parser import parse_tables_from_html
from src.extractor.table.table_rule_parser import encode_table
from src.extractor.entity.ner import NamedEntityReg
from .util import get_url_domains
from .structure import PageInfo
from ..IOUtil import Print, rel_ext_dir, nb_lines_of
from src.extractor.docprocessor import DocProcessor
from .dependency.verb_title_relation_extractor import VerbRelationExtractor
from entity.linkers import SeparatedLinker, MatchRelLinker, PageMemoryEntityLinker
from src.extractor.resource import Resource
import sys
import os
import json


def work(inpath, outpath):
    ner = NamedEntityReg()
    doc_processor = DocProcessor(ner)
    rel_extractor = VerbRelationExtractor()

    entity_linker = PageMemoryEntityLinker()
    rel_linker = MatchRelLinker()
    linker = SeparatedLinker(entity_linker, rel_linker)

    table_parser = Resource.get_singleton().get_table_parser(entity_linker, ner)
    
    ltp_extractor = SimpleLTPExtractor(doc_processor, rel_extractor, linker)
    url2names = linker.entity_linker.url2names
    bk_info_map = linker.entity_linker.bk_info_map
    baike_ename_title_map = Resource.get_singleton().get_baike_ename_title()
    
    important_domains = Resource.get_singleton().get_important_domains()

    outf = file(outpath, 'w')
    total = nb_lines_of(inpath)
    for cnt, line in enumerate(file(inpath), start = 1):
        # obj = json.loads(line)
        # url = obj['url']
        # chapters = obj['chapters']
        url, chapters = line.split('\t')
        

        
        if not url in url2names or not url in bk_info_map or not url in baike_ename_title_map:
            print 'error url %s' %(url)
            continue
        chapters = json.loads(chapters)   

        outf.write('##parse url:%s\n' %url)
        Print('parse url:%s (%d/%d)' %(url, cnt, total))
        names = url2names[url]
        types = bk_info_map[url].types
        page_info = PageInfo(baike_ename_title_map[url][0], names, url, get_url_domains(types, important_domains), types)
        entity_linker.start_new_page(url)

        for title, chapter in chapters:
            # try:
            if type(chapter) is unicode:
                continue
                tables = parse_tables_from_html(chapter)
                tables = [encode_table(table) for table in tables]
                for table in tables:
                    table_kns = table_parser.parse(table, page_info, types)
                    if len(table_kns) > 0:
                        for line, row_kns in table_kns:
                            outf.write("%s\n" %line)
                            for kn in row_kns:
                                outf.write("\t%s\n" %kn.info())

            else:
                for ltp_result, str_entities, _ in doc_processor.parse_chapter(title, chapter, page_info, parse_ner = True):
                    if ltp_result is None:
                        continue
                    triples, _ = ltp_extractor.parse_sentence(ltp_result, str_entities, page_info, None, False)
                    triples = [triple for triple in triples if triple.score() > 0.01]
                    if len(triples) > 0:
                        outf.write("%s\n" %(ltp_result.sentence))
                        for triple in triples:
                            outf.write("\t%s\n" %triple.info(ltp_result))
            # except Exception, e:
            #     print "error at url:%s chapter:%s" %(url, title)
            #     print str(e)
            
    outf.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'format:'
        print "python -m src.extractor.main inpath outpath"
    else:
        inpath = sys.argv[1]
        outpath = sys.argv[2]
        work(inpath, outpath)
        

    
