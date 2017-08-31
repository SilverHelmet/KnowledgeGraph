from ...baike_process.parse import strip_url, parse_summary
from .gen_fb_property import load_mapping_pairs
import glob
from tqdm import tqdm
from ...IOUtil import Print, nb_lines_of, result_dir
import json
import base64
import os

def parse(filepath, entities, outf):
    cnt = 0
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        parts = line.split('\t')
        url = strip_url(parts[0])
        if url in entities:
            content = json.loads(base64.b64decode(tokens[1]))
            summary = parse_summary(content)
            if summary is not None:
                obj = {'summary': summary}
                outf.write("%s\t%s\n" %(url, json.dumps(obj, ensure_ascii = False)))
                cnt += 1
    return cnt



if __name__ == "__main__":
    
    mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    out_dir = os.path.join(result_dir, '360/mapping/classify')
    baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)

    baike_entities = set(baike_entities)

    nb_files = 461
    Print("---- parse summary ----")
    outf = file(os.path.join(out_dir, 'baike_summary.json'), 'w')
    cnt = 0
    for idx, filepath in enumerate(glob.glob('data/360/*finish'), start = 1):
        Print('parse %3d %s' %(idx, os.path.basename(filepath)))
        cnt += parse(filepath, baike_entities, outf)
        Print("cnt = %d" %(cnt))
    outf.close()