#encoding:utf-8
import jieba
import jieba.posseg as pseg
from ..mapping.fb_date import BaikeDatetime
jieba.load_userdict('result/test/dict.txt')
jieba.initialize()

print jieba.get_dict_file()
s = '看过刘德华的《陆上行舟》，或许会感叹其作品的超凡脱俗，也或许正是这样，不了解沃纳的作品的人是很难接受其风格的。他的另一部作品《史楚锡流浪记》，也是不可多得的精品。'
s = u"1997年，《星之卡比老鼠进攻》是欧洲游戏制造商Nintendo公司制作的一款动作游戏。游戏故事讲述的是，玩家控制的卡比和3只小老鼠，当然还有他们的团长之间的故事，玩家的目标是和呐喊团争夺一个神秘宝盒。"
print BaikeDatetime.parse(s)
# words = pseg.cut(s)
# for word, flag in words:
    # print('%s %s' % (word, flag))