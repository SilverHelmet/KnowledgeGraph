#encoding: utf-8
from ..IOUtil import data_dir
from .ltp import LTP
import os
import glob

class Data:
    def __init__(self, url, title, sentence):
        self.url = url
        self.title = title
        self.sentence = sentence
        self.entities = []
        self.bk_urls = []
    
    def add(self, entity_str, bk_url):
        self.entities.append(entity_str)
        self.bk_urls.append(bk_url)


def read_data_from_file(filepath, datas_map, ignore_miss):
    title = None
    sentence = None
    data = None
    datas = []
    url = os.path.basename(filepath).split('.')[0]
    for idx, line in enumerate(file(filepath), start = 1):
        line = line.rstrip()
        if line == "":
            continue
        if title is None:
            title = line
        elif line == '$':
            title = None
            sentence = None
            data = None
        else:
            if line.startswith('\t'):
                assert sentence is not None
                p = line.strip().split('\t')
                assert len(p) == 2
                if p[1].strip() == "*" and ignore_miss:
                    pass
                else:
                    data.add(p[0], p[1])
            
            else:
                sentence = line
                data = Data(url, title, sentence)
                datas.append(data)
    datas_map[url] = datas

def read_data(filepath, ignore_miss):
    datas_map = {}
    for filepath in glob.glob(filepath + '/*t*'):
        read_data_from_file(filepath, datas_map, ignore_miss)
    return datas_map

class Estimation:
    def __init__(self):
        # error + right = total output
        # miss + right = total labeled
        # miss_partial + miss_nn + miss_seg + miss_other = miss
        self.total_output = 0
        self.total_labeled = 0
        self.right = 0
        self.error = 0
        self.miss = 0
        self.miss_partial = 0
        self.miss_nn = 0
        self.miss_seg = 0
        self.miss_other = 0

    def print_info(self):
        print "total output:\t%d" %self.total_output
        print "total labeled:\t%d" %self.total_labeled
        print "right output:\t%d(%f)" %(self.right, (self.right + 0.0)/ self.total_output)
        print "error output:\t%d" %self.error
        print 'miss number:\t%d' %self.miss
        miss = self.miss + 0.0
        f = [self.miss_partial / miss, self.miss_seg/ miss, self.miss_nn /miss, self.miss_other / miss]
        f = [round(x, 2) for x in f]
        print "miss type: %d(%f) %d(%f) %d(%f) %d(%f)" %(self.miss_partial, f[0], self.miss_seg, f[1], self.miss_nn, f[2], self.miss_other, f[3])

class Estimator:
    def __init__(self):
        self.estimation = Estimation()

    def clear(self):
        self.estimation = Estimation()

    def add(self, ltp_result, entities_name, ner_entities_name):

        entities_name = [e if type(e) is str else e.encode('utf-8') for e in entities_name]
        ner_entities_name = [e if type(e) is str else e.encode('utf-8') for e in ner_entities_name]

        self.estimation.total_output += len(ner_entities_name)
        self.estimation.total_labeled += len(entities_name)
        
        entities_name_set = set(entities_name)
        for entity in ner_entities_name:
            if entity in entities_name_set:
                self.estimation.right += 1
            else:
                self.estimation.error += 1

        # miss analysis
        miss_type_map = {}
        for entity in entities_name:
            if entity in ner_entities_name:
                continue
            self.estimation.miss += 1
            if self.check_include(entity, ner_entities_name):
                self.estimation.miss_partial += 1
                miss_type_map[entity] = 1
                continue

            st, ed = self.find_pos(ltp_result, entity)
            if st == -1:
                self.estimation.miss_seg += 1
                miss_type_map[entity] = 2
                continue
            if self.check_noun(ltp_result, st, ed):
                self.estimation.miss_nn += 1
                miss_type_map[entity] = 3
            else:
                self.estimation.miss_other += 1
                miss_type_map[entity] = 4
        return miss_type_map
        
    def check_include(self, entity, reco_entities):
        for reco_entity in reco_entities:
            if reco_entity.find(entity) != -1 or entity.find(reco_entity) != -1:
                return True
        return False

    def find_pos(self, ltp_result, entity):
        length = ltp_result.length
        for st in range(length):
            for ed in range(st + 1, length + 1):
                string = ltp_result.text(st, ed)
                if len(string) > len(entity):
                    break
                if string == entity:
                    return st, ed
        return -1, -1

    def check_noun(self, ltp_result, st, ed):
        noun_tags = set(['n', 'nh', 'ni', 'nl', 'ns', 'nz'])
        for tag in ltp_result.tags[st:ed]:
            if not tag in noun_tags:
                return False
        return True


if __name__ == "__main__":
    datas_map = read_data(os.path.join(data_dir, '实体标注'), False)

    ltp = LTP(None)
    est = Estimator()
    for data_type in datas_map:
        datas = datas_map[data_type]
        for data in datas:
            sentence = data.sentence
            ltp_result = ltp.parse(sentence)

            # direct result of ltp ner, replace ner_entities_name with your improved result
            ner_entities_name = []
            for idx, ner_tag in enumerate(ltp_result.ner_tags):
                if ner_tag.startswith('S'):
                    ner_entities_name.append(ltp_result.text(idx, idx + 1))
                elif ner_tag.startswith('B'):
                    st = idx
                elif ner_tag.startswith('E'):
                    ner_entities_name.append(ltp_result.text(st, idx + 1))

            est.add(ltp_result, data.entities, ner_entities_name)
    est.estimation.print_info()

    