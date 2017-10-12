from entity.linkers import TopRelatedEntityLinker
from .test_ner import read_data
from entity.linkers import SeparatedLinker, MatchRelLinker, TopRelatedEntityLinker
from .entity.ner import NamedEntityReg
from ..IOUtil import data_dir
from .ltp import LTP
import os


class EntityLinkingTestor:
    def __init__(self, ner, linker, ltp): 
        self.linker = linker
        self.ner = ner
        self.ltp = ltp

    def test(self, sentence, data, page_info, stf_result):
        ltp_result = self.ltp.parse(sentence)
        stf_result = stf_results_map[sentence]
    



if __name__ == "__main__":
    datas_map, _, _  = read_data(os.path.join(data_dir, '实体标注'), ignore_miss = True)

    ner = NamedEntityReg()    
    entity_linker = TopRelatedEntityLinker(os.path.join(rel_ext_dir, 'baike_static_info.tsv'))

    base_dir = os.path.join(data_dir, '标注数据')
    stf_results_map = load_stanford_result(os.path.join(base_dir, 'sentences.txt'), os.path.join(base_dir, 'sentences_stanf_nlp.json'))

    testor = EntityLinkingTestor(ner, entity_linker, LTP(None))
    for ename in datas_map:
        for data in datas:
            entities = data.entities
            bk_urls = data.bk_urls

            ner = NamedEntityReg()    








