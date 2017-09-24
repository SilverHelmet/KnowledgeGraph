#encoding:utf-8
import jieba
import jieba.posseg as pseg
from ..mapping.fb_date import BaikeDatetime
from ..baike_process.parse import html_unescape
jieba.load_userdict('result/test/dict.txt')
jieba.initialize()
import re


# t m x 时间
s = '看过刘德华的《陆上行舟》，或许会感叹其作品的超凡脱俗，也或许正是这样，不了解沃纳的作品的人是很难接受其风格的。他的另一部作品《史楚锡流浪记》，也是不可多得的精品。'
s = u'刘德华出生于1993年11月29日, 1883.3'
s = u'29 Amphitrite, 刘德华出生于1993年11月29日, 1883.3'
# print s.find(' ')
# re_userdict = re.compile('^(.+?)( [0-9]+)?( [a-z]+)?$', re.U)
# for x in re_userdict.match('29 Amphitrite 5 baike').groups():
#     print x

words = pseg.cut(u'《星之卡比老鼠进攻》')
for word, flag in words:
    print('%s %s' % (word, flag))

print len(jieba.cut(u'《星之卡比老鼠进攻》'))
# words = jieba.cut(u'《星之卡比老鼠进攻》')
# print " ".join(words)

