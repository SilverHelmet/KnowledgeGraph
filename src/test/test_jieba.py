#encoding:utf-8
import jieba
import jieba.posseg as pseg
from ..mapping.fb_date import BaikeDatetime
jieba.load_userdict('result/test/dict.txt')
jieba.initialize()


# t m x 时间
print jieba.get_dict_file()
s = '看过刘德华的《陆上行舟》，或许会感叹其作品的超凡脱俗，也或许正是这样，不了解沃纳的作品的人是很难接受其风格的。他的另一部作品《史楚锡流浪记》，也是不可多得的精品。'
s = u"刘德华出生于1993年11月29日"
print BaikeDatetime.parse(s)
words = pseg.cut(s)
for word, flag in words:
    print('%s %s' % (word, flag))