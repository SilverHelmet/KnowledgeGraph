from ..IOUtil import doc_dir, load_file, rel_ext_dir
from .util import load_bk_types
from .gen_dict import get_domain
import os
import json
from tqdm import tqdm

if __name__ == "__main__":
    domains = set()
    for line in file(os.path.join(doc_dir, 'important_domains.txt')):
        line = line.strip()
        if line.startswith("#"):
            continue
        domains.add(line)

    
    outf = file(os.path.join(rel_ext_dir, 'vertical_domain_baike_names.tsv'), 'w')
    dict_outf = file(os.path.join(rel_ext_dir, 'vertical_domain_baike_dict.txt'), 'w')
    fb_type_map = load_bk_types()
    names = set()
    for line in tqdm(file(os.path.join(rel_ext_dir, 'baike_names.tsv')), total  = 21710208):
        p = line.rstrip('\n').decode('utf-8').split('\t')
        baike_url = p[0]
        types = fb_type_map[baike_url]
        write_flag = False
        for fb_type in types:
            if get_domain(fb_type) in domains:
                write_flag = True
        if write_flag:
            outf.write('%s\t%s\t%s\n' %(baike_url, json.dumps(types), "\t".join(p[1:])))
            for name in p[1:]:
                names.add(name)
    outf.close()

    for name in sorted(names):
        dict_outf.write("%s\n" %(name))
    dict_outf.close()






