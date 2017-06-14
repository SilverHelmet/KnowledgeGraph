from ..IOUtil import load_ttl2map, result_dir
from ..mapping.predicate_mapping import extend_fb_ttls
import os
import json

if __name__ == "__main__":
    mediator_ttl_map = load_ttl2map(os.path.join(result_dir, 'freebase/mediator_property.ttl'), total = 50413655)
    fb_property_path = os.path.join(result_dir, 'freebase/entity_property.json')

    pcnt = 0
    for cnt, line in enumerate(file(fb_property_path), start = 1):
        p = line.split('\t')
        fb_uri = p[0]
        fb_ttls = json.loads(p[1])
        new_fb_ttls = extend_fb_ttls(fb_ttls, fb_uri, mediator_ttl_map)
        
        if len(new_fb_ttls)  > len(fb_ttls):
            print "------------------"
            print fb_uri
            print fb_ttls
            print new_fb_ttls
            pcnt += 1
            if pcnt > 10:
                break


