from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer
import os

class LTPResult:
    def __init__(self, words, tags, ner_tags, arcs, sentence):
        self.words = words
        self.length = len(words)

        for arc in arcs:
            arc.head -= 1
            if arc.head == -1:
                arc.head = self.length

        self.tags = tags
        self.ner_tags = ner_tags
        self.arcs = arcs
        self.sentence = sentence
        self.words_st = self.find_pos()
        
        
    def find_pos(self):
        words_st = []
        st = 0
        for word in self.words:
            word_st = self.sentence.find(word, st)
            words_st.append(word_st)
            st = word_st
        return words_st

    def text(self, st, ed):
        if ed <= st:
            return ""
        return self.sentence[self.words_st[st]: self.words_st[ed-1] + len(self.words[ed-1])]

class LTP:
    def __init__(self, base_dir):
        if base_dir is None:
            base_dir = 'lib/ltp_data_v3.4.0'
        self.init(base_dir)

    def init(self, base_dir):
        segmentor_model = os.path.join(base_dir, 'cws.model')
        tagger_model = os.path.join(base_dir, 'pos.model')
        ner_model = os.path.join(base_dir, 'ner.model')
        parser_model = os.path.join(base_dir, 'parser.model')

        self.segmentor = Segmentor()
        self.segmentor.load(segmentor_model)

        self.tagger = Postagger()
        self.tagger.load(tagger_model)

        self.nertagger = NamedEntityRecognizer()
        self.nertagger.load(ner_model)

        self.parser = Parser()
        self.parser.load(parser_model)

    def parse(self, sentence):
        words = self.segmentor.segment(sentence)
        tags = self.tagger.postag(words)
        ner_tags = self.nertagger.recognize(words, tags)
        arcs = self.parser.parse(words, tags)
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




