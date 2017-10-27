from .simple_extractors import SimpleLTPExtractor
from test.test_extractor import load_stanford_result, load_important_domains
from .entity.ner import NamedEntityReg
from ..schema.schema import Schema
from .util import get_url_domains
from .structure import PageInfo
from ..IOUtil import Print, rel_ext_dir
import sys
import os
import json
from .ltp import LTP
from .dependency.verb_title_relation_extractor import VerbRelationExtractor
from entity.linkers import SeparatedLinker, MatchRelLinker, PageMemoryEntityLinker

def work(inpath, sentences_path, stanford_results_path, outpath):
    stf_result_map = load_stanford_result(sentences_path, stanford_results_path)

    ltp = LTP(None)
    ner = NamedEntityReg(ltp)
    rel_extractor = VerbRelationExtractor()

    schema = Schema()
    schema.init(init_type_neighbor = True)

    entity_linker = PageMemoryEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))
    rel_linker = MatchRelLinker()
    linker = SeparatedLinker(entity_linker, rel_linker, schema)

    ltp_extractor = SimpleLTPExtractor(ner, rel_extractor, linker, ltp, False)
    url2names = linker.entity_linker.url2names
    bk_info_map = linker.entity_linker.bk_info_map
    important_domains = load_important_domains()

    outf = file(outpath, 'w')
    for line in file(inpath):
        obj = json.loads(line)
        url = obj['url']
        
        if not url in url2names:
            print 'error url %s' %(url)
            continue

        sentences = [s.encode('utf-8').strip() for s in obj['sentences']]
        outf.write('%s\n' %url)
        Print('process %s' %url)
        names = url2names[url]
        types = bk_info_map[url].types
        page_info = PageInfo(names[0], names, url, get_url_domains(types, important_domains))
        
        
        entity_linker.start_new_page()
        for sentence in sentences:
            if sentence not in stf_result_map:
                Print("\terror sentence: %s" %sentence)
            stf_result = stf_result_map[sentence]

            triples, ltp_result = ltp_extractor.parse_sentence(sentence, page_info, stf_result, None, False)
            if len(triples) > 0:
                outf.write("\t%s\n" %sentence)
                for triple in triples:
                    outf.write("\t\t%s\n" %triple.info(ltp_result))
    Print('finished')
    outf.close()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print 'format:'
        print "python -m src.extractor.main inpath sentences_path stanford_results_path outpath"
    else:
        inpath = sys.argv[1]
        sentences_path = sys.argv[2]
        stanford_results_path = sys.argv[3]
        outpath = sys.argv[4]
        work(inpath, sentences_path, stanford_results_path, outpath)
        

    
