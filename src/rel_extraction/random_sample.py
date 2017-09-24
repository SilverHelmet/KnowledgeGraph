import numpy as np
from .util import load_mappings
from ..IOUtil import rel_ext_dir, nb_lines_of
import os

if __name__ == "__main__":
    bk2fb = load_mappings()
    bk_urls = bk2fb.keys()

    permutation = np.random.permutation(len(bk_urls))[:10000]
    random_pool = set()
    for idx in permutation:
        random_pool.add(bk_urls[idx])
    random_pool.add('baike.so.com/doc/4785734-5001726.html')
    random_pool.add('baike.so.com/doc/5382393-5618748.html')
    random_pool.add('baike.so.com/doc/1287918-1361771.html')

    outf = file(os.path.join(rel_ext_dir, 'random_baike_urls.txt'), 'w')
    for bk_url in sorted(random_pool):
        outf.write(bk_url + '\n')
    outf.close()

    Print('extract docs')
    doc_path = os.path.join(rel_ext_dir, 'baike_doc.json')
    outf = file(os.path.join(rel_ext_dir, 'sample_baike_doc.json'), 'w')
    for line in tqdm(file(doc_path), total = nb_lines_of(doc_path)):
        p = line.split('\t')
        bk_url = p[0].decode('utf-8')
        if bk_url in random_pool:
            outf.write(line)
    outf.close()



