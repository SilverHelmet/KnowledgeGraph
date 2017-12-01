import re
from src.IOUtil import base_dir
import os

log_path = os.path.join(base_dir, 'log/error_triple.log')
re_p = re.compile(r'property = (?P<property>[\w\.:^]+), size = (?P<size>\d+)')
props_cnt = {}
props_max_cnt = {}

for line in file(log_path):
    match = re_p.search(line)
    prop = match.group('property')
    size = int(match.group('size'))
    if prop not in props_cnt:
        props_cnt[prop] = 0
        props_max_cnt[prop] = 0
    props_cnt[prop] += 1
    props_max_cnt[prop] = max(size, props_max_cnt[prop])
    

for prop in sorted(props_cnt, key = lambda x: props_cnt[x], reverse = True):
    cnt = props_cnt[prop]
    size =props_max_cnt[prop]
    if cnt >= 5:
        print '\t("%s", %d),' %(prop, size)
    


