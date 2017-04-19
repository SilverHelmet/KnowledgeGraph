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
     
def load_json_dict(path):
    res = []
    for line in file(path):
        p = line.split('\t')
        key = p[0]
        value = json.loads(p[1])
        res[key] = value
    return value

def merge_dict(x, other):
    for key in other:
        if not key in x:
            x[key] = other[key]
        else:
            oattr = other[key]
            mattr = x[key]
            for name in oattr:
                assert name not in mattr
                mattr[name] = oattr[name]

def now():
    time = datetime.datetime.now()
    return time.strftime('%m-%d %H:%M:%S')
    
def Print(*l):
    l = map(str, l)
    print now() + "\t" + " ".join(l)
    
    
        


base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
result_dir = os.path.join(base_dir, 'result')
freebase_rel_dir = os.path.join(result_dir, 'freebase_rel')
doc_dir = os.path.join(base_dir, "docs")
