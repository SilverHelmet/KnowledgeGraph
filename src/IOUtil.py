import sys
import os
import json

def write_strs(out_path, l, sorted_flag = False):
    if sorted_flag:
        l = sorted(l)
    outf = file(out_path, 'w')
    for x in l:
        outf.write(x + '\n')
    outf.close()
        

def load_file(in_path):
    ret = []
    for line in file(in_path):
        ret.append(line.strip())
    return ret
        
        


base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
result_dir = os.path.join(base_dir, 'result')
freebase_rel_dir = os.path.join(result_dir, 'freebase_rel')
doc_dir = os.path.join(base_dir, "docs")
