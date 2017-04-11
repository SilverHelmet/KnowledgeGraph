#encode:utf-8
from ..extract.extract_util import get_domain
from ..IOUtil import doc_dir, result_dir
import os

def load_entity():
    total = 56490649
    entities = set()
    cnt = 0
    chunk = total / 100
    next_percent_cnt = 0
    percent = 0
    for line in file(os.path.join(result_dir, 'freebase/entity_type.json'), 'r'):
        cnt += 1
        if cnt >= next_percent:
            print "load entity %d%%" %percent
            percent += 1
            next_percent_cnt += chunk
        uri = line.split('\t')[0]
        entities.add(uri)
    return entities


def load_types():
    types = set()
    for line in file(os.path.join(doc_dir, 'final_type_attrs.json'), 'r'):
        types.add(line.strip().split("\t")[0])
    return types

def is_zh_en_literal(uri):
    p = uri.strip().split("@")
    print p
    print len(p) == 2
    print p[0].startswith('"')
    print p[0].endswith('"')
    if len(p) == 2 and p[0].startswith('"') and p[0].endswith('"'):
        return p[1] in ['zh', 'en']
    return False

def add_attr(dict, id, name, value):
    if not id in dict:
        dict[id] = {}
    attr = dict[id]
    if not name in attr:
        attr[name] = []
    attr[name].append(value)
        
        

if __name__ == "__main__":
    pass