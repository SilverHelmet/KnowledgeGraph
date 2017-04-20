import sys
import os
import json
import datetime

def now():
    time = datetime.datetime.now()
    return time.strftime('%m-%d %H:%M:%S')
    
def Print(*l):
    l = map(str, l)
    print now() + "\t" + " ".join(l)

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
     
def load_json_dict(path):
    res = {}
    cnt = 0
    for line in file(path):
        cnt += 1
        if cnt % 100000 == 0:
            Print("load cnt = %d" %cnt)
        p = line.split('\t')
        key = p[0]
        value = json.loads(p[1])
        res[key] = value
    return value

def merge_dict(x, other):
    cnt = 0
    for key in other:
        cnt += 1
        if cnt % 100000 == 0:
            Print("merged cnt = %d" %cnt) 
        if not key in x:
            x[key] = other[key]
        else:
            oattr = other[key]
            mattr = x[key]
            for name in oattr:
                assert name not in mattr
                mattr[name] = oattr[name]
    
    
        


base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
result_dir = os.path.join(base_dir, 'result')
freebase_rel_dir = os.path.join(result_dir, 'freebase_rel')
doc_dir = os.path.join(base_dir, "docs")
