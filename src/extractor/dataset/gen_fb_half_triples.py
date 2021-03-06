from src.IOUtil import classify_dir, result_dir, rel_ext_dir, nb_lines_of, Print
from tqdm import tqdm
import json
from src.fb_process.process_fb_result import process_fb_value
from src.mapping.predicate_mapping import load_name_attr
import os
from src.extractor.resource import Resource
from .error_property import load_error_property

def process(inpath, outpath, name_map, fb_uris):
    schema = Resource.get_singleton().get_schema()
    error_props = load_error_property()

    Print('process %s' %inpath)
    outf = file(outpath, 'w')
    error_outf = file('log/error.log', 'w')
    for line in tqdm(file(inpath), total  = nb_lines_of(inpath)):
        fb_key, rels = line.split('\t')
        if not fb_key in fb_uris:
            continue
        rels = json.loads(rels)
        new_rels = {}
        for fb_property, obj in rels:
            if schema.reverse_property(fb_property) == fb_property:
                continue
            if fb_property in error_props:
                continue
            if obj in name_map:
                names = name_map[obj]
            else:
                literal = process_fb_value(obj)
                if literal.startswith('fb:m.'):
                    # error_outf.write('error property %s, entity %s\n' %(fb_property, fb_key))
                    names = []
                else:
                    names = [process_fb_value(obj)]
            if len(names) == 0:
                continue
            if not fb_property in new_rels:
                new_rels[fb_property] = []
            new_rels[fb_property].extend(names)

        big = False
        for fb_property in new_rels:
            new_rels[fb_property] = list(set(new_rels[fb_property]))
            if len(new_rels[fb_property]) > 300:
                error_outf.write('big size property of url = %s, property = %s, size = %d\n' %(fb_key, fb_property, len(new_rels[fb_property])) )
        outf.write("%s\t%s\n" %(fb_key, json.dumps(new_rels, ensure_ascii = False)))
    outf.close()
    error_outf.close()


if __name__ == "__main__":
    mapping_path = os.path.join(rel_ext_dir, 'mapping_result.tsv')
    fb_uris = set()
    for line in file(mapping_path):
        fb_uris.add(line.strip().split('\t')[1])


    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'),
        os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]
    name_map = load_name_attr(name_files, totals)

    in_path = os.path.join(classify_dir, 'mapped_fb_entity_info.json')
    out_path = os.path.join(rel_ext_dir, 'mapped_fb_entity_info_processed.json')
    process(in_path, out_path, name_map, fb_uris)