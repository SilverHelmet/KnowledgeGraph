#encoding: utf-8
import glob
from ..IOUtil import data_dir, rel_ext_dir
import os
from pyltp import NamedEntityRecognizer, Postagger, Segmentor


class Data:
    def __init__(self, url, title, sentence):
        self.url = url
        self.title = title
        self.sentence = sentence
        self.entities = []
    
    def add(self, entity_str, bk_url):
        self.entities.append(entity_str)

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
        miss = self.miss + 0.0
        f = [self.miss_partial / miss, self.miss_seg/ miss, self.miss_nn /miss, self.miss_other / miss]
        f = [round(x, 2) for x in f]
        print "miss type: %d(%f) %d(%f) %d(%f) %d(%f)" %(self.miss_partial, f[0], self.miss_seg, f[1], self.miss_nn, f[2], self.miss_other, f[3])


class Estimator():
    def __init__(self):
        self.segmentor = Segmentor()
        base_dir = 'lib/ltp_data_v3.4.0'
        # self.segmentor.load(os.path.join(base_dir, 'cws.model'))
        self.segmentor.load_with_lexicon(os.path.join(base_dir, 'cws.model'), os.path.join(rel_ext_dir, 'baike_dict_vertical_domain.txt'))

        self.postagger = Postagger()
        self.postagger.load(os.path.join(base_dir, 'pos.model'))

        self.ner_tagger = NamedEntityRecognizer()
        self.ner_tagger.load(os.path.join(base_dir, 'ner.model'))

        self.estimation = Estimation()

    def clear(self):
        self.estimation = Estimation()

    def estimate(self, sentence, entities):
        words = self.segmentor.segment(sentence)
        tags = self.postagger.postag(words)
        ner_tags = self.ner_tagger.recognize(words, tags)

        ner_entities = []
        for idx, ner_tag in enumerate(ner_tags):
            if ner_tag.startswith('S'):
                ner_entities.append((idx, idx + 1))
            elif ner_tag.startswith('B'):
                st = idx
            elif ner_tag.startswith('E'):
                ner_entities.append((st, idx + 1))
        
        

        ner_entity_names = set()
        for st, ed in ner_entities:
            ner_entity_names.add("".join(words[st:ed]))

        self.estimation.total_output += len(ner_entity_names)
        self.estimation.total_labeled += len(entities)

        entities_set = set(entities)
        for entity in ner_entity_names:
            if entity in entities_set:
                self.estimation.right += 1
            else:
                self.estimation.error += 1      

        # miss analysis
        for entity in entities:
            if entity in ner_entity_names:
                continue
            self.estimation.miss += 1
            if self.check_include(entity, ner_entity_names):
                self.estimation.miss_partial += 1
                print sentence
                print '\t%s' %(entity)
                print "\t".join(ner_entity_names)
                continue

            st, ed = self.find_pos(words, entity)
            if st == -1:
                self.estimation.miss_seg += 1
                continue
            if self.check_noun(tags, st, ed):
                self.estimation.miss_nn += 1
            else:
                self.estimation.miss_other += 1

                

        if self.estimation.miss + self.estimation.right != self.estimation.total_labeled:
            print sentence
            import sys
            sys.halt()
        if self.estimation.right + self.estimation.error != self.estimation.total_output:
            print sentence
            import sys
            sys.halt()
        
    def check_include(self, entity, reco_entities):
        entity  = entity.decode('utf-8')
        for reco_entity in reco_entities:
            reco_entity = reco_entity.decode('utf-8')
            if reco_entity.find(entity) != -1 or entity.find(reco_entity) != -1:
                return True
        return False

    def find_pos(self, words, entity):
        length = len(words)
        for st in range(length):
            for ed in range(st + 1, length + 1):
                string = "".join(words[st:ed])
                if len(string) > len(entity):
                    break
                if string == entity:
                    return st, ed
        return -1, -1

    def check_noun(self, tags, st, ed):
        noun_tags = set(['n', 'ni', 'nl', 'ns', 'nz'])
        for tag in tags[st:ed]:
            if not tag in noun_tags:
                return False
        return True
        
  

def read_data_from_file(filepath, datas_map):
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
                data.add(p[0], p[1])
            
            else:
                sentence = line
                data = Data(url, title, sentence)
                datas.append(data)
    datas_map[url] = datas

def read_data():
    datas_map = {}
    for filepath in glob.glob(data_dir + '/实体标注/*t*'):
        read_data_from_file(filepath, datas_map)
    
    est = Estimator()
    for key in sorted(datas_map.keys()):
        print "\n" * 3
        est.clear()
        print "%s 的分析结果" %key
        datas = datas_map[key]
        for data in datas:
            est.estimate(data.sentence, data.entities)
        result = est.estimation
        result.print_info()

    print "\n" * 3
    print "总的分析结果"
    est.clear()
    for datas in datas_map.values():
        for data in datas:
            est.estimate(data.sentence, data.entities)
    
    result = est.estimation
    result.print_info()

    



if __name__ == "__main__":
    # data = read_data()
    est = Estimator()
    print " ".join(est.segmentor.segment('《生活大爆炸》是一出美国情景喜剧，此剧由华纳兄弟电视公司和查克·洛尔制片公司共同制作。'))
    