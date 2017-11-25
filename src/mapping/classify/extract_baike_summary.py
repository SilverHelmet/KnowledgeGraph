#encoding: utf-8
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

def merge_summary_and_infobox(summary_path, infobox_path, out_path):
    Print("load summary from [%s]" %summary_path)
    Print("write summary&infobox to [%s]" %out_path)
    outf = file(out_path, 'w')
    summary_map = {}
    for line in tqdm(file(summary_path, 'r'), total = nb_lines_of(summary_path)):
        p = line.split('\t')
        key = p[0]
        summary = json.loads(p[1])['summary']
        # summary = filter_bad_summary(summary)
        summary_map[key] = summary.encode('utf-8')
    Print('add infobox value to summary, path is [%s]' %infobox_path)
    for line in tqdm(file(infobox_path), total = nb_lines_of(infobox_path)):
        p = line.split('\t')
        key = p[0]
        info_values = list()
        info = json.loads(p[1])['info']
        for value_list in info.values():
            for value in value_list:
                info_values.append(value)
        if len(info_values) == 0:
            continue
        
        text = u"。" + u"#".join(info_values)
        text = text.encode('utf-8')
        if not key in summary_map:
            summary_map[key] = text
        else:
            summary_map[key] = summary_map[key] + text
    
    Print("write summary and infobox to [%s]" %out_path)
    outf = file(out_path, 'w')
    for bk_url in tqdm(sorted(summary_map.keys()), total = len(summary_map)):
        summary = {'summary': summary_map[bk_url]}
        outf.write('%s\t%s\n' %(bk_url, json.dumps(summary, ensure_ascii = False)) )
    outf.close()
    # return summary_map    


if __name__ == "__main__":
    
    # mapping_file = os.path.join(result_dir, '360/360_mapping.json')
    # out_dir = os.path.join(result_dir, '360/mapping/classify')
    # baike2fb_map, baike_entities, fb_entities = load_mapping_pairs(mapping_file)

    # baike_entities = set(baike_entities)

    # extract summary
    # nb_files = 461
    # Print("---- parse summary ----")
    # outf = file(os.path.join(rel_ext_dir, 'baike_summary.json'), 'w')
    # cnt = 0
    # for idx, filepath in enumerate(glob.glob('data/360/*finish'), start = 1):
    #     Print('parse %3d %s' %(idx, os.path.basename(filepath)))
    #     cnt += parse(filepath, None, outf)
    #     Print("cnt = %d" %(cnt))
    # outf.close()


    # filter_bad_summary
    # ori_summary_path = os.path.join(rel_ext_dir, 'baike_summary.json')
    # new_summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary.json')

    # filter_summary(ori_summary_path, new_summary_path)

    # merge_summary_with_infobox
    summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary.json')
    infobox_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    summary_infobox_path = os.path.join(rel_ext_dir, 'baike_filtered_summary_with_infobox.json')
    merge_summary_and_infobox(summary_path, infobox_path, summary_infobox_path)
    