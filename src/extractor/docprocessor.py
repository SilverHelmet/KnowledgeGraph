#encoding: utf-8
from src.extractor.resource import Resource
from src.baike_process.process_page import split_sentences
from src.util import is_no_chinese
from src.IOUtil import rel_ext_dir
from src.extractor.ltp import LTPResult
from src.extractor.resource import Resource
from src.extractor.structure import PageInfo


class ParagraphInfo:
    def __init__(self, nb_sent, names, ename, is_summary, may_info_para):
        self.nb_sent = nb_sent
        self.sent_order = 0
        self.subj_miss_cnt = 0
        self.names = names
        self.ename = ename
        self.is_summary = is_summary
        self.may_info_para = may_info_para

class FakedArc:
    def __init__(self, head, relation):
        self.head = head 
        self.relation = relation

end_puncs = set(['。', '？','?', '!', '！', ';', '；'])
def strip_puncs(token):
    global end_puncs
    for punc in end_puncs:
        if token.endswith(punc):
            return token[:len(token) - len(punc)]
    return token

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
        elif para_info.nb_sent <= 10 and para_info.sent_order == para_info.subj_miss_cnt + 1:
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

    def check_info_para(self, sentence, para_info):
        if not para_info.may_info_para or para_info.nb_sent > 1:
            return None

        seps = [':', '：']
        used_sep = None
        for sep in seps:
            p = sentence.split(sep)
            if len(p) >= 2:
                used_sep = sep


        if not used_sep:
            return None

        p = sentence.split(used_sep)
        if len(p) > 2:
            return p

        pred = p[0].decode('utf-8')
        if len(pred) > 4 or len(pred) <= 1:
            return None
        
        p[1] = strip_puncs(p[1].strip()).strip()
        
        obj = p[1].decode('utf-8')
        if not is_no_chinese(obj) and len(obj) >= 12:
            return None
        if len(obj) >= 40 or len(obj) == 0:
            return None

        return p

    def fake_ltp_result_with_info_para(self, tokens, para_info):
        
        tokens.insert(0, para_info.ename)
        tokens = [token.strip() for token in tokens]
        tags = ['nz', 'v', 'nz']
        ner_tags = ['S-Nz', 'O', 'S-Nz']
        
        arcs = []
        arcs.append(FakedArc(2, "SBV"))
        arcs.append(FakedArc(0, "HEAD"))
        arcs.append(FakedArc(2, "VOB"))

        sentence = "".join(tokens)

        ltp_result = LTPResult(tokens, tags, ner_tags, arcs, sentence)

        return ltp_result
        
        



    def parse_sentence(self, sentence, para_info):
        para_info.sent_order += 1
        if type(sentence) is unicode:
            sentence = sentence.encode('utf-8')
        sentence = sentence.replace("•", '·').strip()

        tokens = self.check_info_para(sentence, para_info)
        is_para_info = tokens is not None

        if tokens is not None and len(tokens) == 2:
            ltp_result = self.fake_ltp_result_with_info_para(tokens, para_info)
            return ltp_result, is_para_info

        ltp_result = self.ltp.parse(sentence, parse_tree = False)
        
        miss = self.check_subj_miss(ltp_result, para_info)
        
        if miss:
            para_info.subj_miss_cnt += 1

        ltp_result.update_parsing_tree(self.ltp)

        return ltp_result, is_para_info

    def parse_chapter(self, title, paragraphs, page_info):
        names = page_info.names
        ename = page_info.ename
        if title == 'intro_summary':
            is_summary = True
        else:
            is_summary = False


        may_info_para = True
        for paragraph in paragraphs:
            sentences = split_sentences(paragraph)
            
            para_info = ParagraphInfo(len(sentences), names, ename, is_summary, may_info_para)

            for sentence in sentences:
                pre_miss = para_info.subj_miss_cnt
                ltp_result, may_info_para = self.parse_sentence(sentence, para_info)
                subj_miss = may_info_para or para_info.subj_miss_cnt == pre_miss+1
                yield ltp_result, subj_miss
        
        

def test_sentence():
    para_info = ParagraphInfo(1, ['方文山'], '方文山', False, True)
    doc_processor = DocProcessor()
    s = u'1989年创刊，最初免费赠给500万任天堂“游戏人间”俱乐部的会员，以后改为月刊，现已成为全美销售量最大的儿童读物，1990年时已拥有600万读者。'

    sentences = split_sentences(s)
    # ner = NamedEntityReg()
    for sent in sentences:
        print sent
        pre_miss = para_info.subj_miss_cnt

        ltp_result, is_para_info = doc_processor.parse_sentence(sent, para_info)

        subj_miss = is_para_info or para_info.subj_miss_cnt == pre_miss+1
        if subj_miss:
            print 'subj miss'
        print '\t%s' %ltp_result.sentence
        print ""
        for word, tag, ner_tag in zip(ltp_result.words, ltp_result.tags, ltp_result.ner_tags):
            print "%s:%s:%s" %(word, tag, ner_tag),
        print ""
        print ""

        words = ltp_result.words + ['root']
        for idx, arc in enumerate(ltp_result.arcs, start = 0):
            head, rel = arc.head, arc.relation
            print "%s-%s:%s" %(words[idx], words[head], rel)

        # es = ner.recognize(ltp_result.sentence, ltp_result, None, None)
        # for e in es:
        #     print ltp_result.text(e.st, e.ed), e.etype    

def test_chapt():
    import json
    import os
    urls = ['baike.so.com/doc/1287918-1361771.html', 'baike.so.com/doc/4835393-5052275.html', 
    'baike.so.com/doc/2526484-2669235.html', 'baike.so.com/doc/5382393-5618748.html', 
    'baike.so.com/doc/6662392-6876216.html', 'baike.so.com/doc/3056594-3221987.html']

    # urls = ["baike.so.com/doc/1287918-1361771.html"]
    resource = Resource.get_singleton()
    url2names = resource.get_url2names()

    baike_doc_path = os.path.join(rel_ext_dir, 'baike_doc.json')
    doc_processor = DocProcessor()
    
    for line in file(baike_doc_path):
        url, doc = line.split('\t')
        if not url in urls:
            continue
        doc = json.loads(doc)
        names = url2names[url]
        ename = names[0]
        page_info = PageInfo(ename, names, url, None)
    
        for chapter_title, chapter in doc:
            print 'parsing %s' %chapter_title
            for ltp_result, subj_miss in doc_processor.parse_chapter(chapter_title, chapter, page_info):
                # print '\t' + ltp_result.sentence
                if subj_miss:
                    print "\t\t" + ltp_result.sentence

        



if __name__ == "__main__":
    test_chapt()   
    # test_sentence() 

        

