import os

from src.IOUtil import table_dir, Print


def collect_table_cnt(cnt_path):
    Print("collect table cols cnt from [%s]" %os.path.basename(cnt_path))
    for line in file(cnt_path):
        

if __name__ == "__main__":
    table_cnt_path = os.path.join(table_dir, 'table_column_count.tsv')
    collect_table_cnt(table_cnt_path)
