#encode:utf-8
from ..extract.extract_util import get_domain
from ..IOUtil import doc_dir
import os

def load_entity():
    entities = set()
    for line in file(os.path.join(result_dir, 'freebase/entity_type.json'), 'r'):
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
        

if __name__ == "__main__":
    pass