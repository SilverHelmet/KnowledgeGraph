from .extract_util import encode
import sys

def is_property(uri):
    uri = encode(uri)
    return uri == 'fb:type.property'

def is_type(uri):
    uri = encode(uri):
    return uri == "fb:type.type"
    
    
if __name__ == "__main__":
    l = []
    mode = sys.argv[1]
    if mode == 'type':
        func = is_type
    elif mode == "property":
        func = is_property

    for line in sys.stdin:
        p = line.strip().split("\t")
        if func(p[2]):
            l.append(encode(p[0]))
            print p[0]
    # for x in sorted(l):
        # print x