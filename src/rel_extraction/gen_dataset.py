#encoding: utf-8
import jieba
import jieba.posseg as pseg
from ..IOUtil import rel_ext_dir
import os

jieba.load_userdict(os.path.join(rel_ext_dir, 'baike_dict.txt'))

if __name__ == "__main__":
    x = u"《星之卡比老鼠进攻》是欧洲游戏制造商Nintendo公司制作的一款动作游戏。游戏故事讲述的是，玩家控制的卡比和3只小老鼠，当然还有他们的团长之间的故事，玩家的目标是和呐喊团争夺一个神秘宝盒。"
    for word, flag in pseg.cut(x):
        print word, flag