import json
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
f1 = open("/home/lhr/KnowledgeGraph/result/360/360_entity_info_processed.json", "r")
f2 = open("/home/lhr/KnowledgeGraph/result/360/mapping/classify/classify_result.tsv", "r")
f3 = open("/home/lhr/KnowledgeGraph/result/360/mapping/classify/fb_entity_type.json", "r")
f4 = open("/home/lhr/KnowledgeGraph/result/rel_extraction/baike_doc.json", "r")
info_type_dict = {}
url_fb_dict = {}
fb_type_dict = {}
title_type_dict = {}
for line in f2:
    tmp = line.split('\t')
    url = tmp[0]
    fb = tmp[1]
    score = tmp[2]
    if float(score) <= 0.4:
        continue
    url_fb_dict[url] = fb
for line in f3:
    tmp = line.split('\t')
    fb = tmp[0]
    fb_type = tmp[1]
    fb_type = json.loads(fb_type)
    types = fb_type["fb:type.object.type"]
    fb_type_dict[fb] = types
for line in f1:
    baike_key, obj = line.split('\t')
    obj = json.loads(obj)
    info = obj['info']
    if url_fb_dict.has_key(baike_key) == False:
        continue
    fb = url_fb_dict[baike_key]
    if fb_type_dict.has_key(fb) == False:
        continue
    types = fb_type_dict[fb]
    for t in types:
        for key, value in info.items():
            key = json.dumps(key, ensure_ascii=False)
            if info_type_dict.has_key(key):
                if len(info_type_dict[key]) >= 100:
                    continue
                info_type_dict[key]["sum"] += 1
                if info_type_dict[key].has_key(t):
                    info_type_dict[key][t] += 1
                else:
                    info_type_dict[key].update({t: 1})
            else:
                info_type_dict.update({key: {t: 1}})
                info_type_dict[key]["sum"] = 1
for line in f4:
    baike_key, obj = line.split('\t')
    obj = json.loads(obj)
    info = obj
    if url_fb_dict.has_key(baike_key) == False:
        continue
    fb = url_fb_dict[baike_key]
    if fb_type_dict.has_key(fb) == False:
        continue
    types = fb_type_dict[fb]
    for t in types:
        for key, value in info.items():
            key = json.dumps(key, ensure_ascii=False)
            key = key[1:len(key) - 1]
            if key == "intro_summary":
                continue
            title = key.split("_")
            for k in title:
                if len(k) == 0:
                    continue
                if title_type_dict.has_key(k):
                    if len(title_type_dict[k]) >= 100:
                        continue
                    title_type_dict[k]["sum"] += 1
                    if title_type_dict[k].has_key(t):
                        title_type_dict[k][t] += 1
                    else:
                        title_type_dict[k].update({t: 1})
                else:
                    title_type_dict.update({k: {t: 1}})
                    title_type_dict[k]["sum"] = 1
info_tmp = dict()
title_tmp = dict()
for key in info_type_dict:
    sorted_types = sorted(info_type_dict[key].items(), key=lambda d: d[1], reverse=True)
    info_tmp.update({key: info_type_dict[key]["sum"]})
    info_type_dict[key] = sorted_types
sorted_info_type_dict = {}
info_tmp = sorted(info_tmp.items(), key=lambda d: d[1], reverse=True)
for key in info_tmp:
    sorted_info_type_dict.update({key[0]: info_type_dict[key[0]]})
for key in title_type_dict:
    sorted_types = sorted(title_type_dict[key].items(), key=lambda d: d[1], reverse=True)
    title_tmp.update({key: title_type_dict[key]["sum"]})
    title_type_dict[key] = sorted_types
sorted_title_type_dict = {}
title_tmp = sorted(title_tmp.items(), key=lambda d: d[1], reverse=True)
for key in title_tmp:
    sorted_title_type_dict.update({key[0]: title_type_dict[key[0]]})
f5 = open("info_type.txt", "w")
f6 = open("title_type.txt", "w")
for key in info_tmp:
    f5.write(key[0][1:len(key[0]) - 1])
    f5.write("\t")
    if len(sorted_info_type_dict[key[0]]) < 10:
        f5.write(str(sorted_info_type_dict[key[0]]))
    else:
        f5.write(str(sorted_info_type_dict[key[0]][0:10]))
    f5.write("\n")
for key in title_tmp:
    f6.write(key[0])
    f6.write("\t")
    if len(sorted_title_type_dict[key[0]]) < 10:
        f6.write(str(sorted_title_type_dict[key[0]]))
    else:
        f6.write(str(sorted_title_type_dict[key[0]][0:10]))
    f6.write("\n")
f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
