import os
from src.IOUtil import table_dir
from .table_rule_parser import TableParser
from .collect_table import collect_tables, load_local_info
from src.extractor.resource import Resource

if __name__ == "__main__":
    table_parser = TableParser(None, None)
    table_parser.init(paths = None)
    table_parser.load_extra_table(None)

    table_cnt_path = os.path.join(table_dir, 'table_column_count.tsv')
    local_type_info_path = os.path.join(table_dir, 'local_info.json')
    local_info = load_local_info(local_type_info_path, table_cnt_path)
    cols_cnt, cols_type_cnt, cols_title_cnt = collect_tables(table_cnt_path, local_info)

    ruled_tables = set()
    schema = Resource.get_singleton().get_schema()
    for table_rule in table_parser.table_rules:
        table_rule.check(schema)
        for t in table_rule.register_tables:
            ruled_tables.add(t)

    coverred_cnt = 0
    miss_cnt = 0
    total = 0
    for table in cols_cnt:
        cnt = cols_cnt[table]
        total += cnt
        if cnt < 20:
        #     if cnt > 20 and cnt < 30:
        #         print table, cnt
            continue
        if table in ruled_tables:
            coverred_cnt += cnt
        else:
            miss_cnt += cnt
            # print table, cnt

    print coverred_cnt, miss_cnt, total


    

