import os
import sys


fb_prefix = "http://rdf.freebase.com/ns/"

def get_domain(uri):
    global fb_prefix
    uri = uri[1:-1]
    if uri.startswith(fb_prefix):
        uri = uri[len(fb_prefix):]
    else:
        return None
    p = uri.split('.')
    if len(p) <= 2:
        return None
    return '.'.join(p[:-2])

def get_type(uri):
    global fb_prefix
    uri = uri[1:-1]
    if uri.startswith(fb_prefix):
        uri = uri[len(fb_prefix):]
    else:
        return None
    p = uri.split('.')
    if len(p) <= 2:
        return None
    return '.'.join(p[:-1])

def add_to_dict(cnt, key):
    if key is None:
        return
    if not key in cnt:
        cnt[key] = 1
    else:
        cnt[key] += 1

def print_cnt(cnt, out_filepath):
    outf = file(out_filepath, 'w')
    for key in sorted(cnt.keys(), reverse = True):
        outf.write("%s\n" %(key))
    outf.close()

if __name__ == "__main__":
    domain_cnt = {}
    type_cnt = {}

    for line in file(sys.argv[1]):
        line = line.strip()
        ttl = line.split('\t')
        fb_domain = get_domain(ttl[0])
        fb_type = get_type(ttl[0])
        if fb_domain and not fb_domain.startswith("base") and not fb_domain.startswith('user') and not fb_domain.startswith('freebase'):
            add_to_dict(domain_cnt, fb_domain)
            add_to_dict(type_cnt, fb_type)

        fb_domain = get_domain(ttl[2])
        fb_type = get_type(ttl[2])
        if fb_domain and not fb_domain.startswith("base") and not fb_domain.startswith('user') and not fb_domain.startswith('freebase'):
            add_to_dict(domain_cnt, fb_domain)
            add_to_dict(type_cnt, fb_type)


    print_cnt(domain_cnt, sys.argv[2])
    print_cnt(type_cnt, sys.argv[3])
        
        
