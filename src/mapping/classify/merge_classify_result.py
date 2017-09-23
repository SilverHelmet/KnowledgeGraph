from ...IOUtil import classify_dir
from .util import load_baike_entity_class, load_fb_type, load_baike_attr_names
from .type_infer import TypeInfer, topk_key
import os

if __name__ == "__main__":
    classify_result_path = os.path.join(classify_dir, 'classify_result.tsv')
    outf = file(os.path.join(classify_dir, 'mapping_result.tsv'), 'w')
    bk2fb = {}
    for line in file(classify_result_path):
        bk_url, fb_uri, score = line.decode('utf-8').split('\t')
        score = float(score)
        if score < 0.1:
            continue
        bk2fb[bk_url] = fb_uri
        outf.write('%s\t%s\n' %(bk_url, fb_uri))

    one2one_map_path = os.path.join(classify_dir, 'good_one2one_mappings.txt')

    one2one_mappings = []
    bk_urls = set()
    fb_uris = set()
    for line in file(one2one_map_path):
        bk_url, fb_uri, score = line.decode('utf-8').split('\t')
        score = float(score)
        if bk_url in bk2fb:
            continue
        one2one_mappings.append((bk_url, fb_uri))
        bk_urls.add(bk_url)
        fb_uris.add(fb_uri)

    bk_cls_map = load_baike_entity_class(os.path.join(classify_dir, 'baike_cls.tsv'), baike_urls = bk_urls, simple = True)
    fb_type_map = load_fb_type(filepath = os.path.join(classify_dir, 'fb_entity_type.json'), fb_uris = fb_uris) 
    bk_info_map = load_baike_attr_names(filepath = os.path.join(result_dir, '360/360_entity_info_processed.json'),
                                         total = 21710208, baike_urls = baike_urls)

    infobox_path = os.path.join(result_dir, '360/mapping/one2one_predicates_map.json')
    baike_cls_path = os.path.join(classify_dir, 'baike_cls2fb_type.json')
    type_infer = TypeInfer(infobox_path = infobox_path, baike_cls_path = baike_cls_path)

    extra_mappings = 0
    for bk_url, fb_uris in mappings:
        bk_clses = bk_cls_map.get(bk_url, [])
        bk_info = bk_info_map.get(bk_url, [])
        fb_types = fb_type_map.get(fb_uri, [])
        type_probs = type_infer.infer(bk_info, bk_clses)
        top_types = topk_key(type_probs, 2)
        for top_type in top_types:
            if top_type in fb_types:
                outf.write("%s\t%s\n" %(bk_url, fb_uris))
                extra_mappings += 1
                break
    print "#extra mappings = %d" %extra_mappings
    outf.close()

