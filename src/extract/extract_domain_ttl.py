import sys
import glob
from process_fb_result import get_domain

def load_domain():
    domains = set()
    for line in file('result/freebase_domain/schema.domain.txt'):
        line = line.strip()
        if line:
            domains.add(line)
    return domains

domains = load_domain()
print domains
pref = 'result/freebase/'
partterns = ["type.property.unique", 'type.property.unit', 'type.property.reverse_property', 'type.object.type', 
'type.object.name', 'freebase.type_profile.instance_count', 'freebase.type_hints.mediator', 'freebase.type_hints.included_types', 
'common.topic.description','type.property.schema', 'type.property.expected_type']
partterns = [pref + p + "/*ttl" for p in partterns]

outf = file('result/freebase_domain/schema.ttl', 'w')
for p in partterns:
    print "parttern is %s" %p
    for filepath in glob.glob(p):
        for line in file(filepath):
            p = line.strip().split('\t')
            domain = get_domain(p[0])
            if domain is not None and domain in domains:
                outf.write(line)

outf.close()

        
