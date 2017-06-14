import os
from ..schema.schema import load_property_attrs
from ..IOUtil import result_dir, Print


if __name__ == "__main__":
    in_path = os.path.join(result_dir, 'freebase/entity_property.ttl')
    data_types = set()
    prop_attrs_map = load_property_attrs()

    for line in file(in_path):
        line = line.strip()
        p = line.split('\t')
        value = p[2]
        if "^^" in value:
            t = value.split("^^")
            if len(t) > 2:
                print "error", line
                continue
            _, data_type  = value.split('^^')
            if not data_type in data_types:
                data_types.add(data_type)
                print "add data_type", data_type, prop_attrs_map[p[1]]['fb:type.property.expected_type']
                print line
    
            

