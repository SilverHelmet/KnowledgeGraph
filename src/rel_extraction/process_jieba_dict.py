import jieba
from jieba.posseg import pseg
from ..IOUtil import rel_ext_dir, nb_lines_of
import os
import res
from tqdm import tqdm

if __name__ == "__main__":
    dict_path = os.path.join(rel_ext_dir, 'baike_dict.txt')
    processed_path = os.path.join(rel_ext_dir, 'trimmed_baike_dict.txt')
    re_eng = re.compile("^[a-zA-Z0-9]+$")

    outf = file(processed_path, 'w')
    for line in tqdm(file(dict_path), total = nb_lines_of(dict_path)):
        word, freq, tag = line.strip().decode('utf-8').split(' ')
        if re_eng.match(word):
            outf.write(line)
            continue
        words = pseg.cut(word)
        words = [x[0] for x in words]
        if len(words) != 1:
            outf.write(line)
    outf.close()

