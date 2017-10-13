#encoding:utf-8
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer
import os

class LTPResult:
    def __init__(self, words, tags, ner_tags, arcs, sentence):
        self.words = words
        self.length = len(words)
        
        self.tags = tags
        self.ner_tags = ner_tags

        if arcs is not None:
            for arc in arcs:
                arc.head -= 1
                if arc.head == -1:
                    arc.head = self.length
        self.arcs = arcs
        self.sentence = sentence
        if self.sentence is not None and self.words is not None:
            self.words_st = self.find_pos()
        
        
    def find_pos(self):
        words_st = []
        st = 0
        for word in self.words:
            word_st = self.sentence.find(word, st)
            words_st.append(word_st)
            st = word_st + len(word)
        return words_st

    def search_word(self, name, search_all = False):
        st_eds = []
        for i in range(0, self.length):
            for j in range(i + 1, self.length + 1):
                text = self.text(i, j)
                if text == name:
                    if search_all:
                        st_eds.append((i, j)) 
                    else:
                        return i, j
                if len(text) > name:
                    break
        if search_all:
            return st_eds
        else:
            return -1, -1
                    


    def text(self, st, ed):
        if ed <= st:
            return ""
        return self.sentence[self.words_st[st]: self.words_st[ed-1] + len(self.words[ed-1])]

    def update(self, new_words = None, new_tags = None, new_ner_tags = None):
        if new_words:
            self.words = new_words
        if new_tags:
            self.tags = new_tags
        if new_ner_tags:
            self.ner_tags = new_ner_tags
        self.length = len(self.words)
        self.words_st = self.find_pos()

    def update_parsing_tree(self, ltp):
        arcs = ltp.parser.parse(self.words, self.tags)
        arcs = list(arcs)
        for arc in arcs:
            arc.head -= 1
            if arc.head == -1:
                arc.head = self.length
        self.arcs = arcs

class LTP:
    def __init__(self, base_dir,is_custom_seg_dict = False):
        if base_dir is None:
            base_dir = 'lib/ltp_data_v3.4.0'
        self.init(base_dir,is_custom_seg_dict)

    def init(self, base_dir,is_custom_seg_dict):
        segmentor_model = os.path.join(base_dir, 'cws.model')
        tagger_model = os.path.join(base_dir, 'pos.model')
        ner_model = os.path.join(base_dir, 'ner.model')
        parser_model = os.path.join(base_dir, 'parser.model')
        custom_seg_dict = os.path.join(base_dir,'vertical_domain_baike_dict.txt')

        self.segmentor = Segmentor()
        if is_custom_seg_dict:
            self.segmentor.load_with_lexicon(segmentor_model,custom_seg_dict)
        else:
            self.segmentor.load(segmentor_model)

        self.tagger = Postagger()
        self.tagger.load(tagger_model)

        self.nertagger = NamedEntityRecognizer()
        self.nertagger.load(ner_model)

        self.parser = Parser()
        self.parser.load(parser_model)

    def parse(self, sentence):
        words = list(self.segmentor.segment(sentence))
        tags = list(self.tagger.postag(words))
        ner_tags = list(self.nertagger.recognize(words, tags))
        arcs = list(self.parser.parse(words, tags))
        result = LTPResult(words, tags, ner_tags, arcs, sentence)
        return result
        
if __name__ == "__main__":
    sentence = '《新媒体》，美国电影，J.J. Adler导演'
    # LTP参数就是模型的位置
    ltp = LTP('lib/ltp_data_v3.4.0')
    ltp_result = ltp.parse(sentence)
    for word, postag, nertag in zip(ltp_result.words, ltp_result.tags, ltp_result.ner_tags):
        print "%s %s %s" %(word, postag, nertag), 

    print '\n'
    print '-' * 50

    for idx, arc in enumerate(ltp_result.arcs):
        head = arc.head
        rel = arc.relation

        son_word = ltp_result.words[idx]
        if head == ltp_result.length:
            head_word = 'root'
        else:
            head_word = ltp_result.words[head]
        print "%s - %s : %s" %(son_word, head_word, rel)


    print '-' * 50 

    print ltp_result.text(0, 4)
    print ltp_result.text(8, 11)




