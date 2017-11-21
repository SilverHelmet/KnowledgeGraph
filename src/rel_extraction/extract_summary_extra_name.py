#encoding: utf-8
from src.IOUtil import rel_ext_dir, Print, nb_lines_of, load_file
from src.baike_process.process_page import split_sentences
import os
from src.extractor.resource import Resource
from tqdm import tqdm
import json

class SummaryNameExtractor():
    def __init__(self):
        self.end_puncs = set([u'。', u'？',u'?', u'!', u'！', u';', u'；', '\n'])
        self.other_puncs = set([u'、'])
        self.commas = [u',', u'，']

        self.puncs = []
        self.puncs.extend(self.end_puncs)
        self.puncs.extend(self.other_puncs)
        self.puncs.extend(self.commas)

        self.left_brackets = [u'(', u'（']
        self.right_brackets = [u')', u'）']
        self.max_comma = 3
        self.max_length = 100

    def find_name_sentence(self, summary, names):
        summary = summary.replace(u'（', '(').replace(u'）', u')')
        max_len_name = u""
        for name in names:
            if summary.startswith(name) and len(name) > len(max_len_name):
                max_len_name = name
        
        if len(max_len_name) == 0:
            return None

        st = len(max_len_name)
        

        in_bracket = False
        length = len(summary)
        chars = []
        comma = 0

        
        for i in range(st, length):
            if i == self.max_length:
                return None
            char = summary[i]
            if char in self.left_brackets:
                in_bracket = True

            if not in_bracket:
                chars.append(char)

            if char in self.right_brackets:
                in_bracket = False

            if in_bracket:
                continue

            if char in self.commas:
                comma += 1 
                if comma == self.max_comma:
                    break
            if char in self.end_puncs:
                break
        return "".join(chars), max_len_name

    def find_extra_name(self, rest_sent, first_name, names):
        # rest_sent = sent[len(first_name):]
        second_name_pos = (10000, 0)
        for name in names:
            pos = rest_sent.find(name)
            if pos == -1:
                continue
            if pos < second_name_pos[0]:
                second_name_pos = (pos, len(name))

        if second_name_pos[0] == 10000:
            return None

        second_name = rest_sent[second_name_pos[0]:second_name_pos[0] + second_name_pos[1]]

        if second_name == first_name:
            return None

        ed = second_name_pos[0] + second_name_pos[1]
        if ed >= len(rest_sent):
            return None
        if rest_sent[ed] not in self.end_puncs and rest_sent[ed] not in self.commas and not rest_sent[ed] in self.other_puncs:
            return None

        right = second_name_pos[0]
        left = right
        while left > 0:
            char = rest_sent[left-1]
            if char in self.commas:
                break
            left -= 1
        if left == right:
            return None

        name_pred_sent = rest_sent[left:right].strip()
        if len(name_pred_sent) == 0:
            return None

        return first_name, name_pred_sent, second_name

    def find_only_key(self, mapped_keys):
        max_len_key = u''
        for key in mapped_keys:
            if len(key) > len(max_len_key):
                max_len_key = key
            
        if len(max_len_key) == 0:
            return None

        for key in mapped_keys:
            if not key in max_len_key:
                return None
        return max_len_key

    def get_extra_name_from_key(self, sentence, key):
        st = sentence.find(key) + len(key)
        length = len(sentence)
        ed = st
        while ed < length:
            if ed - st >= 50:
                return None
            char = sentence[ed]
            if char in self.puncs:
                break
            ed += 1
        return sentence[st:ed]

    def find_no_subj_name(self, summary, keywords):
        mapped_keys = set()
        for key in keywords:
            if summary.startswith(key):
                mapped_keys.add(key)

        mapped_key = self.find_only_key(mapped_keys)
        if mapped_key is None:
            return None

        return self.get_extra_name_from_key(summary, mapped_key)

    def find_new_extra_name(self, rest_sentence, keywords):
        mapped_keys = set()
        for key in keywords:
            if rest_sentence.find(key) != -1:
                mapped_keys.add(key)

        mapped_key = self.find_only_key(mapped_keys)
        if mapped_key is None:
            return None
        pos = rest_sentence.find(mapped_key)
        if pos > 15:
            return None

        extra_name = self.get_extra_name_from_key(rest_sentence, mapped_key)
        if len(extra_name) == 0:
            return None
        if extra_name is not None and mapped_key in extra_name:
            return None
        return extra_name





def train_extract_summary_name(summary_path, out_path):
    outf = file(out_path, 'w')
    url2names = Resource.get_singleton().get_url2names()
    extor = SummaryNameExtractor()
    Print('train summary extra name')
    for line in tqdm(file(summary_path), total = nb_lines_of(summary_path)):
        url, summary = line.split('\t')
        summary = json.loads(summary)['summary']
        names = url2names[url]
        names = [x.decode('utf-8') for x in names]

        ret = extor.find_name_sentence(summary, names)
        if ret is None:
            continue
        sent, first_name = ret

        ret = extor.find_extra_name(sent, first_name, names)

        
        if ret is None:
            continue
        
        first_name, sent, second_name = ret
        outs = [url, first_name, sent, second_name]
        outf.write('%s\n' %('\t'.join(outs)))
    outf.close()

def collect_keyword(train_log_path, outpath, limit):
    outf = file(outpath, 'w')
    keyword_cnts = {}
    for line in file(train_log_path):
        p = line.split('\t')
        if len(p) != 4:
            print line
        keyword = p[2].strip()
        if not keyword in keyword_cnts:
            keyword_cnts[keyword] = 0
        keyword_cnts[keyword] += 1
    
    for key in sorted(keyword_cnts.keys(), key = lambda x: keyword_cnts[x], reverse = True):
        cnt = keyword_cnts[key]
        if cnt >= 10:
            outf.write("%s\t%d\n" %(key, cnt))
        
    outf.close()

def load_keywords(error_path, keyword_path, limit):
    good_ends = [u'是',u':', u'为', u'：']
    error_keys = load_file(error_keyword_path)
    error_keys = set([x.decode('utf-8') for x in error_keys])
    
    keys = set()
    last_words = set()
    for line in file(keyword_path):
        p = line.split('\t')
        key = p[0].decode('utf-8')
        if len(key) < 2:
            continue
        if key in error_keys:
            continue
        cnt = int(p[1])
        if cnt < limit:
            continue
        keys.add(key)
        last_words.add(key[-1])
    extra_keys = set()
    for key in keys:
        is_good_end = False
        for end in good_ends:
            if key.endswith(end):
                is_good_end = True
        if is_good_end:
            continue
        for end in good_ends:
            extra_keys.add(key + end)
    keys.update(extra_keys)


    return keys

def extract_summary_name(summary_path, keywords, outpath):
    Print('extract extra name from ')
    url2names = Resource.get_singleton().get_url2names()
    ext = SummaryNameExtractor()
    outf = file(outpath, 'w')
    for line in tqdm(file(summary_path), total = nb_lines_of(summary_path)):
        url, summary = line.split('\t')
        summary = json.loads(summary)['summary']
        summary = summary.replace(u'（', '(').replace(u'）', u')')

        names = url2names[url]
        names = [x.decode('utf-8') for x in names]
        ret = ext.find_name_sentence(summary, names)
        if ret is None:
            extra_name = None
            sentences = split_sentences(summary)
            if len(sentences) > 0:
                first_sentence = sentences[0]
                no_subj = True
                for name in names:
                    if name in first_sentence:
                        no_subj = False
                if no_subj:
                    extra_name = ext.find_no_subj_name(summary, keywords)
        else:
            rest_sentence, first_name = ret
            extra_name = ext.find_new_extra_name(rest_sentence, keywords)

        
        if extra_name is not None:
            extra_name = extra_name.strip('\'" \t\n')
            if not extra_name in names:
                outf.write('%s\t%s\n' %(url, extra_name))
    outf.close()    
        
    

def debug():
    s = u'4-硝基苯酚甲酯，英文名为\n4-Nitrophenyl formate，又名\n甲酸对硝基苯酯，CAS登记号为1865-01-6，分子式是C7H5NO4，分子量为167.1189，化工中间体一种。'
    names = [u'4-硝基苯酚甲酯', u'4-Nitrophenyl formate']
    ext = SummaryNameExtractor()
    rest_sent, first_name = ext.find_name_sentence(s, names)
    print rest_sent
    print first_name
    ret = ext.find_extra_name(rest_sent, first_name, names)
    if ret:
        first_name, sent_name, second_name = ret
        print first_name, sent_name, second_name


if __name__ == "__main__":
    summary_path = os.path.join(rel_ext_dir, 'baike_summary.json')
    train_log_path = os.path.join(rel_ext_dir, 'extra_name/summary_extra_name.train.tsv')
    keyword_path = os.path.join(rel_ext_dir, 'extra_name/summary_name_key_word_cnt.tsv')
    error_keyword_path = os.path.join(rel_ext_dir, 'extra_name/error_keys.txt')
    new_extra_name_path = os.path.join(rel_ext_dir, 'extra_name/summary_extra_name.tsv')
    # debug()

    # train_extract_summary_name(summary_path, train_log_path)

    collect_keyword(train_log_path, keyword_path, 10)

    keywords = load_keywords(error_keyword_path, keyword_path, 10)
    extract_summary_name(summary_path, keywords, new_extra_name_path)

    

    
    