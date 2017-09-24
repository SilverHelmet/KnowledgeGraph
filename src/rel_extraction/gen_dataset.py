#encoding: utf-8
import jieba
import jieba.posseg as pseg
from ..IOUtil import rel_ext_dir, Print, cache_dir
import os
from parse_baike_entity import parse_sentence, split_sentences
from .dataset import DatasetFinder
from ..mapping.fb_date import FBDatetime
from ..mapping.predicate_mapping import map_time
import numpy as np

Print('time')
jieba.load_userdict(os.path.join(rel_ext_dir, 'trimmed_baike_dict.txt'))
Print('time')

class Case:
    def __init__(self, st1, ed1, st2, ed2, rel):
        self.st1 = st1
        self.ed1 = ed1
        self.st2 = st2
        self.ed2 = ed2
        self.rel = rel

    def __str__(self):
        return " ".join(map(str, [self.st1, self.ed1, self.st2, self.ed2, self.rel]) )



def map_to_fb(objs, finder):
    ret = []
    for st, ed, obj, obj_type in objs:
        if obj_type == 'time':
            ret.append((st, ed, obj, obj_type))
        else:
            fb_uris = finder.name2fb_map.get(obj, [])
            for fb_uri in fb_uris:
                ret.append((st, ed, fb_uri, obj_type))
    return ret

def try_get_rel(obj1, obj2, obj2_type, finder, cache):
    if obj2_type == 'time':
        time_ttls = finder.fb_ttls_map.get(obj1, ([], []))[1]
        for prop, value in time_ttls:
            if value not in cache:
                cache[value] = FBDatetime.parse_fb_datetime(value)
            time_obj = cache[value]
            if map_time(time_obj, obj2):
                return prop
    else:
        entity_ttls = finder.fb_ttls_map.get(obj1, ([], []))[0]
        for prop, value in entity_ttls:
            if value == obj2:
                return prop
    return None


def gen_dataset(sentence, finder):
    ret = pseg.cut(sentence)
    words = []
    flags = []
    for word, flag in ret:
        words.append(word)
        flags.append(flag)

    objs = parse_sentence(words, flags)
    fb_objs = map_to_fb(objs, finder)

    cache = {}
    cases = []
    none_cases = []
    for obj1_st, obj1_ed, obj1, obj1_type in fb_objs:
        if obj1_type == 'time':
            continue 
        for obj2_st, obj2_ed, obj2, obj2_type in fb_objs:
            if obj2_st <= obj1_st and obj2_type != 'time':
                continue
            rel = try_get_rel(obj1, obj2, obj2_type, finder, cache)
            if rel:
                case = Case(obj1_st, obj1_ed, obj2_st, obj2_ed, rel)
                cases.append(case)
            else:
                case = Case(obj1_st, obj1_ed, obj2_st, obj2_ed, 'none')
                none_cases.append(case)
    if len(cases) > 0:
        return cases
    elif len(none_cases) > 0:
        x = np.random.randint(low = 0, high = len(none_cases))
        return none_cases[x:x+1]
    else:
        return []

def test():
    x = u"《星之卡比老鼠进攻》是欧洲游戏制造商Nintendo公司于2006-11-02制作的一款动作游戏。游戏故事讲述的是，玩家控制的卡比和3只小老鼠，当然还有他们的团长之间的故事，玩家的目标是和呐喊团争夺一个神秘宝盒。"
    x = u'刘德华制作了星之卡比老鼠进攻。'
    sentences = split_sentences(x)
    # jieba.add_word(u'星之卡比老鼠进攻', 5, 'baike')
    # jieba.add_word(u'Nintendo', 5, 'baike')
    # jieba.add_word(u'游戏故事', 5, 'baike')
    # jieba.add_word(u'呐喊团', 5, 'baike')
    # jieba.add_word(u'神秘宝盒', 5, 'baike')
    
    # name2fb_path = os.path.join(cache_dir, 'DatasetFinder.name2fb.sample.cache')
    # fb_ttls_path = os.path.join(cache_dir, 'DatasetFinder.fb_ttls.sample.cache')
    name2fb_path = os.path.join(cache_dir, 'DatasetFinder.name2fb.cache')
    fb_ttls_path = os.path.join(cache_dir, 'DatasetFinder.fb_ttls.cache')
    finder = DatasetFinder.load_from_cache(name2fb_path, fb_ttls_path)
    for x in gen_dataset(sentences[0], finder):
        print x
    print '-' * 50
    for x in gen_dataset(sentences[1], finder):
        print x

def gen_dataset_from_baike():
    sample_path = os.path.join(rel_ext_dir, 'random_baike_urls.txt')
    bk_urls = set()
    for line in file(sample_path):
        bk_urls.add(line.strip().decode('utf-8'))

    


if __name__ == "__main__":
    test()
    # jieba.add_word
    # jieba.initialize()

    # x = u'刘德华出生于1993年11月29日, 1883.3'
    # for word, flag in pseg.cut(x):
        # print word, flag
    