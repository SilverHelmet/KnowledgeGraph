#encoding: utf-8
from src.IOUtil import rel_ext_dir, Print, nb_lines_of
import os
from src.extractor.resource import Resource
from tqdm import tqdm
import json

class SummaryNameExtractor():
    def __init__(self):
        self.end_puncs = set([u'。', u'？',u'?', u'!', u'！', u';', u'；'])
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

    def find_extra_name(self, sent, first_name, names):
        rest_sent = sent[len(first_name):]
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

        right = second_name_pos[0]
        left = right
        while left > 0:
            char = rest_sent[left-1]
            if char in self.commas:
                break
            left -= 1
        if left == right:
            return None

        return first_name, rest_sent[left:right], second_name


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


        


if __name__ == "__main__":
    summary_path = os.path.join(rel_ext_dir, 'baike_summary.json')
    train_log_path = os.path.join(rel_ext_dir, 'extra_name/summary_extra_name.train.tsv')
    train_extract_summary_name(summary_path, train_log_path)
    