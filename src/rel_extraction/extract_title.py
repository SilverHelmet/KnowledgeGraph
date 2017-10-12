from ..IOUtil import rel_ext_dir
from ..baike_process.parse import strip_url, parse_text
import os
import glob

def extract_title(filepath, outf):
    Print('extract doc from [%s]' %os.path.basename(filepath))

    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        p = line.strip().split('\t')
        url = strip_url(p[0])

        docs = parse_text(url, p[1])
        titles = docs.keys()

        outf.write("%s\t%s\n" %(url, json.dumps(titles, ensure_ascii = False)))


if __name__ == "__main__":
    out_path = os.path.join(rel_ext_dir, 'baike_titles.json')
    outf = file(out_path, 'w')
    nb_files = 461
    for idx, filepath in enumerate(glob.glob('data/360/*finish'), start = 1):
        Print('parse %3d %s' %(idx, os.path.basename(filepath)))
        extract_title(filepath, outf)
    outf.close()