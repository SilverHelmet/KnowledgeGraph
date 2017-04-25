from ..IOUtil import load_json_dict, Print as P, merge_dict
import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')

def add_to_dict(d, key, oattr):
    if not key in d:
        d[key] = {}
    mattr = d[key]
    for name in oattr:
        # assert name not in mattr
        mattr[name] = sorted(set(oattr[name]))

def load_and_merge(res, inpath):
    cnt = 0
    P("")
    for line in file(inpath):
        p = line.split('\t')
        cnt += 1
        if cnt % 1000000 == 0:
            P("\b\rload cnt = %d" %cnt)
        key = p[0]
        value = json.loads(p[1])
        add_to_dict(res, key, value)

if __name__ == "__main__":
    outpath = sys.argv[1]
    inpaths = sys.argv[2:]
    P("outpath is %s" %outpath)
    P("inpaths is %s" %"   ".join(inpaths))
    
    res = {}
    for inpath in inpaths:
        P("load path %s" %inpath)
        load_and_merge(res, inpath)
        
        # other_res = load_json_dict(inpath)
        # P("merge dict %s" %inpath)
        # merge_dict(res, other_res)
        P("res size = %d" %len(res))
        
    P("write dict ot [%s]" %outpath)
    outf = file(outpath, 'w')
    for key in sorted(res.keys()):
        outf.write(key + '\t' + json.dumps(res[key], ensure_ascii = False) + '\n')
    outf.close()

        
        

    
    