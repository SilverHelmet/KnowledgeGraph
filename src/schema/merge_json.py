from ..IOUtil import load_json_dict, Print as P, merge_dict
import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == "__main__":
    outpath = sys.argv[1]
    inpaths = sys.argv[2:]
    P("outpath is %s" %outpath)
    P("inpaths is %s" %"   ".join(inpaths))
    
    res = {}
    for inpath in inpaths:
        P("load path %s" %inpath)
        other_res = load_json_dict(inpath)
        P("merge dict %s" %inpath)
        merge_dict(res, other_res)
        P("res size = %d" %len(res))
        
    
    outf = file(outpath, 'w')
    for key in sorted(res.keys()):
        outf.write(key + '\t' + json.dumps(res[key], ensure_ascii = False) + '\n')
    outf.close()

        
        

    
    