#encoding: utf-8
from src.extractor.resource import Resource
from src.baike_process.process_page import split_sentences
from src.util import is_no_chinese
from src.IOUtil import rel_ext_dir
from src.extractor.ltp import LTPResult
from src.extractor.resource import Resource
from src.extractor.structure import PageInfo
from entity.ner import NamedEntityReg


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
    def __init__(self, ner = None):
        self.ner = ner
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
        sentence = sentence.replace("•", '·').replace('　','').strip()
        if len(sentence) == 0:
            return None, False

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

    def parse_chapter(self, title, paragraphs, page_info, parse_ner = False):
        if parse_ner and self.ner is None:
            self.ner = NamedEntityReg()

        names = page_info.names
        ename = page_info.ename
        if title == 'intro_summary':
            is_summary = True
        else:
            is_summary = False


        may_info_para = True
        for paragraph in paragraphs:
            if type(paragraph) == str:
                paragraph = paragraph.decode('utf-8')
            sentences = split_sentences(paragraph)
            
            para_info = ParagraphInfo(len(sentences), names, ename, is_summary, may_info_para)

            for sentence in sentences:
                pre_miss = para_info.subj_miss_cnt
                ltp_result, may_info_para = self.parse_sentence(sentence, para_info)

                subj_miss = may_info_para or para_info.subj_miss_cnt == pre_miss+1

                if not self.ner:
                    yield ltp_result, subj_miss
                else:
                    if ltp_result is None:
                        yield ltp_result, [], False
                        continue
                    str_entities = self.ner.recognize(ltp_result.sentence, ltp_result, page_info)
                    new_ename = self.check_new_subj(para_info, ltp_result, str_entities)
                    if new_ename:
                        # print 'change subj to %s' %new_ename
                        ename = new_ename
                        names = [new_ename]
                    yield ltp_result, str_entities, subj_miss

    def check_new_subj(self, para_info, ltp_result, str_entities):
        if para_info.nb_sent != 1:
            return None

        if len(str_entities) != 1:
            return None

        entity = str_entities[0]
        st = entity.st
        ed = entity.ed

        valid = True
        for i in range(ltp_result.length):
            if i >= st and i < ed:
                continue
            if ltp_result.tags[i] == 'wp':
                continue
            valid = False
            break
        if not valid:
            return None
        return ltp_result.text(st, ed)

        
        

def test_sentence():
    para_info = ParagraphInfo(10, ['方文山'], '方文山', True, True)
    doc_processor = DocProcessor()
    s = u'中国皮划艇激流回旋队 领队:韩建国 男队组成:胡明海、舒俊榕、黄存光、滕志强 女队组成:李晶晶参赛情况本次2012年伦敦奥运会上，中国皮划艇激流回旋队由5人组成。明星男队胡明海胡明海，出生于1989年4月19日，中国皮划艇激流回旋项目运动员。在2008年皮划艇激流回旋澳大利亚公开赛暨2008年北京奥运会大洋洲资格赛中，胡明海和舒俊榕爆大冷击败了那一对占据霸主地位多年的斯洛伐克孪生兄弟组合，一举夺得了男子双人划艇的金牌。这样的成绩，让国际划联激流委员会主席布鲁诺在接受采访时都不禁连称，中国激流运动员的竞技水平进步神速，让人难以置信。在即将到来的2012年伦敦奥运会上，他将向奖牌冲击。舒俊榕舒俊榕，中国皮划艇激流队队员，曾拿到过2008年澳大利亚公开赛第一，2008年世界杯赛第二，雅典奥运会冠军等历史性荣誉。黄存光黄存光，福建省三明市将乐县余坊乡人，小的时候在余坊中心校就读，因体能出众，被选入三明市体校参加训练，2002年选入福建省激流皮划艇队参加训练2005年，年仅20岁的他就入选国家皮划艇激流回旋运动队。滕志强滕志强，湖南怀化人，1991年10月26日出生，皮划艇激流回旋运动员。'

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

        # words = ltp_result.words + ['root']
        # for idx, arc in enumerate(ltp_result.arcs, start = 0):
        #     head, rel = arc.head, arc.relation
        #     print "%s-%s:%s" %(words[idx], words[head], rel)

        # es = ner.recognize(ltp_result.sentence, ltp_result, None, None)
        # for e in es:
        #     print ltp_result.text(e.st, e.ed), e.etype    

def test_chapt():
    import json
    import os
    urls = ['baike.so.com/doc/1287918-1361771.html', 'baike.so.com/doc/4835393-5052275.html', 
    'baike.so.com/doc/2526484-2669235.html', 'baike.so.com/doc/5382393-5618748.html', 
    'baike.so.com/doc/6662392-6876216.html', 'baike.so.com/doc/3056594-3221987.html',
    'baike.so.com/doc/8716294-9038723.html', 'baike.so.com/doc/5390356-5627004.html']

    # urls = ["baike.so.com/doc/1287918-1361771.html"]
    resource = Resource.get_singleton()
    url2names = resource.get_url2names()
    baike_info_map = resource.get_baike_info()

    baike_doc_path = os.path.join(rel_ext_dir, 'baike_doc.json')
    doc_processor = DocProcessor()
    
    for line in file(baike_doc_path):
        url, doc = line.split('\t')
        if not url in urls:
            continue
        doc = json.loads(doc)
        names = url2names[url]
        ename = names[0]
        types = baike_info_map[url].types
        page_info = PageInfo(ename, names, url, [], types)
        print " ".join(page_info.names)
    
        for chapter_title, chapter in doc:
            print 'parsing %s' %chapter_title
            for ltp_result, str_entities, subj_miss in doc_processor.parse_chapter(chapter_title, chapter, page_info, parse_ner = True):
                # print '\t' + ltp_result.sentence
                if subj_miss:
                    print "\t\t" + ltp_result.sentence

        



if __name__ == "__main__":
    test_chapt()   
    # test_sentence() 

        

