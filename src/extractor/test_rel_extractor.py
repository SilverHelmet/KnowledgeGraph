from .test_extractor import process_labeled_data
from .ltp import LTP

class Estimation():
    def __init__(self):
        self.total = 0
        self.right = 0
        self.partial_right = 0
        self.error_seg = 0


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
            self.estimation.total += 1
            st_1, ed_1 = ltp_result.search_word(kl.subj)
            st_2, ed_2 = ltp_result.search_word(kl.obj)
            if st_1 == -1 or st_2 == -1:
                self.estimation.error_seg += 1
                continue





            
            
    

        



if __name__ == "__main__":
    datas_map, nb_data, nb_kl = process_labeled_data(ignore_miss = True)


