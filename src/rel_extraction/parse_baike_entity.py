#encoding: utf-8
import jieba
import jieba.posseg as pseg
from ..mapping.fb_date import BaikeDatetime

end_puncs = set([u'。', u'？',u'?', u'!', u'！', u';', u'；'])
def split_lines(text):
    global end_puncs
    lines = []
    st = 0
    pos = 0
    ed = len(text)
    while pos < ed:
        if text[pos] in end_puncs or pos - st >= 100:
            lines.append((text[st:pos+1]))
            st = pos+1
        pos += 1
    if st < ed:
        lines.append(text[st:])
    return lines

class TimeParser:
    time_flags = set([u't', u'm', u'x'])

    @staticmethod
    def check_flags(flags, st, ed):
        for idx in range(st, ed):
            if flags[idx] not in TimeParser.time_flags:
                return False
        return True

    @staticmethod
    def parse(words, flags):
        st = 0
        length = len(words)
        rets = []
        while st < length:

            if flags[st] not in TimeParser.time_flags:
                st += 1
                continue

            ed = length
            while st < ed:
                if TimeParser.check_flags(flags, st, ed):
                    text = "".join(words[st:ed])
                    time_obj = BaikeDatetime.parse(text, strict = True)
                    if time_obj is not None:
                        rets.append((st, ed, time_obj, 'time'))
                        st = ed
                        break
                ed -= 1
            st += 1
        return rets

class EntityParser:
    entity_flags = set(['baike', 'ns', 'nt', 'nr', 'nz', 'nrt'])

    @staticmethod
    def parse(words, flags):
        ret = []
        idx = 0
        for word, flag in zip(words, flags):
            if flag in EntityParser.entity_flags:
                ret.append((idx, idx+1, word, 'baike'))
            idx += 1
        return ret

def parse_sentence(words, flags):        
    objs = []
    objs.extend(TimeParser.parse(words, flags))
    objs.extend(EntityParser.parse(words, flags))
    return objs


if __name__ == "__main__":
    s = u'刘德华出生于1993年11月29日。'
    parse_line(s)
    # print BaikeDatetime.parse(u'1993年11月29日', strict = True)
