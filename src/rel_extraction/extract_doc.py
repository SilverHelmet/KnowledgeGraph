from ..IOUtil import rel_ext_dir, nb_lines_of, Print
import glob
from tqdm import tqdm
import os
import json
from ..baike_process.parse import strip_url, parse_text

def extract_doc(filepath, doc, baike_urls, ignore_table):
    Print('extract doc from [%s]' %os.path.basename(filepath))
    hit = 0
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        p = line.strip().split('\t')
        url = strip_url(p[0])
        if not url in baike_urls:
            continue
        docs = parse_text(url, p[1], ignore_table)
        outf.write("%s\t%s\n" %(url, json.dumps(docs, ensure_ascii = False)))
        hit += 1

    Print("hit = %d" %hit)
        

if __name__ == "__main__":
    mapping_path = os.path.join(rel_ext_dir, 'mapping_result.tsv')
    baike_urls = set()
    for line in file(mapping_path):
        baike_urls.add(line.split('\t')[0].decode('utf-8'))
    Print("#baike_urls is %d" %len(baike_urls))
    out_path = os.path.join(rel_ext_dir, 'baike_doc.json')
    outf = file(out_path, 'w')
    hit = 0
    for filepath in glob.glob('data/360/*finish'):
        extract_doc(filepath, outf, baike_urls, False)
    outf.close()
    
