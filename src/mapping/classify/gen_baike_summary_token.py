#encoding:utf-8
import jieba
import os
from ...IOUtil import result_dir
import json
from tqdm import tqdm

if __name__ == "__main__":
    base_dir = os.path.join(result_dir, '360/mapping/classify')
    baike_summary_path = os.path.join(base_dir, 'baike_summary.json')
    inf = file(baike_summary_path, 'r')
    outf = file(os.path.join(base_dir, 'baike_summary.tokens'), 'w')
    total = 1129345
    for line in tqdm(inf, total = total):
        p = line.split('\t')
        baike_url = p[0]
        summary = json.loads(p[1])['summary']
        words = jieba.cut(summary)
        words = [for word in words if word.strip() != ""]
        token_str = " ".join(words)
        outf.write("%s\t%s\n" %(baike_url, token_str))
    outf.close()
    # s = '广州康利酒店是由意大利卡拉利国际服饰集团有限公司投资兴建的现代化商务酒店。座落于广州市白云区黄金地段--机场北门岗贝路。南临火车站，北接新白云机场，地理位置十分优越，交通便利，四通八达。 广州康利酒店的景观建筑由名家设计，风格古朴、典雅、温馨，环境幽雅、干净、舒适，房间内装饰精致、细腻、和谐柔美，尽显豪华气派。酒店内设有各式豪华、标准、精致的商务客房(免费宽带上网)以及露天休闲花园、餐厅、商务中心、商场、停车场、24小时公共区域安全监控、消防系统等各种完备的配套设施。'
    # print " ".join(jieba.cut(s))


 

