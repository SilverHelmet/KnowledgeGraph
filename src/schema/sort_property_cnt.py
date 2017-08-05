from .schema import load_property_attrs
from ..fb_process.extract_util import get_type
from ..IOUtil import doc_dir
import os
import json

if __name__ == "__main__":
    prop_attrs = load_property_attrs()
    type_prop_attrs = {}
    type_prop_cnts = {}
    for prop in prop_attrs:
        cnt = prop_attrs[prop]['count']
        fb_type = get_type(prop)
        
        if not fb_type in type_prop_cnts:
            type_prop_attrs[fb_type] = {}
            type_prop_cnts[fb_type] = 0
        type_prop_cnts[fb_type] += cnt
        type_prop_attrs[fb_type][prop] = prop_attrs[prop]
    
    outf = file(os.path.join(doc_dir, "sorted_final_property_attrs.json"), 'w')
    for fb_type in sorted(type_prop_cnts.keys(), key = lambda x: type_prop_cnts[x], reverse = True):
        fb_prop_attrs = type_prop_attrs[fb_type]
        for prop in sorted(fb_prop_attrs.keys()):
            attrs = fb_prop_attrs[prop]
            out_str = "%s\t%s\n" %(prop, json.dumps(attrs, ensure_ascii = False))
            outf.write(out_str.encode('utf-8'))
    outf.close()




