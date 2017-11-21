#encoding: utf-8
from src.IOUtil import rel_ext_dir, Print, nb_lines_of
import os
from src.extractor.resource import Resource
from tqdm import tqdm
import json

class SummaryNameExtractor():
    def __init__(self):
        self.end_puncs = set([u'。', u'？',u'?', u'!', u'！', u';', u'；', '\n'])
        self.other_puncs = set([u'、'])
        self.commas = [u',', u'，']
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

def collect_keyword(train_log_path, outpath):
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

    train_extract_summary_name(summary_path, train_log_path)

    # collect_keyword(train_log_path, keyword_path)

    # debug()

    
    