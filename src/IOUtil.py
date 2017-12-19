import sys
import os
import json
import datetime
from tqdm import tqdm
import commands
reload(sys)
sys.setdefaultencoding('utf-8')

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
        
def write_json_map(out_path, json_map, sort = False):
    keys = json_map.keys()
    if sort:
        keys = sorted(keys)
    outf = file(out_path, 'w')
    for key in keys:
        outf.write("%s\t%s\n" %(key, json.dumps(json_map[key], ensure_ascii = True)))
    outf.close()

def load_json_map(in_path, total = None):
    json_map = {}
    Print("load json map from %s" %in_path)
    for line in tqdm(file(in_path), total = total):
        p = line.split('\t')
        key = p[0]
        json_map[key.decode('utf-8')] = json.loads(p[1])
    return json_map


def load_file(in_path):
    ret = []
    for line in file(in_path):
        l = line.strip()
        if len(l) > 0:
            ret.append(line.strip())
    return ret
     
def load_json_dict(path):
    res = {}
    cnt = 0
    for line in file(path):
        cnt += 1
        if cnt % 1000000 == 0:
            Print("\rload cnt = %d," %cnt)
        p = line.split('\t')
        key = p[0]
        value = json.loads(p[1])
        res[key] = value
    Print("load finished")
    return res

def load_html_file(path):
    f = file(path, 'r')
    html = f.read()
    f.close()
    return html

def merge_dict(x, other):
    cnt = 0
    for key in other:
        cnt += 1
        if cnt % 1000000 == 0:
            Print("merged cnt = %d" %cnt) 
        if not key in x:
            x[key] = other[key]
        else:
            oattr = other[key]
            mattr = x[key]
            for name in oattr:
                assert name not in mattr
                mattr[name] = oattr[name]

def write_dict_cnt(dict_cnt, outpath):
    outf = file(outpath, 'w')
    cnt = 0
    for key in sorted(dict_cnt.keys(), key = lambda x: dict_cnt[x], reverse = True):
        cnt += 1
        if cnt % 100000 == 0:
            Print("write cnt = %d" %cnt)
        outf.write(str(key) + '\t' + str(dict_cnt[key]) + '\n')
    outf.close()

def load_ttl2map(filepath, total = None, entities = None):
    Print('load ttl from %s' %filepath)
    if total is None:
        total = nb_lines_of(filepath)
    if total:
        generator = tqdm(file(filepath), total = total)
    else:
        generator = file(filepath)
    prop_map = {}
    for line in generator:
        s, p, o = line.strip().split('\t')
        if entities is not None and s in entities:
            continue
        if not s in prop_map:
            prop_map[s] = []
        prop_map[s].append((p, o))
    return prop_map

def nb_lines_of(filepath):
    output = commands.getoutput('wc -l %s' %filepath)
    p = int(output.strip().split(" ")[0])
    return p



        
        
base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
result_dir = os.path.join(base_dir, 'result')
cache_dir = os.path.join(result_dir, 'cache')
classify_dir = os.path.join(result_dir, '360/mapping/classify')
rel_ext_dir = os.path.join(result_dir, 'rel_extraction')
dict_dir = os.path.join(rel_ext_dir, 'dict')
dataset_dir = os.path.join(rel_ext_dir, 'dataset')
extra_name_dir = os.path.join(rel_ext_dir, 'extra_name')
extra_type_dir = os.path.join(rel_ext_dir, 'extra_type')
table_dir = os.path.join(rel_ext_dir, 'tables')
infobox_cnt_dir = os.path.join(rel_ext_dir, 'infobox_count')
freebase_rel_dir = os.path.join(result_dir, 'freebase_rel')
doc_dir = os.path.join(base_dir, "docs")
data_dir = os.path.join(base_dir, 'data')

