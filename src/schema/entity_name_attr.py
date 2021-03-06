import sys
import os
from .schema import load_entity, is_zh_en_literal, add_attr
from ..IOUtil import freebase_rel_dir, result_dir
from ..fb_process.extract_util import encode
import json


def load(filepath, outpath):
    print "load [%s]" %os.path.basename(filepath)
    e_set = load_entity()
    attrs = {}
    for cnt, line in enumerate(file(filepath, 'r')):
        if cnt % 1000000 == 0:
            print "cnt = %d, size = %d" %(cnt, len(attrs))
        p = line.strip().split('\t')[:3]
        p = [encode(x) for x in p]
        e = p[0]
        if e in e_set:
            literal = p[2]
            if is_zh_en_literal(literal):
                add_attr(attrs, e, p[1], p[2])

    outf = file(outpath, 'w')
    for x in sorted(attrs.keys()):
        outf.write('%s\t%s\n' %(x, json.dumps(attrs[x], ensure_ascii = False)))
    outf.close()
        
                
        
        


if __name__ == "__main__":
    # inpath = os.path.join(freebase_rel_dir, 'type.object.name.ttl')
    # outpath = os.path.join(result_dir, 'freebase/entity_name.json')

    inpath = os.path.join(freebase_rel_dir, 'common.topic.description.ttl')
    outpath = os.path.join(result_dir, 'freebase/entity_description.json')

    inpath = os.path.join(freebase_rel_dir, 'common.topic.alias.ttl')
    outpath = os.path.join(result_dir, 'freebase/entity_alias.json')

    load(os.path.join(result_dir, inpath), outpath)



