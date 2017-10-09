from .test_extractor import process_labeled_data
from .structure import StrEntity
from .ltp import LTP

class Estimation():
    def __init__(self):
        self.total = 0
        self.right = 0
        self.partial_right = 0
        self.error_seg = 0
        self.error = 0


class RelExtractorTestor():
    def __init__(self, extractor, ltp = None):
        if ltp is None:
            ltp = LTP(None)
        self.ltp = ltp
        self.extractor = extractor
        self.estimation = Estimation()

    def add(self, data):
        sentence = data.sentence        
        ltp_result = ltp.parse(sentence)
        self.extractor.find_path_verbs()

        entity_pool = [False] * ltp_result.length

        for kl in data.knowledges:
            kl.subj = kl.subj.encode('utf-8')
            kl.rel = kl.rel.encode('utf-8')
            kl.obj = kl.subj.encode('utf-8')

            st, ed = ltp_result.search_word(kl.subj)
            if st != -1:
                for i in range(st, ed):
                    entity_pool[i] = True

            st, ed = ltp_result.search_word(kl.obj)
            if st == -1:
                continue
            for i in range(st, ed):
                entity_pool[i] = True
        
        ret = {}
        for kl in data.knowledges:
            kl_str = kl.triple()
            self.estimation.total += 1
            st_1, ed_1 = ltp_result.search_word(kl.subj)
            st_2, ed_2 = ltp_result.search_word(kl.obj)
            if st_1 == -1 or st_2 == -1:
                self.estimation.error_seg += 1
                ret[kl_str] = (None, "miss segement")
                continue
            
            rels = self.extractor.find_path_verbs(ltp_result, StrEntity(st_1, ed_1), StrEntity(st_2, ed_2), entity_pool)
            rels = [ltp_result.text(st, ed) for st, ed in rels]
            rels_str = "\t".join(rels)
            prop = kl.prop

            if prop in rels:
                self.estimation.right += 1
                ret[kl_str] = (rels_str, "right")
                continue

            partial_right_flag = False
            for rel in rels:
                if rel.find(prop) != -1:
                    partial_right_flag = True
                    break
            if partial_right_flag:
                self.estimation.partial_right += 1
                ret[kl_str] = (rels_str, 'partial rights')
                continue
        
            self.estimation.error += 1
            ret[kl_str] = (rels_str, 'error')
        return ret

if __name__ == "__main__":
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_miss = True)
    


