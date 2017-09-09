#encoding: utf-8
from ...loader import load_stopwords

if __name__ == "__main__":
    stopwords = load_stopwords()
    s = u"徐 俊 男 ， 博士后 ， 中华医学会 神经病 学分 会 会员 ， 美国 神经病 学 研究院 ( AAN ) 会员 ， 美国 癌症 学会 ( AACR ) 会员 。 先后 于 南京医科大学 、 中山大学 获得 神经病 学 硕士 、 博士学位 。"
    s2 = u'徐俊 ， 中国 国际象棋 棋手 ， 江苏 苏州人 。 曾 打进 FIDE 排名 的 全世界 前 100 名 。 \ n 等级分 : 2005 年 4 月 : 2582 \ n 徐俊 ， 男 ， 博士后 ， 中华医学会 神经病 学分 会 会员 ， 美国 神经病 学 研究院 会员 ， 美国 神经科学 会 会员 。 先后 于 南京医科大学 、 中山大学 获得 神经病 学 硕士 、 博士学位 。 2003 - 2006 于 美国匹兹堡大学 从事 博士后 研究 ， 回国 后 获 国家自然科学基金 、 人事部 留学 归国 人员 启动 基金 及省 、 市 科研 基金 14 项 资助 。 主要 对 老年期 痴呆 及 相关 认知障碍 疾病 ， 以及 神经系统 免疫 疾病 进行 临床 诊治 与 发病 机制 研究 。 已 发表 论文 30 余篇 ， 其中 SCI 论文 7 篇 ， 发表 在 Blood 、 Brain Res 、 J Leuoko Cell Biol 等 核心 期刊 。 现为 南京 脑科 医院 神经内科 主任医师 ， 南京 神经 精神病学 研究所 副所长 ， 神经内科 副 主任 。 兼任 南京医科大学 副教授 、 硕士生 导师 。'
    words = [word for word in s.split(" ") if not word in stopwords]
    words2 = set([word for word in s2.split(" ") if not word in stopwords])
    print len(words2)
    print len(words)
    print len(set(words))
    for w in set(words):
        if not w in words2:
            print w
