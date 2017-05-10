import sys
from .extract_util import get_domain, encode, get_type
from ..schema import schema
from ..IOUtil import Print

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


def filter_entity(ttl):
    global types
    p = ttl.split("\t")
    uri = encode(p[2])
    if get_domain(uri) in ['fb:measurement_unit', 'fb:type', 'fb:common']:
        return False
    return uri in types



def filter_property_ttl(ttl):
    global predicates, entities
    p = ttl.split('\t')
    s = encode(p[0])
    m = encode(p[1])
    return s in entities and m in predicates

    

def filter_ttl(in_filepath, out_filepath, valid_func):
    outf = file(out_filepath, 'w')
    cnt = 0
    out_cnt = 0
    for line in file(in_filepath):
        line = line.strip()
        cnt += 1
        if cnt % 1000000 == 0:
            Print("cnt = %d out_cnt = %d" %(cnt, out_cnt))
        if valid_func(line):
            out_cnt += 1
            p = line.split('\t')[:3]
            pp = [encode(x) for x in p]
            for x in pp:
                if x is None:
                    print line
            outf.write("\t".join(pp) + "\n")
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
        types = schema.load_types()
        func = filter_entity
    elif mode == "property_ttl":
        predicates = schema.load_predicates()
        entities = schema.load_entity()
        func = filter_property_ttl
    filter_ttl(in_filepath, out_filepath, func)