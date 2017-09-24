import jieba
import jieba.posseg as pseg
from ..IOUtil import rel_ext_dir, nb_lines_of
import os
import re
from tqdm import tqdm

if __name__ == "__main__":
    dict_path = os.path.join(rel_ext_dir, 'baike_dict.txt')
    processed_path = os.path.join(rel_ext_dir, 'trimmed_baike_dict.txt')
    re_eng = re.compile(r"^[a-zA-Z]+$")
    re_digit = re.compile(r'^[0-9+-=!?]+$')

    outf = file(processed_path, 'w')
    for line in tqdm(file(dict_path), total = nb_lines_of(dict_path)):
        word, freq, tag = line.strip().decode('utf-8').split(' ')
        if re_digit.match(word):
            continue
        words = [x for x in jieba.cut(word)]
        if len(words) != 1:
            outf.write(line)
        elif re_eng.match(word):
            outf.write(line)
    outf.close()

