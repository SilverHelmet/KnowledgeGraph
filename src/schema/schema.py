from ..extract.extract_util import get_domain
from ..IOUtil import doc_dir
import os

def load_types():
    types = set()
    for line in file(os.path.join(doc_dir, 'final_type_attrs.json'), 'r'):
        type = line.strip().split("\t")[0]
        if not get_domain(type) in ['fb:measurement_unit', 'fb:type']:
            types.add(type)
    return types

if __name__ == "__main__":
    print len(load_types())