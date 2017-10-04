#encoding:utf-8
import jieba
import jieba.posseg as pseg
import re
from ..IOUtil import result_dir
import os

# t m x 时间
s = u'刘德华是一个演员'
s = '《新媒体》，美国电影，J.J. Adler导演，Chris Stack、约翰·罗斯曼、BethAnn Bonner主演。'
for word, flag in pseg.cut(s):
    print "%s:%s" %(word, flag),
# print " ".join(jieba.cut(s))
# jieba.load_userdict(os.path.join(result_dir, 'test/dict.txt'))


