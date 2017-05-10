import sys
from ..IOUtil import Print, result_dir
import os
import json
reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == "__main__":
    in_file = os.path.join(result_dir, 'freebase/entity_property.ttl')
    out_file = os.path.join(result_dir, 'freebase/entity_property.json')

    # in_file = os.path.join(result_dir, 'test/entity_property.ttl')
    out_file = os.path.join(result_dir, 'test/entity_property.json')
    property_map = {}



    for cnt, line in enumerate(file(in_file), start = 1):
        if cnt % 10000 == 0:
            Print("load cnt = %d" %cnt)
        p = line.split('\t')
        s = p[0]
        if not s in property_map:
            property_map[s] = []
        property_map[s].append((p[1], p[2]))

    outf = file(out_file, 'w')
    for key in sorted(property_map.keys()):
        outf.write("%s\t%s\n" %(key, json.dumps(property_map[key])))
    outf.close()
