import sys
from .extract_util import get_domain, encode, get_type
from ..schema import schema

black_schema_domains = set(['fb:freebase', 'fb:base', 'fb:m', 'fb:g', 'fb:user'])
def useful_domain(ttl):
    p = ttl.split('\t')
    global black_schema_domains
    domain = get_domain(p[0])
    if domain is None:
        return False
    return not domain in black_schema_domains

def filter_type(ttl):
    uri = encode(ttl.split('\t')[2])
    return uri == 'fb:type.type'

def filter_property(ttl):
    uri = encode(ttl.split("\t")[2])
    return uri == 'fb:type.property'

types = schema.load_types()
def filter_entity(ttl):
    global types
    p = ttl.split("\t")
    uri = encode(p[2])
    if get_domain(uri) in ['fb:measurement_unit', 'fb:type', 'fb:common']:
        return False
    return uri in types
    

def filter_ttl(in_filepath, out_filepath, valid_func):
    outf = file(out_filepath, 'w')
    cnt = 0
    for line in file(in_filepath):
        line = line.strip()
        cnt += 1
        if cnt % 100000 == 0:
            print "cnt = %d" %cnt
        if valid_func(line):
            outf.write("\t".join(line.split('\t')[:3]) + "\n")
    outf.close()
    

if __name__ == "__main__":
    in_filepath = sys.argv[1]
    out_filepath = sys.argv[2]
    mode = sys.argv[3]
    print "load from [%s]" %in_filepath
    print 'write to [%s]' %out_filepath
    print "mode = %s" %mode
    if mode == "schema":
        func = useful_domain
    elif mode == "type":
        func = filter_type
    elif mode == 'property':
        func = filter_property
    elif mode == "entity":
        func = filter_entity
    filter_ttl(in_filepath, out_filepath, func)