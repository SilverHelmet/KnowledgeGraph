#encoding: utf-8
import jieba
import jieba.posseg as pseg
from ..IOUtil import rel_ext_dir, Print
import os
# Print('time')

# jieba.load_userdict(os.path.join(rel_ext_dir, 'baike_dict.txt'))
# Print('time')

if __name__ == "__main__":
    # jieba.add_word(u"Nintendo", 5, 'baike')
    # jieba.add_word(u"", 5, 'baike')
    x = u"《星之卡比老鼠进攻》是欧洲游戏制造商Nintendo公司制作的一款动作游戏。游戏故事讲述的是，玩家控制的卡比和3只小老鼠，当然还有他们的团长之间的故事，玩家的目标是和呐喊团争夺一个神秘宝盒。"
    x = u'欧洲'
    x = u'Nintendo'
    # x = u'刘德华出生于1993年11月29日, 1883.3'
    for word, flag in pseg.cut(x):
        print word, flag
    
    # jieba.add_word
    # jieba.initialize()

    # x = u'刘德华出生于1993年11月29日, 1883.3'
    # for word, flag in pseg.cut(x):
        # print word, flag
    