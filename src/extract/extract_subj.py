from .extract_util import encode
import sys

def is_property(uri):
    uri = encode(uri)
    return uri == 'fb:type.property'

def is_type(uri):
    uri = encode(uri)
    return uri == "fb:type.type"

def is_true(uri):
    return True
    
    
if __name__ == "__main__":
    l = set()
    mode = sys.argv[1]
    outf = file(sys.argv[2], 'w')
    
    func = None
    if mode == 'type':
        func = is_type
    elif mode == "property":
        func = is_property
    elif mode == "True":
        func = is_true

    for cnt, line in enumerate(sys.stdin):
        p = line.strip().split("\t")
        if func(p[2]):
            l.add(encode(p[0]))
        if cnt % 100000 == 0:
            print "cnt = %dW, #subj = %d" %(cnt/10000, len(l)) 
            # print p[0]
    for x in sorted(l):
        outf.write(x)
        outf.write('\n')
    outf.close()