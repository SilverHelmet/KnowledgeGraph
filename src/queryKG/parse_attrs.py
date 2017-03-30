import sys
import json
from ..extract.extract_util import get_domain
from ..IOUtil import write_strs

def parse_types_of_domains():
    types = set()
    for line in file('result/old_freebase/queried_domain_attrs.json'):
        p = line.split("\t")
        domain = p[0]
        attrs = json.loads(p[1])
        types = types.union(attrs['fb:type.domain.types'])
    outf = file('result/old_freebase/queried_type.txt', 'w')
    for type in sorted(types):
        domain = get_domain(type)
        if domain == "fb:type":
            continue
        outf.write(type + "\n")
    outf.close()

def parse_properties_of_types():
    properties = set()
    for line in file('result/old_freebase/queried_type_attrs.json'):
        p = line.split('\t')
        type = p[0]
        attrs = json.loads(p[1])
        properties = properties.union(attrs['fb:type.type.properties'])
    write_strs('result/old_freebase/queried_property.txt', properties, sorted_flag = True)

if __name__ == "__main__":
    parse_types_of_domains()
    parse_properties_of_types()
