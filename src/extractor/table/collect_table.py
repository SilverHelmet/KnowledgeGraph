#encoding:utf-8
import json
import os

from src.extractor.resource import Resource
from src.IOUtil import Print, table_dir
from src.util import add_to_dict_cnt, topk_keys


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
        



def collect_tables(cnt_path, local_info):
    cols_cnt = {}
    cols_type_cnt = {}
    cols_title_cnt = {}
    for line in file(cnt_path):
        p = line.strip().split('\t')
        bk_url = p[0]
        titles = p[1]
        cols = p[2]
        add_to_dict_cnt(cols_cnt, cols)
        
        if not cols in cols_type_cnt:
            cols_type_cnt[cols] = {}
            cols_title_cnt[cols] = {}
        type_cnt = cols_type_cnt[cols]

        types = local_info[bk_url]['types']
        # if cols == '获奖时间 # 奖项名称 # 获奖作品 # 备注' and not 'fb:people.person' in types:
        #     print bk_url
        for fb_type in types:
            add_to_dict_cnt(type_cnt, fb_type)

        title = p[1].split("_")[-1]
        add_to_dict_cnt(cols_title_cnt[cols], title)

    return cols_cnt, cols_type_cnt, cols_title_cnt

def collect_table_cnt(cnt_path, outpath, local_info):
    Print("collect table cols cnt from [%s], write to [%s]" %(os.path.basename(cnt_path), os.path.basename(outpath)))
    cols_cnt, cols_type_cnt, cols_title_cnt = collect_tables(cnt_path, local_info)

    outf = file(outpath, 'w')
    useful_cols = []
    total = 0
    for cols in sorted(cols_cnt.keys(), key = lambda x: (len(x), x), reverse = True):
        cols_obj = cols.split(" # ")
        if not check_in(useful_cols, cols_obj):
            if cols_cnt[cols]  < 20:
                continue
            total += cols_cnt[cols]
            useful_cols.append(cols_obj)
            
            types_cnt = topk_keys(cols_type_cnt[cols], 8)
            titles_cnt = topk_keys(cols_title_cnt[cols], 4)
            types_str = " ".join([fb_type + "#" + str(cnt) for fb_type, cnt in types_cnt])
            titles_str = " ".join([title + "#" + str(cnt) for title, cnt in titles_cnt])
            outf.write("%s\t%d\n" %(cols, cols_cnt[cols] ))
            for fb_type, cnt in types_cnt:
                outf.write("\t%s\t%d\n" %(fb_type, cnt))
            for title, cnt in titles_cnt:
                outf.write('\t%s\t%d\n' %(title, cnt))

        else:
            total += cols_cnt[cols]
    print total
    outf.close()

if __name__ == "__main__":
    table_cnt_path = os.path.join(table_dir, 'table_column_count.tsv')
    outpath = os.path.join(table_dir, 'frequent_table_cols.tsv')

    local_type_info_path = os.path.join(table_dir, 'local_info.json')
    local_info = load_local_info(local_type_info_path, table_cnt_path)
    collect_table_cnt(table_cnt_path, outpath, local_info)
