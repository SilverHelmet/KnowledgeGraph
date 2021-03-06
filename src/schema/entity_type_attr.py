from ..IOUtil import result_dir
from ..fb_process.extract_util import encode
import json, os



def load(filepath):
    attrs = {}
    print filepath
    for cnt, line in enumerate(file(filepath, 'r')):
        if (cnt+1) % 1000000 == 0:
            print "cnt = %dW" %((cnt+1) / 10000)
        p = line.strip().split('\t')[:3]
        p = [encode(x) for x in p]
        if not p[0] in attrs:
            attrs[p[0]] = {}
        attr = attrs[p[0]]
        if not p[1] in attr:
            attr[p[1]] = []
        attr[p[1]].append(p[2])
    return attrs

        
            

if __name__ == "__main__":
    attrs = load(os.path.join(result_dir, 'freebase/entity_type.ttl'))
    outf = file(os.path.join(result_dir, 'freebase/entity_type.json'), 'w')
    for uri in sorted(attrs.keys()):
        outf.write(uri +'\t' + json.dumps(attrs[uri]) + "\n")
    outf.close()
