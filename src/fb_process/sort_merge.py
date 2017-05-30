
import sys
from ..IOUtil import Print, result_dir, load_ttl2map
import os
import json
from tqdm import tqdm
reload(sys)
sys.setdefaultencoding('utf-8')


        



if __name__ == "__main__":
    in_file = os.path.join(result_dir, 'freebase/entity_property.ttl')
    out_file = os.path.join(result_dir, 'freebase/entity_property.json')
    
    # in_file = os.path.join(result_dir, 'test/entity_property.ttl')
    # out_file = os.path.join(result_dir, 'test/entity_property.json')

    property_map = {}

    mediator_ttl_map = load_ttl2map(os.path.join(result_dir, 'freebase/mediator_property.ttl'), total = 50413655)

    for line in tqdm(file(in_file), total  = 283388281):
        p = line.strip().split('\t')
        s = p[0]
        if not s in property_map:
            property_map[s] = []
        property_map[s].append((p[1], p[2]))

    outf = file(out_file, 'w')
    Print("start sorting")
    for key in tqdm(sorted(property_map.keys()), total = len(property_map)):
        ttls = property_map[key]
        mediator_ttls = []
        p_map = {'property': ttls}
        for _, value in ttls:
            if value in mediator_ttl_map:
                mediator_ttls.extend(mediator_ttl_map[value])
        if len(mediator_ttls) > 0:
            p_map['mediator_property'] = mediator_ttls
        outf.write("%s\t%s\n" %(key, json.dumps(p_map)))
    outf.close()
    Print("Write Over")
