import os
from .util import load_bk_entity_pop, load_name2baike
from ..IOUtil import rel_ext_dir, Print
from tqdm import tqdm

if __name__ == "__main__":
    pop_map = load_bk_entity_pop()
    name2bk = load_name2baike()
    keys = sorted(name2bk)
    out_path = os.path.join(rel_ext_dir, 'baike_dict.txt')
    outf = file(out_path, 'w')
    Print('write dict to %s' %out_path)
    for name in tqdm(keys, total = len(keys)):
        bks = name2bk[name]
        pop = 0
        for bk_url in bks:
            pop = max(pop, pop_map.get(bk_url, 0))
        ouf.write('%s %d baike' %(name, pop))
    outf.close()


    
