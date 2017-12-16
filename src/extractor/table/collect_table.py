import json
import os

from src.extractor.resource import Resource
from src.IOUtil import Print, table_dir
from src.util import add_to_dict_cnt


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

def load_local_info(path, cnt_path):
    if not os.path.exists(path):
        outf = file(path, 'w')
        bk_info_map = Resource.get_singleton().get_baike_info()
        for line in file(cnt_path):
            bk_url = line.split('\t')[0]
            types = bk_info_map[bk_url].types
            info = {"types": types}
            outf.write("%s\t%s\n" %(bk_url, json.dumps(info)) )
        outf.close()

    local_info = {}
    for line in file(path):
        bk_url, info = line.split('\t')
        local_info[bk_url] = json.loads(info)
    return local_info
        







def collect_table_cnt(cnt_path, outpath):
    Print("collect table cols cnt from [%s], write to [%s]" %(os.path.basename(cnt_path), os.path.basename(outpath)))
    cols_cnt = {}
    for line in file(cnt_path):
        p = line.strip().split('\t')
        cols = p[2]
        add_to_dict_cnt(cols_cnt, cols)
    
    useful_cols = []
    outf = file(outpath, 'w')
    for cols in sorted(cols_cnt.keys(), key = lambda x: (len(x), x), reverse = True):
        cnt = cols_cnt[cols] 
        if cnt < 40:
            continue
        cols = cols.split(" # ")
        if not check_in(useful_cols, cols):
            useful_cols.append(cols)
            outf.write("%s\t%d\n" %(" # ".join(cols), cnt))
    outf.close()

if __name__ == "__main__":
    table_cnt_path = os.path.join(table_dir, 'table_column_count.tsv')
    outpath = os.path.join(table_dir, 'frequent_table_cols.tsv')

    local_type_info_path = os.path.join(table_dir, 'local_info.json')
    local_info = load_local_info(local_type_info_path, table_cnt_path)
    # collect_table_cnt(table_cnt_path, outpath)
