#encoding: utf-8
from src.extractor.resource import Resource
from src.baike_process.process_page import split_sentences

class ParagraphInfo:
    def __init__(self, nb_sent, names, ename, is_summary):
        self.nb_sent = nb_sent
        self.sent_order = 0
        self.subj_miss_cnt = 0
        self.names = names
        self.ename = ename
        self.is_summary = is_summary


class DocProcessor:
    def __init__(self):
        self.ltp = Resource.get_singleton().get_ltp()
        self.subj_miss_patterns = [
            ['p', '《'],
            ['p', 'n'],
            ['p', 'j'],
            ['p', 'v'],
            ['v'],
            ['a', 'v'],
            ['d', 'v'],
        ]

    def get_start_nt(self, ltp_result):
        pos = 0
        wp_cnt = 0
        nt_cnt = 0
        while pos < ltp_result.length:
            postag = ltp_result.tags[pos]
            if postag == 'wp':
                pos += 1
                wp_cnt += 1
                if wp_cnt >= 2:
                    return 0, 0, 0
            elif postag == 'nt':
                nt_cnt += 1
                pos += 1
            else:
                break
        return pos, wp_cnt, nt_cnt

    def match(self, ltp_result, pos, pattern):
        for i in range(pos, pos + len(pattern)):
            if i >= ltp_result.length:
                return False
            if ltp_result.tags[i] == 'nt':
                return False

            valid = False
        
            if ltp_result.tags[i][0] == pattern[i - pos]:
                valid = True
            elif ltp_result.words[i] == pattern[i - pos]:
                valid = True
            if not valid:
                return False
        return True

    def check_subj_miss(self, ltp_result, para_info):

        check_flag = False
        if para_info.is_summary:
            check_flag = True
        elif para_info.nb_sent <= 3 and para_info.sent_order == para_info.subj_miss_cnt + 1:
            check_flag = True
        if not check_flag:
            return False
        nt_ed, wp_cnt, nt_cnt = self.get_start_nt(ltp_result)
        
        nt_flag = False
        if nt_cnt > 0:
            nt_flag = True
        elif para_info.is_summary:
            nt_flag = True

        if not nt_flag:
            return False
        
        for name in para_info.names:
            if name in ltp_result.sentence:
                return False
        miss = False
        for parttern in self.subj_miss_patterns:
            if self.match(ltp_result, nt_ed, parttern):
                miss = True
                break

        if miss:
            ltp_result.insert_word(nt_ed, para_info.ename, 'nz', 'S-Nz')
        return miss
    
    def process(self, sentence, para_info):
        para_info.sent_order += 1
        if type(sentence) is unicode:
            sentence = sentence.encode('utf-8')
        sentence = sentence.replace("•", '·')

        ltp_result = self.ltp.parse(sentence, parse_tree = False)

        
        
        miss = self.check_subj_miss(ltp_result, para_info)
        
        if miss:
            para_info.subj_miss_cnt += 1

        ltp_result.update_parsing_tree(self.ltp)

        return ltp_result


if __name__ == "__main__":
    para_info = ParagraphInfo(3, ['方文山'], '方文山', False)
    doc_processor = DocProcessor()
    s = u'2001年因创作歌曲《娘子》提名第12届金曲奖最佳作词人奖。2003年凭借创作的歌曲《威廉古堡》获得第十二届金曲奖最佳作词人，同年创作的歌曲《直来直往》获得第三届香港音乐风云榜港台年度最佳填词奖。2005年出版书籍《演好你自己的偶像剧》。2008年获得第十九届台湾金曲奖最佳作词人，同年出版《青花瓷：隐藏在釉色里的文字秘密》，并参演舞台剧 《六义帮》。2010年出版《方道·文山流》，参演电影 《混混天团》。  2011年出版书籍《亲爱的，我们活在最好的年代》，同年参演电视剧 《冲吧宅男》和执导《中国风演唱会》南昌站。2013年执导电影处女作《听见下雨的声音》。'

    sentences = split_sentences(s)
    for sent in sentences:
        print sent
        ltp_result = doc_processor.process(sent, para_info)

        print '\t%s' %ltp_result.sentence
        print ""
        for word, tag, ner_tag in zip(ltp_result.words, ltp_result.tags, ltp_result.ner_tags):
            print "%s:%s:%s" %(word, tag, ner_tag),
        print ""
        print ""
