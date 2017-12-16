import os

from src.util import add_to_dict_cnt
from src.IOUtil import table_dir, Print

def is_sub_seq(sons, p):
    idx = 0
    for x in sons:
        while idx < len(p) and p[idx] != x:
            idx += 1
        if idx == len(p):
            return False
        idx += 1
    return True
         

def check_in(useful_cols, cols):
    for useful_columns in useful_cols:
        if is_sub_seq(cols, useful_columns):
            return True
    return False

def collect_table_cnt(cnt_path):
    Print("collect table cols cnt from [%s]" %os.path.basename(cnt_path))
    cols_cnt = {}
    for line in file(cnt_path):
        p = line.strip().split('\t')
        cols = p[2]
        add_to_dict_cnt(cols_cnt, cols)
    
    useful_cols = []
    for cols in sorted(cols_cnt.keys(), key = lambda x: (len(x), x), reverse = True):
        cnt = cols_cnt[col] 
        if cnt < 50:
            continue
        cols = cols.split(" # ")
        if not check_in(useful_cols, cols):
            useful_cols.append(cols)

        



        


if __name__ == "__main__":
    table_cnt_path = os.path.join(table_dir, 'table_column_count.tsv')
    collect_table_cnt(table_cnt_path)
