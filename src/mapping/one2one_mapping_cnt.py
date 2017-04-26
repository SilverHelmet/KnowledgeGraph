import sys
import json
from ..IOUtil import base_dir, load_file, Print
import os

def load_attrs():
    path = os.path.join(base_dir, 'docs/name_attr.txt')
    attrs = load_file(path)
    return attrs

if __name__ == "__main__":
    attrs = load_attrs()
    print attrs
    one_cnt = 0
    for cnt, line in enumerate(sys.stdin, start = 1):
        if cnt % 100000 == 0:
            Print("cnt = %d one_cnt = %d" %(cnt, one_cnt))
        key, obj = line.split('\t')
        obj = json.loads(obj)
        fb_uris = []
        for name_attr in attrs:
            if name_attr in obj:
                fb_uris.extend(obj[name_attr])
        fb_uris = set(fb_uris)
        if len(fb_uris) == 1:
            one_cnt += 1
    print "one cnt = %d" %one_cnt

        
    