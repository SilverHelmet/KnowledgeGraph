#encoding:utf-8
from .test_extractor import process_labeled_data
from ..util import load_stanford_result
from ..structure import StrEntity
from src.extractor.resource import Resource
from ..ltp import LTP
from ..dependency.verb_title_relation_extractor import VerbRelationExtractor
from ..entity.naive_ner import NaiveNer
from ..entity.ner import NamedEntityReg
from ...IOUtil import data_dir
import os

class Estimation():
    def __init__(self):
        self.total = 0
        self.exact_right = 0
        self.right = 0
        self.partial_right = 0
        self.error_seg = 0
        self.error = 0
        self.noverb_right = 0
        self.noverb_error = 0

    def print_info(self):
        print "total:", self.total
        print "exact_right:", self.exact_right
        print "right:", self.right
        print "partial right:", self.partial_right
        print 'error segment:', self.error_seg
        print "error", self.error
        print ""
        print "noverb right", self.noverb_right
        print "noverb error", self.noverb_error


class RelExtractorTestor():
    def __init__(self, extractor, ltp = None, use_advanced_ner = True):
        if ltp is None:
            ltp = LTP(None)
        self.ltp = ltp
        self.use_advanced_ner = use_advanced_ner
        if use_advanced_ner:
            self.ner = NamedEntityReg()
            base_dir = os.path.join(data_dir, '标注数据')
            self.stf_results_map = load_stanford_result(os.path.join(base_dir, 'sentences.txt'), os.path.join(base_dir, 'sentences_stanf_nlp.json'))
        else:
            self.ner = NaiveNer()

        self.extractor = extractor
        self.estimation = Estimation()

    def add(self, data):
        sentence = data.sentence.encode('utf-8')
        ltp_result = ltp.parse(sentence)

        
        if self.use_advanced_ner:
            stf_result = self.stf_results_map[sentence]
            
            entities = self.ner.recognize(sentence, ltp_result, None, stf_result)
            entities = [(e.st, e.ed)for e in entities]
            ltp_result.update_parsing_tree(self.ltp)
        else:
            entities = self.ner.recognize(sentence, ltp_result, None)
        entity_pool = [False] * ltp_result.length
        for st, ed in entities:
            for i in range(st, ed):
                entity_pool[i] = True

        # for kl in data.knowledges:		         
            
        #     kl.subj = kl.subj.encode('utf-8')		
        #     kl.prop = kl.prop.encode('utf-8')		
        #     kl.obj = kl.obj.encode('utf-8')		
        #     st, ed = ltp_result.search_word(kl.subj)		
        #     if st != -1:		
        #         for i in range(st, ed):		
        #             entity_pool[i] = True		

        #     st, ed = ltp_result.search_word(kl.obj)		
        #     if st != -1:				
        #         for i in range(st, ed):		  
        #             entity_pool[i] = True
        
        ret = {}
        for kl in data.knowledges:
            kl.subj = kl.subj.encode('utf-8')
            kl.prop = kl.prop.encode('utf-8')
            kl.obj = kl.obj.encode('utf-8')
            kl_str = kl.triple()
            self.estimation.total += 1
            st_eds_1 = ltp_result.search_word(kl.subj, search_all = True)
            st_eds_2 = ltp_result.search_word(kl.obj, search_all = True)
            if len(st_eds_1) == 0 or len(st_eds_2) == 0:
                self.estimation.error_seg += 1
                ret[kl_str] = (" ".join(ltp_result.words), "error segment")
                continue

            rels = []
            for st_1, ed_1 in st_eds_1:
                for st_2, ed_2 in st_eds_2:
                    rels.extend(self.extractor.find_relation(ltp_result, StrEntity(st_1, ed_1, None), StrEntity(st_2, ed_2, None), entity_pool))
            rels = [ltp_result.text(st, ed) for st, ed in rels]
            rels_str = "\t".join(rels)
            prop = kl.prop

            if prop in rels:
                
                if len(rels) == 1:
                    self.estimation.exact_right += 1
                    ret[kl_str] = (rels_str, "exact right")
                else:
                    self.estimation.right += 1
                    ret[kl_str] = (rels_str, "right")
                continue

            partial_right_flag = False
            for rel in rels:
                if prop.find(rel) != -1:
                    partial_right_flag = True
                    break
            if partial_right_flag:
                self.estimation.partial_right += 1
                ret[kl_str] = (rels_str, 'partial right')
                continue

            if prop.strip() == '*':
                if len(rels) > 0:
                    self.estimation.noverb_right += 1
                    ret[kl_str] = (rels_str, 'noverb right')
                else:
                    self.estimation.noverb_error += 1
                    ret[kl_str] = (rels_str, 'noverb error')
                continue
                
        
            self.estimation.error += 1
            ret[kl_str] = (rels_str, 'error')
        return ret, ltp_result

    def test_all(self, data):
        sentence = data.sentence.encode('utf-8')
        ltp_result = ltp.parse(sentence)
    
        if self.use_advanced_ner:
            stf_result = self.stf_results_map[sentence]
            
            entities = self.ner.recognize(sentence, ltp_result, None, stf_result)
            entities = [(e.st, e.ed)for e in entities]
        else:
            entities = self.ner.recognize(sentence, ltp_result, None)

        entity_pool = [False] * ltp_result.length
        for st, ed in entities:
            for i in range(st, ed):
                entity_pool[i] = True

        ret = []
        str_entity = []
        for i in entities:
            str_entity.append(StrEntity(i[0], i[1], None))
        raw_rels = self.extractor.find_tripple(ltp_result, str_entity)
        r1 = None
        r2 = None
        r3 = None
        for k, item in enumerate(raw_rels):
            if isinstance(item[0], int) == False:
                r1 = ltp_result.text(item[0].st, item[0].ed)
            else:
                r1 = ltp_result.text(item[0], item[0] + 1)
            if isinstance(item[2], int) == False:
                r3 = ltp_result.text(item[2].st, item[2].ed)
            else:
                r3 = ltp_result.text(item[2], item[2] + 1)
            if item[1] == None:
                r2 = "是"
            else:
                r2 = ltp_result.text(item[1], item[1] + 1)
            ret.append((r1, r2, r3))
        ret = set(ret)
        '''
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                e1 = entities[i]
                e2 = entities[j]
                e1_text = ltp_result.text(e1[0], e1[1])
                e2_text = ltp_result.text(e2[0], e2[1])
                rels = self.extractor.find_relation(ltp_result, StrEntity(e1[0], e1[1], None), StrEntity(e2[0], e2[1], None), entity_pool)
                rels = [ltp_result.text(st, ed) for st, ed in rels]
                if len(rels) > 0:
                    rel = " ".join(rels)
                    ret.append((e1_text, rel, e2_text))
        '''
        return ret
                
                
        
                
def test(extractor, ltp):
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_subj_miss = True, ignore_verb_miss = False)

    print "#sentence: %d, #labeled: %d" %(nb_data, nb_kl)

    testor = RelExtractorTestor(extractor, ltp, use_advanced_ner = True)
    for url in datas_map:
        datas = datas_map[url]
        for data in datas:
            ret, ltp_result = testor.add(data)
            for labeled in ret:
                out = ret[labeled]
                if out[1] == 'noverb right':
                    print data.sentence
                    print '\t%s' %out[0]
                    print '\t%s' %labeled
                    
    testor.estimation.print_info()

def print_all(extractor, ltp):
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_subj_miss = True, ignore_verb_miss = True, clear = False)

    print "#sentence: %d, #labeled: %d" %(nb_data, nb_kl)

    testor = RelExtractorTestor(extractor, ltp, use_advanced_ner = True)
    for url in datas_map:
        datas = datas_map[url]
        for data in datas:
            triples = testor.test_all(data)
            # if data.sentence != u'《青花瓷》是方文山作词，周杰伦作曲并演唱的歌曲，收录于2007年11月2日周杰伦制作发行音乐专辑《我很忙》中。':
            #     continue
            print data.sentence
            print "tripple num:", len(triples)
            for triple in triples:
                print '\t%s' %('\t'.join(triple))
            for kl in data.knowledges:
                print "\t\t%s" %(kl.triple())



if __name__ == "__main__":
    extractor = VerbRelationExtractor()
    ltp = Resource.get_singleton().get_ltp()
    print_all(extractor, ltp)
    


