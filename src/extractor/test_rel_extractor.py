
from .test_extractor import process_labeled_data
from .structure import StrEntity
from .ltp import LTP
from .dependency.tree import VerbRelationExtractor
from .entity.naive_ner import NaiveNer

class Estimation():
    def __init__(self):
        self.total = 0
        self.exact_right = 0
        self.right = 0
        self.partial_right = 0
        self.error_seg = 0
        self.error = 0

    def print_info(self):
        print "total:", self.total
        print "exact_right:", self.exact_right
        print "right:", self.right
        print "partial right:", self.partial_right
        print 'error segment:', self.error_seg
        print "error", self.error


class RelExtractorTestor():
    def __init__(self, extractor, ltp = None):
        if ltp is None:
            ltp = LTP(None)
        self.ltp = ltp
        self.ner = NaiveNer()
        self.extractor = extractor
        self.estimation = Estimation()

    def add(self, data):
        sentence = data.sentence.encode('utf-8')
        ltp_result = ltp.parse(sentence)

        entity_pool = [False] * ltp_result.length
        entities = self.ner.recognize(sentence, ltp_result, None)

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
            st_1, ed_1 = ltp_result.search_word(kl.subj)
            st_2, ed_2 = ltp_result.search_word(kl.obj)
            if st_1 == -1 or st_2 == -1:
                self.estimation.error_seg += 1
                ret[kl_str] = (" ".join(ltp_result.words), "error segment")
                continue
            
            rels = self.extractor.extract_relation(ltp_result, StrEntity(st_1, ed_1), StrEntity(st_2, ed_2), entity_pool)
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
        
            self.estimation.error += 1
            ret[kl_str] = (rels_str, 'error')
        return ret

def test(extractor, ltp):
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_miss = True)

    print "#sentence: %d, #labeled: %d" %(nb_data, nb_kl)

    testor = RelExtractorTestor(extractor, ltp)
    for url in datas_map:
        datas = datas_map[url]
        for data in datas:
            ret = testor.add(data)
            for labeled in ret:
                out = ret[labeled]
                if out[1] == 'partial right':
                    print data.sentence
                    print '\t%s' %out[0]
                    print '\t%s' %labeled
                    
    testor.estimation.print_info()



if __name__ == "__main__":
    extractor = VerbRelationExtractor()
    ltp = LTP(None)
    test(extractor, ltp)
    


