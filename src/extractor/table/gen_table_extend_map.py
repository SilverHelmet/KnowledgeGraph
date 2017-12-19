import glob
import os

from src.IOUtil import table_dir
from .table_rule_parser import TableParser
from .collect_table import load_local_info, collect_tables, topk_keys

def nb_overlap(t1, t2):
    t1 = set(t1.split(" # "))
    t2 = t2.split(' # ')
    cnt = 0
    for x in t2:
        if x in t1:
            cnt += 1
    return cnt

def table_size(table):
    return len(table.split(' # '))

def gen_table_extend_map():
    table_parser = TableParser(None)
    table_parser.init(paths = None)

    tables = set()
    table_info = {}
    for table_rule in table_parser.table_rules:
        print table_rule.name, table_rule.preferred_types.get('entity', 'None'), len(table_rule.register_tables)
        for table in table_rule.register_tables:
            tables.add(table)
            if table in table_info:
                table_info[table].append((table_rule.name, table_rule.preferred_types['entity']))
            else:
                table_info[table] = [(table_rule.name, table_rule.preferred_types['entity'])]

    
    table_cnt_path = os.path.join(table_dir, 'table_column_count.tsv')
    local_type_info_path = os.path.join(table_dir, 'local_info.json')
    local_info = load_local_info(local_type_info_path, table_cnt_path)
    cols_cnt, cols_type_cnt, cols_title_cnt = collect_tables(table_cnt_path, local_info)
    
    miss_freq_cnt =  0
    cover_cnt = 0
    hit_freq_cnt =0
    partial_cover_cnt = 0
    miss_sparse_cnt = 0
    for table in cols_cnt:
        cnt = cols_cnt[table]
        if cnt < 20:
            if cnt > 10:
                miss_sparse_cnt += cnt
            continue

        if table in tables:
            hit_freq_cnt += cnt
        else:

            max_over_lap = 0
            for freq_table in tables:
                max_over_lap = max(max_over_lap, nb_overlap(freq_table, table))
            


            if max_over_lap == len(table.split(' # ')):
                cover_tables = []
                for freq_table in tables:
                    if nb_overlap(freq_table, table) == max_over_lap:
                        cover_tables.append(freq_table)
                    
                cover_cnt += cnt
                print table, cnt
                types_cnt = topk_keys(cols_type_cnt[table], 5)
                types_str = " ".join([fb_type + "#" + str(cnt) for fb_type, cnt in types_cnt])
                print '\t%s' %types_str
                for freq_table in cover_tables:
                    info_str = ""
                    for info in table_info[freq_table]:
                        info_str += "\t%s" %(info[0])
                        info_str += "\t%s" %(" ".join(info[1]))
                    print '\t%s%s' %(freq_table, info_str)
            else:
                miss_freq_cnt += cnt

    print len(tables)
    print "hit freq cnt = %d" %hit_freq_cnt
    print 'covered freq cnt = %d' %cover_cnt
    print 'miss freq cnt = %d' %miss_freq_cnt
    print 'miss 10 < freq < 40  cnt = %d' %miss_sparse_cnt
    # print 'partial coverred cnt = %d' %partial_cover_cnt

if __name__ == "__main__":
    
    gen_table_extend_map()

