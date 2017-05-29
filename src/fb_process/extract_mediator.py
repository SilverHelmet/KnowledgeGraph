from .extract_util import encode
from ..IOUtil import result_dir
import os
from tqdm import tqdm
from ..schema.schema import Schema

def parse_mediator_entities(property_path, total = 283388281):
    schema = Schema()
    schema.init()
    med_entities = []
    for line in tqdm(file(property_path), total = total):
        p = line.strip().split('\t')
        prop = p[1]
        value = p[2]
        value_type = schema.expected_type(prop)
        if schema.is_mediator(value_type):
            med_entities.append(value)

    print "size = %d, %d" %(len(med_entities), len(set(med_entities)) )
    return med_entities





if __name__ == "__main__":
    property_path = os.path.join(result_dir, 'freebase/entity_property.ttl')
    freebase_path = "/home/wzc/freebase/fb.ttl"

    mediator_entities = parse_mediator_entities(property_path)

    outf = file(os.path.join(result_dir, 'freebase/mediator_entities.txt'), 'w')
    for e in tqdm(mediator_entities, total = len(mediator_entities)):
        outf.write("%s\n" %e)
    outf.close()