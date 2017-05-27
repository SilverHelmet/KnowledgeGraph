import sys
from ..IOUtil import result_dir, Print
import os
import json
from tqdm import tqdm

def extract_name(value):
    suffix = value[-4:]
    assert suffix == '"@en' or suffix == '"@zh'
    name = value[1:-4]
    return name


def load_name_attr(filepaths, totals):
    name_map = {}
    for filepath, total in zip(filepaths, totals):
        Print("load name %s" %filepath)
        for line in tqdm(file(filepath), total = total):
            p = line.split('\t')
            key = p[0].decode('utf-8')
            if not key in name_map:
                name_map[key] = []
            obj = json.loads(p[1])
            if "fb:type.object.name" in obj:
                for x in obj['fb:type.object.name']:
                    name = extract_name(x)
                    name_map[key].append(name)
            if "fb:common.topic.alias" in obj:
                for x in obj['fb:common.topic.alias']:
                    name = extract_name(x)
                    name_map[key].append(name)
    return name_map


if __name__ == "__main__":
    exact_mapping_file = os.path.join(result_dir, "360/mapping/exact_mapping.tsv")
    name_files = [os.path.join(result_dir, 'freebase/entity_name.json'), 
                os.path.join(result_dir, 'freebase/entity_alias.json')]
    totals = [39345270, 2197095]

    name_map = load_name_attr(name_files, totals)
    print name_map['fb:m.010016']