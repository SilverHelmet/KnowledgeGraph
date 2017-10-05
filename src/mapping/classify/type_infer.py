#encoding:utf-8
import os
from .util import load_match_result, load_baike_entity_class, load_fb_type
from ...IOUtil import result_dir, Print, classify_dir, rel_ext_dir
from ...fb_process.extract_util import get_type
import json
from .gen_baike_class_to_fb import BaikeClassCount
from tqdm import tqdm
from ...schema.schema import Schema

class Mapping:
    def __init__(self, pair):
        self.fb_prop, prob = pair
        hit, total = prob.split('/')
        self.hit = int(hit)
        self.total = int(total)

    def prob(self):
        return (self.hit + 0.0) / (self.total + 6)

    def fb_type(self):
        return get_type(self.fb_prop)
    
    def __str__(self):
        return ' '.join([self.fb_prop, '%d/%d' %(self.hit, self.total)])

class InfoboxTypeInfer:
    def __init__(self, path):
        self.baikeattr2fb_type = self.init(path)

    def init(self, mapping_path):
        Print('load mapping result from [%s]' %mapping_path)

        baikeattr2fb_type = {}
        for line in file(mapping_path):
            p = line.decode('utf-8').split('\t')
            baikeattr = p[0]
            mapping_pairs = json.loads(p[1])[:5]
            mappings = []
            for index, pair_str in enumerate(mapping_pairs, start = 1):
                mapping = Mapping(pair_str)

                if (index <= 2 or mapping.hit >= 50) and mapping.hit >= 3:
                    mappings.append(mapping)
            baikeattr2fb_type[baikeattr] = mappings

        return baikeattr2fb_type

    def infer(self, baike_attrs, prob_map):
        for attr in baike_attrs:
            if not attr in self.baikeattr2fb_type:
                continue
            mappings = self.baikeattr2fb_type[attr]
            for mapping in mappings:
                fb_type = mapping.fb_type()
                prob = mapping.prob()
                if not fb_type in prob_map:
                    prob_map[fb_type] = prob
                else:
                    prob_map[fb_type] += prob
        return prob_map      

class BKClassTypeInfer:
    def __init__(self, path):
        self.baike_cls_cnt_map = self.init(path)

    def init(self, path):
        Print("init Baike Url type infer from [%s]" %path)
        baike_cls_cnt_map = {}
        for line in file(path):
            obj = json.loads(line)
            baike_cls_cnt = BaikeClassCount.load_from_obj(obj)
            baike_cls_cnt.calc_prob()
            baike_cls = baike_cls_cnt.baike_cls
            baike_cls_cnt_map[baike_cls] = baike_cls_cnt
        return baike_cls_cnt_map

    def infer(self, baike_clses, prob):
        for cls in baike_clses:
            if cls not in self.baike_cls_cnt_map:
                continue
            cls_cnt = self.baike_cls_cnt_map[cls]
            cls_prob = cls_cnt.fb_type_prob
            for fb_type in cls_prob:
                if not fb_type in prob:
                    prob[fb_type] = 0
                prob[fb_type] += cls_prob[fb_type]
        return prob

class TypeInfer:
    def __init__(self, infobox_path, baike_cls_path):
        self.infobox_type_infer = InfoboxTypeInfer(path = infobox_path)
        self.baike_cls_infer = BKClassTypeInfer(path = baike_cls_path)
    
    def infer(self, info, baike_clses):
        prob = {}
        self.infobox_type_infer.infer(info, prob)
        self.baike_cls_infer.infer(baike_clses, prob)
        return prob

def topk_key(key_map, k):
    keys = sorted(key_map.keys(), key = lambda x: key_map[x], reverse = True)[:k]
    return keys

def test():
    infobox_path = os.path.join(result_dir, '360/mapping/one2one_predicates_map.json')
    baike_cls_path = os.path.join(classify_dir, 'baike_cls2fb_type.json')
    type_infer = TypeInfer(infobox_path = infobox_path, baike_cls_path = baike_cls_path)
    info = [u'民族', u'影视作品', u'音乐作品']
    info = [u"时间", u"专辑", u"风格", u"公司"]
    info = [u'职业']
    # clses = [u'prod:art:music']
    clses = [u'person']
    res = type_infer.infer(info, clses)
    print res
    print topk_key(res, 2)
    
def decide_type(type_probs, schema):
    if len(type_probs) == 0:
        return []
    types = []
    for fb_type in type_probs:
        if type_probs[fb_type] >= 0.8:
            types.append(fb_type)
    if len(types) == 0:
        types = topk_key(type_probs, 1)
    types = schema.complement_type(types)
    return types
    
    

def infer_type():
    bk2fb_map = load_match_result(filepath = os.path.join(rel_ext_dir, 'mapping_result.tsv'))
    baike_cls_map = load_baike_entity_class()
    fb_type_map = load_fb_type(fb_uris = set(bk2fb_map.values()) )
    

    predicates_map_path = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
    baike_cls2tpe_path = os.path.join(classify_dir, 'final_baike_cls2fb_type.json')
    type_infer = TypeInfer(infobox_path = predicates_map_path, baike_cls_path = baike_cls2tpe_path)
    
    
    out_path = os.path.join(rel_ext_dir, 'baike_static_info.tsv')
    outf = file(out_path, 'w')
    
    baike_info_path = os.path.join(result_dir, '360/360_entity_info.json')
    total = 21710208
    cls_hit = 0
    schema = Schema()
    schema.init()
    Print("type infer")
    for line in tqdm(file(baike_info_path), total = total):
        p = line.split('\t')
        baike_url = p[0].decode('utf-8')
        obj = json.loads(p[1])
        names = obj.get('info', {}).keys()
        nb_names = len(names)

        if baike_url in bk2fb_map:
            fb_uri = bk2fb_map[baike_url]
            fb_types = fb_type_map[fb_uri]
            outf.write('%s\t%s\t%d\t%s\n' %(baike_url, fb_uri, nb_names, json.dumps(fb_types)))
            continue

        obj = json.loads(p[1])
        names = obj.get('info', {}).keys()
        if baike_url in baike_cls_map:
            cls_hit += 1
            clses = baike_cls_map[baike_url]
        else:
            clses = []
        type_probs = type_infer.infer(names, clses) 
        inffered_types = decide_type(type_probs, schema)
        outf.write('%s\t%s\t%d\t%s\n' %(baike_url, "None", nb_names, json.dumps(inffered_types)))

    
    outf.close()
    Print('baike classes hit = %d' %cls_hit)
    


if __name__ == "__main__":
    # infer_type()

    infobox_path = os.path.join(result_dir, '360/mapping/one2one_predicates_map.json')
    baike_cls_path = os.path.join(classify_dir, 'baike_cls2fb_type.json')
    type_infer = TypeInfer(infobox_path = infobox_path, baike_cls_path = baike_cls_path)

    baike_cls = ['prod:art:filmtv']
    baike_info = [u'唱片公司', u'所属专辑', u'发行时间', u'歌曲原唱', u'谱曲', u'编曲', u'填词', u'音乐风格', u'版本', u'歌曲语言', u'歌曲时长']
    type_probs = type_infer.infer(baike_info, baike_cls)
    decided_inferred_types = []
    for inferred_type in type_probs:
        prob = type_probs[inferred_type]
        if prob > 0.8:
            decided_inferred_types.append(inferred_type)
    print " ".join(decided_inferred_types)