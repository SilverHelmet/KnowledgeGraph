from .util import load_baike_entity_class, load_mappings
from ...IOUtil import result_dir, Print, data_dir
import os

if __name__ == "__main__":
    baike2fb = load_mappings()
    baike_urls =set(baike2fb.keys())
    baike_class_path =  os.path.join(data_dir, '360_final_type_url.json')
    baike2cls = load_baike_entity_class(filepath = baike_class_path, baike_urls = baike_urls, simple = True)
    Print('load class %d/%d' %(len(baike2cls), len(baike_urls)))
    values = set()
    for cls_list in baike2cls.values():
        for value in cls_list:
            values.add(value)
    for value in sorted(values):
        print value
    Print("#value = %d" %len(values))

    out_path = os.path.join(result_dir, '360/mapping/classify/baike_cls.tsv')
    outf = file(out_path, 'w')    
    for baike_url in sorted(baike2cls.keys()):
        outf.write('%s\t%s\n' %(baike_url, " ".join(baike2cls[baike_url])))
    outf.close()

        
