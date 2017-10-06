from ..IOUtil import data_dir
import glob
import os
from .parse import strip_url

if __name__ == "__main__":
    type_path = os.path.join(data_dir, '360_final_type_url')
    out_path = os.path.join(data_dir, '360_final_type_url.json')
    outf = file(out_path, 'w')
    baike_cls_map = {}
    for filepath in glob.glob(type_path + "/type*"):
        baike_cls = os.path.basename(filepath)
        print baike_cls
        for line in file(filepath):
            baike_url, name = line.split('\t')
            baike_url = strip_url(baike_url)
            if not baike_url in baike_cls_map:
                baike_cls_map[baike_url] = []
            baike_cls_map[baike_url].append(baike_cls)

    
    for key in sorted(baike_cls_map.keys()):
        type_str = ' '.join(list(set(baike_cls_map[key])))
        outf.write("%s\t%s\n" %(key, type_str))
    outf.close()
                

