from ..IOUtil import rel_ext_dir, Print
from tqdm import tqdm
import os
from .util import load_bk_types

if __name__ == "__main__":
    title_map = {
        'fb:location.country': "nationality",
        "fb:people.profession": "profession",
    }
    name2title = {}
    bk_types_map =load_bk_types()
    for line in tqdm(file(os.path.join(rel_ext_dir, 'baike_names.tsv')), total = 21710208):
        p = line.strip().split('\t')
        bk_url = p[0]
        types = bk_types_map[bk_url]
        names = p[1:]
        for title_type in title_map:
            if title_type in types:
                for name in names:
                    if name not in name2title:
                        name2title[name] = []
                    name2title[name].append(title_map[title_type])

    outf = file(os.path.join(rel_ext_dir, 'title_verb_dict.txt'), 'w')
    for key in sorted(name2title.keys()):
        titles = sorted(list(set(name2title[key])))
        outf.write("%s\t%s\n" %(key, "\t".join(titles)))
    outf.close()


