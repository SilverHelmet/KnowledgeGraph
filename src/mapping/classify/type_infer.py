#encoding:utf-8
import os
from .util import load_match_result, load_baike_entity_class, load_fb_type, load_baike_entity_title
from ...IOUtil import data_dir, result_dir, Print, classify_dir, rel_ext_dir, write_json_map, load_json_map
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
'''
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
'''

class InfoTypeInfer:
    def __init__(self, path):
        self.baike_info_map = self.init(path)

    def init(self, mapping_path):
        Print('load mapping result from [%s]' %mapping_path)

        baike_info_map = {}
        for line in file(mapping_path):
            p = line.decode('utf-8').split('\t')
            baikeattr = p[0]
            mapping_pairs = eval(p[1])
            mappings = []
            info_count = 0
            info_sum = 0
            info_maximum = 0
            for info_tuple in mapping_pairs:
                if info_tuple[0] == 'sum':
                    info_sum = info_tuple[1]
                    break
            for info_tuple in mapping_pairs:
            	if info_tuple[0] == 'sum':
            		info_count += 1
            		continue
            	info_count += 1
                #print info_tuple[0], info_tuple[1], info_sum
                mapping = Mapping((info_tuple[0], str(info_tuple[1]) + '/' + str(info_sum)))
                if (info_count <= 3 or mapping.hit >= 50) and mapping.hit >= 3:
                    mappings.append(mapping)
            baike_info_map[baikeattr] = mappings

        return baike_info_map

    def infer(self, baike_attrs, prob_map, sep_prob_map):
        for attr in baike_attrs:
            if not attr in self.baike_info_map:
                continue
            mappings = self.baike_info_map[attr]
            for mapping in mappings:
                fb_type = mapping.fb_type()
                prob = mapping.prob()
                if fb_type not in prob_map:
                    prob_map[fb_type] = prob
                else:
                    prob_map[fb_type] += prob
                if fb_type not in sep_prob_map:
                    sep_prob_map[fb_type] = [0, 0, 0]
                sep_prob_map[fb_type][0] = prob
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

    def add_map(self, baike_cls, fb_type):
        baike_cls_cnt = BaikeClassCount(baike_cls)
        baike_cls_cnt.fb_type_cnt = {fb_type: 10000}
        baike_cls_cnt.count = 10000
        baike_cls_cnt.calc_prob()
        self.baike_cls_cnt_map[baike_cls] = baike_cls_cnt


    def infer(self, baike_clses, prob, sep_prob_map):
        for cls in baike_clses:
            if cls not in self.baike_cls_cnt_map:
                continue
            cls_cnt = self.baike_cls_cnt_map[cls]
            cls_prob = cls_cnt.fb_type_prob
            for fb_type in cls_prob:
                if fb_type not in prob:
                    prob[fb_type] = 0
                prob[fb_type] += cls_prob[fb_type]
                if fb_type not in sep_prob_map:
                    sep_prob_map[fb_type] = [0, 0, 0]
                sep_prob_map[fb_type][1] = cls_prob[fb_type]
        return prob

class TitleTypeInfer:
    def __init__(self, path):
        self.baike_title_map = self.init(path)

    def init(self, mapping_path):
        Print('load mapping result from [%s]' %mapping_path)

        baike_title_map = {}
        for line in file(mapping_path):
            p = line.decode('utf-8').split('\t')
            baikeattr = p[0]
            mapping_pairs = eval(p[1])
            mappings = []
            title_count = 0
            title_sum = 0
            title_maximum = 0
            for title_tuple in mapping_pairs:
                if title_tuple[0] == 'sum':
                    title_sum = title_tuple[1]
                    break
            for title_tuple in mapping_pairs:
            	if title_tuple[0] == 'sum':
            		title_count += 1
            		continue
            	title_count += 1
                mapping = Mapping((title_tuple[0], str(title_tuple[1]) + '/' + str(title_sum)))
                if (title_count <= 3 or mapping.hit >= 50) and mapping.hit >= 3:
                    mappings.append(mapping)
            baike_title_map[baikeattr] = mappings

        return baike_title_map

    def infer(self, baike_attrs, prob_map, sep_prob_map):
        for attr in baike_attrs:
            if not attr in self.baike_title_map:
                continue
            mappings = self.baike_title_map[attr]
            for mapping in mappings:
                fb_type = mapping.fb_type()
                prob = mapping.prob() * 2
                if fb_type not in prob_map:
                    prob_map[fb_type] = prob
                else:
                    prob_map[fb_type] += prob
                if fb_type not in sep_prob_map:
                    sep_prob_map[fb_type] = [0, 0, 0]
                sep_prob_map[fb_type][2] = prob
        return prob_map

class ExtraTypeInfer:
    def __init__(self, path):
        self.baike_extra_map = self.init(path)

    def init(self, mapping_path):
        Print('load mapping result from [%s]' %mapping_path)

        baike_extra_map = {}
        for line in file(mapping_path):
            p = line.decode('utf-8').split('\t')
            baikeattr = p[0]
            mapping_dict = eval(p[1])
            mappings = []
            extra_count = 0
            extra_sum = 0
            extra_maximum = 0
            extra_sum = mapping_dict['sum']

            mapping_pairs = []
            for extra_key in mapping_dict:
                if extra_key == 'sum':
                    continue
                mapping_pairs.append((extra_key, mapping_dict[extra_key]))
            sorted(mapping_pairs, key=lambda pairs: pairs[1]) 
            for extra_tuple in mapping_pairs:
                extra_count += 1
                mapping = Mapping((extra_tuple[0], str(extra_tuple[1]) + '/' + str(extra_sum)))
                if (extra_count <= 3 or mapping.hit >= 50) and mapping.hit >= 3:
                    mappings.append(mapping)
            baike_extra_map[baikeattr] = mappings

        return baike_extra_map

    def infer(self, baike_attrs, prob_map, sep_prob_map):
        for attr in baike_attrs:
            if not attr in self.baike_extra_map:
                continue
            mappings = self.baike_extra_map[attr]
            for mapping in mappings:
                fb_type = mapping.fb_type()
                prob = mapping.prob() * 2
                if not fb_type in prob_map:
                    prob_map[fb_type] = prob
                else:
                    prob_map[fb_type] += prob
                if not fb_type in sep_prob_map:
                    sep_prob_map[fb_type] = [0, 0, 0]
                sep_prob_map[fb_type][2] = prob
        return prob_map

class TypeInfer:
    def __init__(self, baike_info_path, baike_cls_path, baike_title_path, extra_info_path):
        #self.infobox_type_infer = InfoboxTypeInfer(path = infobox_path)
        self.info_type_infer = InfoTypeInfer(path = baike_info_path)
        self.baike_cls_infer = BKClassTypeInfer(path = baike_cls_path)
        Print("Baike Class Infer: add mapping type_person -> fb:people.person")
        self.baike_cls_infer.add_map('type_person', 'fb:people.person')
        self.title_type_infer = TitleTypeInfer(path = baike_title_path)
        self.extra_type_infer = ExtraTypeInfer(path = extra_info_path)
    
    def infer(self, info, baike_clses, baike_title, extra_info):
        prob = {}
        sep_prob = {}
        self.info_type_infer.infer(info, prob, sep_prob)
        self.baike_cls_infer.infer(baike_clses, prob, sep_prob)
        self.title_type_infer.infer(baike_title, prob, sep_prob)
        self.extra_type_infer.infer(extra_info, prob, sep_prob)
        return prob, sep_prob

    def choose_one_music_type(self, type_probs, threshold):
        types = set(type_probs.keys())
        if "fb:music.composition" in type_probs and type_probs['fb:music.composition'] >= threshold:
            if "fb:music.recording" in type_probs:
                type_probs.pop('fb:music.recording')
            if "fb:music.album" in type_probs:
                type_probs.pop("fb:music.album")
        elif "fb:music.album" in type_probs and "fb:music.recording" in type_probs:
            max_key = "fb:music.album"
            other_key = "fb:music.recording"
            if type_probs['fb:music.recording'] > type_probs[max_key]:
                max_key = 'fb:music.recording'
                other_key = 'fb:music.album'
            if type_probs[max_key] >= threshold:
                type_probs.pop(other_key)

    def choose_music_type(self, type_probs, threshold):
        composition_prob = type_probs.get('fb:music.composition', 0)
        recording_prob = type_probs.get("fb:music.recording", 0)
        album_prob = type_probs.get("fb:music.album", 0)

        if recording_prob > album_prob:
            max_key = 'fb:music.recording'
            other_key = 'fb:music.album'
        else:
            max_key = 'fb:music.album'
            other_key = 'fb:music.recording'
        
        if composition_prob >= threshold:    
            if type_probs.get(max_key, 0) >= threshold:
                if other_key in type_probs:
                    type_probs.pop(other_key)
        elif recording_prob >= threshold or album_prob >= threshold:
            if other_key in type_probs:
                type_probs.pop(other_key)
            type_probs['fb:music.composition'] = threshold + 0.01

def topk_key(key_map, k):
    keys = sorted(key_map.keys(), key = lambda x: key_map[x], reverse = True)[:k]
    return keys
  
def decide_type(type_probs, schema, chosen_prob):
    if len(type_probs) == 0:
        return []
    types = []
    for fb_type in type_probs:
        if type_probs[fb_type] >= chosen_prob:
            types.append(fb_type)
    if len(types) == 0:
        # types = topk_key(type_probs, 1)
        pass
    types = schema.complement_type(types)
    return types

def find_music_type(props):
    is_album = False
    for prop, value in props:
        if prop == 'fb:music.composition.recordings':
            return ['fb:music.recording']
        if prop == 'fb:music.composition.recorded_as_album':
            is_album = True
    if is_album:
        return ['fb:music.album']
    else:
        return ['fb:music.recording']
            
def load_extra_type(fb_prop_path, total):
    extra_type_map = {}
    fb_type_map = load_fb_type()
    Print('load music extra type')
    for line in tqdm(file(fb_prop_path), total = total):
        fb_uri, obj = line.split('\t')
        fb_uri = fb_uri.decode('utf-8')

        fb_types = fb_type_map[fb_uri]
        extra_types = []
        if "fb:music.composition" in fb_types:
            if "fb:music.recording" not in fb_types and "fb:music.album" not in fb_types:
                extra_types = find_music_type(json.loads(obj))
                # if "fb:music.recording" not in extra_types:
                    # extra_types.append('fb:music.recording')
            else:
                extra_types.append('fb:music.recording')
                    
        elif "fb:music.album" in fb_types or "fb:music.recording" in fb_types:
            extra_types.append('fb:music.composition')
            # if "fb:music.recording" not in extra_types:
            #     extra_types.append('fb:music.recording')
        if len(extra_types) > 0:
            extra_type_map[fb_uri] = extra_types
    return extra_type_map

def infer_type():

    print "start reading"
    bk2fb_map = load_match_result(filepath = os.path.join(rel_ext_dir, 'mapping_result.tsv'))
    baike_cls_map = load_baike_entity_class(os.path.join(data_dir, '360_final_type_url.json'), simple=True)
    baike_title_map = load_baike_entity_title()
    fb_type_map = load_fb_type(fb_uris = set(bk2fb_map.values()) )



    #predicates_map_path = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
    extra_info_path = os.path.join(result_dir, '360/extra_info.json')
    baike_title_path = os.path.join(result_dir, '360/title_type.txt')
    baike_infobox_path = os.path.join(result_dir, '360/info_type.txt')
    baike_cls2tpe_path = os.path.join(classify_dir, 'final_baike_cls2fb_type.json')
    type_infer = TypeInfer(baike_info_path = baike_infobox_path, baike_cls_path = baike_cls2tpe_path, baike_title_path = baike_title_path, extra_info_path = extra_info_path)
    
    extra_type_path = os.path.join(classify_dir, 'extra_type.json')
    extra_type_map = load_json_map(extra_type_path)
    
    out_path = os.path.join(rel_ext_dir, 'test_baike_static_info.tsv')
    outf = file(out_path, 'w')
    
    baike_info_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
    total = 21710208
    cls_hit = 0
    schema = Schema()
    schema.init()
    print "start inferring"
    Print("type infer")
    mega_count = 0
    for line in tqdm(file(baike_info_path), total = total):
        p = line.split('\t')
        baike_url = p[0].decode('utf-8')
        obj = json.loads(p[1])
        names = obj.get('info', {}).keys()
        nb_names = len(names)
        mega_count += 1
        if mega_count > 1000:
            break

        if baike_url in bk2fb_map:
            fb_uri = bk2fb_map[baike_url]
            fb_types = fb_type_map[fb_uri]
            if fb_uri in extra_type_map:
                extra_types = extra_type_map[fb_uri]
                for ext_type in extra_types:
                    fb_types.append(ext_type)
            fb_types = list(set(fb_types))
            chosen_prob = 2
            # outf.write('%s\t%s\t%d\t%s\n' %(baike_url, fb_uri, nb_names * 2 + 3, json.dumps(fb_types)))
            #outf.write('%s\t%s\t%d\t%s\n' %(baike_url, fb_uri, nb_names, json.dumps(fb_types)))
            #continue
        else:
            fb_uri = "None"
            fb_types = []
            chosen_prob = 1

        obj = json.loads(p[1])
        names = obj.get('info', {}).keys()
        extra_info = []
        print obj['info']
        if '职业' in obj['info']:
            extra_info += obj['info']['职业']
        if '运动项目' in obj['info']:
            extra_info += obj['info']['运动项目']
        for j in extra_info:
            print extra_info
        if baike_url in baike_cls_map:
            cls_hit += 1
            clses = baike_cls_map[baike_url]
        else:
            clses = []
        if baike_url in baike_title_map:
            titles = baike_title_map[baike_url]
        else:
            titles = []
        type_probs, sep_type_probs = type_infer.infer(names, clses, titles, extra_info) 
        type_infer.choose_music_type(type_probs, 0.8)
        type_probs_assumed = []
        for fb_type_in in type_probs:
            if type_probs[fb_type_in] >= chosen_prob:
                type_probs_assumed.append((fb_type_in, type_probs[fb_type_in], sep_type_probs[fb_type_in]))
        st_ad = "["
        for j in names:
            st_ad += j + " "
        st_ad += "]["
        print 'class'
        for j in clses:
            st_ad += j + " "
        st_ad += "]["
        for j in titles:
            st_ad += j + " "
        st_ad += "]["
        for j in  extra_info:
            st_ad += j + " "
        st_ad += "]"
        print baike_url, type_probs_assumed, st_ad.encode('utf-8')
        inffered_types = decide_type(type_probs, schema, chosen_prob)
        for fb_type_origin in fb_types:
            if not fb_type_origin in inffered_types:
                inffered_types.append(fb_type_origin)
        outf.write('%s\t%s\t%d\t%s\n' %(baike_url, fb_uri, nb_names, json.dumps(inffered_types)))
    
    outf.close()
    print 'finish inferring '
    Print('baike classes hit = %d' %cls_hit)

def load_and_write_extra_types():
    print 'a'
    fb_prop_path = os.path.join(classify_dir, 'mapped_fb_entity_info.json')
    print 'b'
    total = 6282988
    print 'c'
    extra_type_map = load_extra_type(fb_prop_path, total)
    print 'd'
    write_json_map(os.path.join(classify_dir, 'extra_type.json'), extra_type_map, sort = True)
    print 'e'

def test():
    infobox_path = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
    baike_cls_path = os.path.join(classify_dir, 'final_baike_cls2fb_type.json')
    baike_title_path = os.path.join(result_dir, '360/title_type.txt')
    baike_info_path = os.path.join(result_dir, '360/info_type.txt')
    type_infer = TypeInfer(baike_info_path = baike_info_path, baike_cls_path = baike_cls_path, baike_title_path=baike_title_path)

    baike_cls = ['type_default']

    baike_info = [u'唱片公司', u'所属专辑', u'发行时间', u'歌曲原唱', u'谱曲', u'编曲', u'填词', u'音乐风格', u'版本', u'歌曲语言', u'歌曲时长']
    baike_info = [u'专辑歌手', u'音乐风格', u'发行地区', u'曲目数量', u'唱片公司', u'获得奖项', u'发行时间', u'专辑语言', u'制作人']
    baike_info = [u'中文名称', u'所属公司', u'名师讲堂', u'商业模式', u'特色', u'上市时间']
    baike_info = [u'中文名称', u'所属专辑', u'发行时间', u'歌曲原唱', u'谱曲', u'编曲', u'填词', u'音乐风格', u'MV导演', u'歌曲语言', u'歌曲时长']
    baike_title = [u'基本信息', u'创作背景', u'歌词内容', u'歌曲鉴赏', u'歌曲MV', u'社会影响', u'获奖记录', u'重要演出', u'歌曲争议']
    type_probs = type_infer.infer(baike_info, baike_cls, baike_title)
    type_infer.choose_music_type(type_probs, 0.8)
    # type_infer.choose_one_music_type(type_probs, 0.8)
    decided_inferred_types = []

    for inferred_type in type_probs:
        prob = type_probs[inferred_type]
        
        if prob > 0.8:
            print inferred_type, prob
            decided_inferred_types.append(inferred_type)
    print " ".join(decided_inferred_types)
  


if __name__ == "__main__":
    print 'start loading and writing extra types'
    load_and_write_extra_types()
    print 'start inferring types'
    infer_type()
    print 'finish inferring types'

    #debug
    #test()
