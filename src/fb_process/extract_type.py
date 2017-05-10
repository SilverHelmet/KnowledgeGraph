from .extract_util import get_type
from .extract_domain import black_domains

def extract(line, types):
    p = line.split("\t")
    if len(p) == 3:
        if p[2][-1] == '.':
            p[2] = p[2][:-1]
    for part in p:
        fb_type = get_type(part)
        if fb_type:
            types.add(fb_type)




if __name__ == "__main__":
    types = set()
    inf = file("result/old_freebase/old_schema.ttl", 'r')
    outf = file('result/old_freebase/schema_type.txt', 'w')
    blacks = black_domains()
    for line in inf:
        extract(line, types)
    
    for fb_types in sorted(types):
        fb_domain = fb_types.split(".")[0]
        if fb_domain not in blacks:
            outf.write(fb_types + "\n")
    outf.close()

    