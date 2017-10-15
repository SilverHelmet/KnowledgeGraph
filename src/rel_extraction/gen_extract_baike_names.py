from .util import load_bk_types
from ..IOUtil import rel_ext_dir
import os
from tqdm import tqdm

def gen_extra_person_name(out_path):
    bk_type_map = load_bk_types()
    baike_names_path = os.path.join(rel_ext_dir, 'baike_names.tsv')
    Print('gen exta person name')
    outf = file(out_path, 'w')
    for line in tqdm(file(baike_names_path), total = 21710208):
        p = line.strip().split('\t')
        bk_url = p[0]
        types = bk_type_map[bk_url]
        if "fb:people.person" in types:
            
    outf.close()


if __name__ == "__main__":
    out_path = os.path.join(rel_ext_dir, 'extra_baike_names.tsv')
    gen_extra_person_name(out_path)