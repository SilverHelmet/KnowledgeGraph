from __future__ import absolute_import
import sys
import os
from .extract_util import get_domain, get_type


def extract(line, domains):
    p = line.split("\t")
    if len(p) == 3:
        if p[2][-1] == '.':
            p[2] = p[2][:-1]
    for part in p:
        domain = get_domain(part)
        if domain:
            domains.add(domain)
        
def black_domains():
    return set(["fb:" + x for x in ['m','en','user','base', 'freebase']])



if __name__ == "__main__":
    domains = set()
    inf = file("result/old_freebase/old_schema.ttl", 'r')
    outf = file('result/old_freebase/schema_domain.txt', 'w')
    for line in inf:
        extract(line, domains)
    blacks = black_domains()
    for domain in sorted(domains):
        if domain not in blacks:
            outf.write(domain + "\n")
    outf.close()