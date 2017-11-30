from src.IOUtil import classify_dir, result_dir, rel_ext_dir, nb_lines_of, Print
from tqdm import tqdm
import json
from src.fb_process.process_fb_result import process_fb_value

def process(inpath, outpath, name_map):
    Print('process %s' %inpath)
    outf = file(outpath, 'w')
    error_outf = file('log/error.log')
    for line in tqdm(file(inpath), total  = nb_lines_of(inpath)):
        fb_key, rels = line.split('\t')
        rels = json.loads(rels)
        if len(rels) > 500:
            error_outf.write("big size rels for uri: %s\n" %fb_key)
        new_rels = {}
        for fb_property, obj in rels:
            
            if obj in name_map:
                name = name_map[obj]
            else:
                name = [process_fb_value(obj)]
            if not fb_property in new_rels:
                new_rels[fb_property] = []
            new_rels[fb_property].extend(name)

        big = False
        for fb_property in new_rels:
            new_rels[fb_property] = list(set(new_rels[fb_property]))
            if len(new_rels[fb_property]) > 500:
                big = True
        if big:
            error_outf.write('big size property of url = %s, property = %s\n' %(fb_key, fb_property))
        outf.write("%s\t%s\n" %(fb_key, json.dumps(new_rels, ensure_ascii = False)))
    outf.close()
    error_outf.close()


if __name__ == "__main__":
    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
        os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]
    name_map = load_name_attr(name_files, totals)

    in_path = os.path.join(classify_dir, 'mapped_fb_entity_info.json')
    out_path = os.path.join(rel_ext_dir, 'mapped_fb_entity_info_processed.json')
    process(in_path, out_path)