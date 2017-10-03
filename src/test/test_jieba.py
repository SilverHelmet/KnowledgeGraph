#encoding:utf-8
import jieba
import jieba.posseg as pseg
import re
from ..IOUtil import result_dir
import os

# t m x 时间
s = u'刘德华是一个演员'
print " ".join(jieba.cut(s))
# jieba.load_userdict(os.path.join(result_dir, 'test/dict.txt'))


