from src.baike_process.parse import strip_url, parse_summary
from .gen_fb_property import load_mapping_pairs
import glob
from tqdm import tqdm
from src.IOUtil import Print, nb_lines_of, result_dir, rel_ext_dir
import json
import base64
import os
from src.baike_process.process_page import split_sentences

def parse(filepath, entities, outf):
    cnt = 0
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        parts = line.split('\t')
        url = strip_url(parts[0])
        if entities is None or url in entities:
            try:
                content = json.loads(base64.b64decode(parts[1]))
            except Exception, e:
                print "error", e
                print parts[1]
                continue
            
            summary = parse_summary(content)
            if summary is not None:
                obj = {'summary': summary}
                outf.write("%s\t%s\n" %(url, json.dumps(obj, ensure_ascii = False)))
                cnt += 1
    return cnt

def filter_bad_summary(summary):
    sentences = split_sentences(summary, max_length = 200)
    new_s = []
    for sentence in sentences:
        if len(sentence) >= 200:
            break
        if len(sentence.split(u"：")) >= 4:
            break
        new_s.append(sentence)
    return u''.join(new_s)

def filter_summary(ori_path, new_path):
    Print('filter summary from [%s] to [%s]' %(os.path.basename(ori_path), os.path.basename(new_path)))
    outf = file(new_path, 'w')
    for line in tqdm(file(ori_path), total = nb_lines_of(ori_path)):
        bk_url, summary = line.split('\t')
        summary = json.loads(summary)['summary']
        new_summary = filter_bad_summary(summary)
        new_summary = {'summary': new_summary}
        outf.write("%s\t%s\n" %(bk_url, json.dumps(new_summary, ensure_ascii = False)) )
    outf.close()



if __name__ == "__main__":
    
    # mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    # out_dir = os.path.join(result_dir, '360/mapping/classify')
    # baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)

    # baike_entities = set(baike_entities)

    # nb_files = 461
    # Print("---- parse summary ----")
    # outf = file(os.path.join(rel_ext_dir, 'baike_summary.json'), 'w')
    # cnt = 0
    # for idx, filepath in enumerate(glob.glob('data/360/*finish'), start = 1):
    #     Print('parse %3d %s' %(idx, os.path.basename(filepath)))
    #     cnt += parse(filepath, None, outf)
    #     Print("cnt = %d" %(cnt))
    # outf.close()

    ori_summary_path = os.path.join(rel_ext_dir, 'baike_summary.json')
    new_summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary.json')

    filter_summary(ori_summary_path, new_summary_path)
    