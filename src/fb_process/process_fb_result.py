import os
import sys


fb_prefix = "http://rdf.freebase.com/ns/"

def process_fb_value(fb_str):
    if fb_str.startswith('"') and fb_str.endswith('"'):
        fb_str = fb_str[1:-1]
    elif fb_str[0] == '"' and fb_str[-4:] in['"@en', '"@zh']:
        fb_str = fb_str[1:-4]
    return fb_str

def get_domain(uri):
    global fb_prefix
    uri = uri[1:-1]
    if uri.startswith(fb_prefix):
        uri = uri[len(fb_prefix):]
    else:
        return None
    p = uri.split('.')
    return '.'.join(p[:1])

def get_type(uri):
    global fb_prefix
    uri = uri[1:-1]
    if uri.startswith(fb_prefix):
        uri = uri[len(fb_prefix):]
    else:
        return None
    p = uri.split('.')
    if len(p) < 2:
        return None
    return '.'.join(p[:2])

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
        if fb_domain and not fb_domain in ['m', 'base', 'user', 'freebase']:
            add_to_dict(domain_cnt, fb_domain)
            add_to_dict(type_cnt, fb_type)

        fb_domain = get_domain(ttl[2])
        fb_type = get_type(ttl[2])
        if fb_domain and not fb_domain in ['m', 'base', 'user', 'freebase']:
            add_to_dict(domain_cnt, fb_domain)
            add_to_dict(type_cnt, fb_type)


    print_cnt(domain_cnt, sys.argv[2])
    print_cnt(type_cnt, sys.argv[3])
        
        
