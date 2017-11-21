#encoding: utf-8
from src.IOUtil import rel_ext_dir, Print, nb_lines_of
import os
from src.extractor.resource import Resource
from tqdm import tqdm
import json

class SummaryNameExtractor():
    def __init__(self):
        self.end_puncs = set([u'。', u'？',u'?', u'!', u'！', u';', u'；'])
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


def debug():
    s = u'易行，全称为易行实战销售训练机构，'
    s = u'瓦哈巴英文名:Ben Vahaba'
    ext = SummaryNameExtractor()
    summary = u'瓦哈巴英文名:Ben Vahaba生日:1992-03-27场上位置:后卫惯用脚:右脚个人资料代表国家队:出场0次，进0球欧洲三大杯:出场2次，进0球欧洲冠军联赛:出场0次，进0球职业生涯比赛日期比赛性质代表球队对手球队主客场比分出场时间状态进球得牌分析2012-08-22欧冠谢莫纳镇工人鲍里索夫客场0:253首发0 [析]2012-07-24欧冠谢莫纳镇工人日利纳主场2:05替补0 [析]'
    print " ".join(ext.find_extra_name(s[3:], u'瓦哈巴', [u'瓦哈巴',u'Ben Vahaba']))


if __name__ == "__main__":
    summary_path = os.path.join(rel_ext_dir, 'baike_summary.json')
    train_log_path = os.path.join(rel_ext_dir, 'extra_name/summary_extra_name.train.tsv')
    train_extract_summary_name(summary_path, train_log_path)

    
    