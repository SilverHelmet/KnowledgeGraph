import numpy as np
from .util import load_mappings
from ..IOUtil import rel_ext_dir
import os

if __name__ == "__main__":
    bk2fb = load_mappings()
    bk_urls = bk2fb.keys()
    
    permutation = np.random.permutations(len(bk_urls))[:10000]
    random_pool = set()
    for idx in permutation:
        random_pool.add(bk_urls[idx])
    random_pool.add('baike.so.com/doc/4785734-5001726.html')
    random_pool.add('baike.so.com/doc/5382393-5618748.html')

    outf = file(os.path.join(rel_ext_dir, 'random_baike_urls.txt'), 'w')
    for bk_url in sorted(random_pool):
        outf.write(bk_url + '\n')
    outf.close()



