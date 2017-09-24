from ..IOUtil import rel_ext_dir, Print, result_dir
from ..mapping.predicate_mapping import load_name_attr
from util import load_mappings
import json
import os
from tqdm import tqdm

def load_mapping_names(bk2fb):
    fb_uris = set(bk2fb.values())
    Print('#fb uris is %d' %len(fb_uris))
    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
                os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]

    fb_name_map = load_name_attr(name_files, totals, fb_uris)
    Print("#fb name map is %d" %len(fb_name_map))

    bk_name_map = {}
    for bk_url in bk2fb:
        fb_uri = bk2fb[bk_url]
        names = fb_name_map.get(fb_uri, [])
        if len(names) > 0:
            bk_name_map[bk_url] = names
    return bk_name_map

def load_and_write_baike_name(bk_name_map, out_path):
    baike_entity_info_path = os.path.join(result_dir, '360/360_entity_info.json')
    total = 21710208
    Print('load and write baike name to [%s]' %out_path)
    outf = file(out_path, 'w')
    for line in tqdm(file(baike_entity_info_path), total = total):
        p = line.split('\t')
        bk_url = p[0].decode('utf-8')
        names = bk_name_map.get(bk_url, [])
        obj = json.loads(p[1])
        names.append(obj['ename'])
        names.append(obj['title'])
        names = [x.replace('\n',"").strip() for x in names]
        names = list(set(names))

        outf.write("%s\t%s\n" %(bk_url, "\t".join(names)))
    outf.close()


if __name__ == "__main__":
    bk2fb = load_mappings()
    bk_name_map = load_mapping_names(bk2fb)

    out_path = os.path.join(rel_ext_dir, 'baike_names.tsv')
    load_and_write_baike_name(bk_name_map, out_path)

