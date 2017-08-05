from ..IOUtil import result_dir, nb_lines_of
import os
from tqdm import tqdm
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == "__main__":
    entity_info_filepath = os.path.join(result_dir, '360/360_entity_info_processed.json')
    attr_cnt = {}
    for line in tqdm(file(entity_info_filepath), total = nb_lines_of(entity_info_filepath)):
        p = line.split('\t')
        baike_url = p[0]
        attrs = json.loads(p[1])
        info_obj = attrs['info']
        for name in info_obj:
            if not name in attr_cnt:
                attr_cnt[name] = 0
            attr_cnt[name] += 1
        
    outf = file(os.path.join(doc_dir, '360_info_stat.json'), 'w')
    for name in sorted(attr_cnt.keys(), key = lambda x: attr_cnt[x], reverse = True):
        obj = {
            "count": attr_cnt[name]
        }
        outf.write("%s\t%s\n" %(name, attr_cnt[name]))
    outf.close()

