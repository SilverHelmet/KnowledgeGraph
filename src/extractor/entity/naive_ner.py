#encoding: utf-8
from ..ltp import LTP, LTPResult

class NaiveNer:
    def __init__(self):
        pass

    def recognize(self, sentence, ltp_result, page_info):
        entities = []
        for idx, ner_tag in enumerate(ltp_result.ner_tags):
            if ner_tag.startswith('S'):
                entities.append((idx, idx + 1))
            elif ner_tag.startswith('B'):
                st = idx
            elif ner_tag.startswith('E'):
                entities.append((st, idx + 1))
        return entities


if __name__ == "__main__":
    ner = NaiveNer()
    ltp = LTP(None)
    sentence = '2004年，刘德华先与导演张艺谋合作武侠片《远古谜团》，而后又与导演冯小刚合作《天下无贼》，在票房上获得不错的成绩。'
    ltp_result = ltp.parse(sentence)
    entities = ner.recognize(sentence, ltp_result, None)
    for st, ed in entities:
        print ltp_result.text(st, ed)



