from ..IOUtil import doc_dir
import os

def load_types():
    types = set()
    for line in file(os.path.join(doc_dir, 'final_type_attrs.json'), 'r'):
        types.add(line.strip().split("\t")[0])
    return types

if __name__ == "__main__":
    print len(load_types())