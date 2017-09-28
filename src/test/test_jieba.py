#encoding:utf-8
import jieba
import jieba.posseg as pseg
from ..mapping.fb_date import BaikeDatetime
from ..baike_process.parse import html_unescape

jieba.initialize()
import re


# t m x 时间
jieba.load_userdict('result/test/dict.txt')
s = '看过刘德华的《陆上行舟》，或许会感叹其作品的超凡脱俗，也或许正是这样，不了解沃纳的作品的人是很难接受其风格的。他的另一部作品《史楚锡流浪记》，也是不可多得的精品。'
s = u'刘德华出生于1993年11月29日, 1883.3'
s = u'29 Amphitrite, 刘德华出生于1993年11月29日, 1883.3'
s = u'哈利·波特（Harry Potter）是英国女作家J.K.罗琳的著名魔幻系列小说与改编电影哈利·波特系列中的主人公，是詹姆波特和莉莉波特的独生子，出生于1980年7月31日，教父为小天狼星布莱克。'
# print s.find(' ')
# re_userdict = re.compile('^(.+?)( [0-9]+)?( [a-z]+)?$', re.U)
# for x in re_userdict.match('29 Amphitrite 5 baike').groups():
#     print x

words = pseg.cut(s)
for word, flag in words:
    print('%s %s' % (word, flag))
# jieba.load_userdict('result/test/dict.txt')

# words = pseg.cut(s)
# for word, flag in words:
#     print('%s %s' % (word, flag))
# words = jieba.cut(u'《星之卡比老鼠进攻》')
# print " ".join(words)

