#encoding: utf-8
import jieba.posseg as pseg

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

def parse_time(words):
    for word, 

def parse_line(text):        
    words = pseg.cut(text)
    time_span = parse_time(words)


def parse_entity():


if __name__ == "__main__":
    s = '刘德华出生于1993年11月29日'
