#encoding:utf-8
import jieba
import jieba.posseg as pseg
import re
from ..IOUtil import result_dir
import os

# t m x 时间
s = u'出生日期：'
s = u'"1,2,9-壬三醇'
jieba.load_userdict(os.path.join(result_dir, 'test/dict.txt'))
for word, flag in pseg.cut(s):
    print "%s:%s" %(word, flag),

