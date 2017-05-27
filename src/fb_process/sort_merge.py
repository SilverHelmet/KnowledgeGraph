import sys
from ..IOUtil import Print, result_dir
import os
import json
from tqdm imprt tqdm
reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == "__main__":
    in_file = os.path.join(result_dir, 'freebase/entity_property.ttl')
    out_file = os.path.join(result_dir, 'freebase/entity_property.json')

    # in_file = os.path.join(result_dir, 'test/entity_property.ttl')
    # out_file = os.path.join(result_dir, 'test/entity_property.json')
    property_map = {}



    for cnt, line in tqdm(enumerate(file(in_file), start = 1), total  = 53574900):
        p = line.strip().split('\t')
        s = p[0]
        if not s in property_map:
            property_map[s] = []
        property_map[s].append((p[1], p[2]))

    outf = file(out_file, 'w')
    Print("start sorting")
    for cnt, key in enumerate(sorted(property_map.keys()), start = 0):
        if cnt % 100000 == 0:
            Print("write cnt = %d" %cnt)
        outf.write("%s\t%s\n" %(key, json.dumps(property_map[key])))
    outf.close()
