#encoding: utf-8
import jieba
import jieba.posseg as pseg
import os
from ..IOUtil import result_dir
from ..rel_extraction.parse_baike_entity import split_sentences

class SimpleExtractor:
    def __init__(self):
        self.sentence_splitter = split_sentences
        self.init()
    
    def init(self):
        pass

        

    def parse(self, paragraph):
        if type(paragraph) is str:
            paragraph = paragraph.decode('utf-8')

        sentences = self.sentence_splitter(paragraph)
        ret = {}
        for sentence in sentences:
            result = self.parse_sentence(sentence)
            if result:
                ret[sentence] = ret

    def parse_sentence(sentence):
        res = pseg.cut(sentence)
        words = []
        flags = []
        for word, flag in res:
            print word, flag


if __name__ == "__main__":
    s = u'刘德华（Andy Lau），1961年9月出生于中国香港，中国知名演员、歌手、词作人、制片人、电影人，影视歌多栖发展的代表艺人之一。'
    for word, flag in pseg.cut(s):
        print "%s:%s" %(word, flag),