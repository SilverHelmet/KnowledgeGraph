import sys
from .extract_util import get_domain

black_schema_domains = set(['freebase', 'base', 'type', 'm', 'g'])
def useful_domain(ttl):
    p = ttl.split('\t')
    global black_schema_domains
    domain = get_domain(p[0])
    if domain is None:
        return False
    return not domain in black_schema_domains

    

def filter_ttl(in_filepath, out_filepath, valid_func):
    outf = file(out_filepath, 'w')
    cnt = 0
    for line in file(in_filepath):
        cnt += 1
        if cnt % 10000 == 0:
            print "cnt = %d" %cnt
        if valid_func(line):
            outf.write("\t".join(line.split('\t')[:3]))
    outf.close()
    

if __name__ == "__main__":
    in_filepath = sys.argv[1]
    out_filepath = sys.argv[2]
    filter_ttl(in_filepath, out_filepath, useful_domain)