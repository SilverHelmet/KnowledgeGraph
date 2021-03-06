#encoding: utf-8
from ...loader import load_stopwords
from .gen_summary_sim_score import gen_word_cnt

if __name__ == "__main__":

    stopwords = load_stopwords()
    s = u"徐 俊 男 ， 博士后 ， 中华医学会 神经病 学分 会 会员 ， 美国 神经病 学 研究院 ( AAN ) 会员 ， 美国 癌症 学会 ( AACR ) 会员 。 先后 于 南京医科大学 、 中山大学 获得 神经病 学 硕士 、 博士学位 。"
    s = u'人物 简介 徐俊 ， 男 ， 藏族 ， 生于 1966 年 3 月 ， 四川 泸定县 人 ， 大学 文化 。 1992 年 7 月 参加 工作 ， 1996 年 5 月 加入 中国共产党 ， 现任 泸定县 人民政府 副县长 。 个人简历 如下 : 1973 年 9 月 - 1978 年 7 月 在岚安 小学  读书 ; 1978 年 9 月 - 1981 年 7 月 在岚安读 初中 ; 1981 年 9 月 - 1983 年 7 月 分别 于岚安 学校 、 泸定 中学 读 初中 ; 1983 年 9 月 - 1985 年 7 月 在 泸定 四中 读 职业高中 ; 1985 年 9 月 - 1986 年 4 月 在 泸定县 岚 安乡 乡 林业 员 ; 1986 年 4 月 - 1986 年 12 月 在 理塘 县 林业局 工作 ( 招聘 技术员 ) ; 1986 年 12 月 - 1987 年 7 月 在 泸定 中学 补习 高中 ; 1987 年 9 月 - 1992 年 7 月 在 西南 民族 学院 读书 ; 1992 年 7 月 - 1993 年 4 月 在 泸定县 烹坝 乡政府 工作 ; 1993 年 4 月 - 1993 年 12 月 在 泸定县 政府 办公室 任 秘书 ; 1994 年 1 月 - 2000 年 11 月 在 县 计经委 工作 ; 2000 年 11 月 至 2006 年 12 月 29 日 在 县政府 办公室 工作 ， 任 办公室 副 主任 、 主任 ; 2006 年 12 月 30 日 至今 任 县政府 副县长 。'
    s2 = u'徐俊 ， 中国 国际象棋 棋手 ， 江苏 苏州人 。 曾 打进 FIDE 排名 的 全世界 前 100 名 。 \ n 等级分 : 2005 年 4 月 : 2582 \ n 徐俊 ， 男 ， 博士后 ， 中华医学会 神经病 学分 会 会员 ， 美国 神经病 学 研究院 会员 ， 美国 神经科学 会 会员 。 先后 于 南京医科大学 、 中山大学 获得 神经病 学 硕士 、 博士学位 。 2003 - 2006 于 美国匹兹堡大学 从事 博士后 研究 ， 回国 后 获 国家自然科学基金 、 人事部 留学 归国 人员 启动 基金 及省 、 市 科研 基金 14 项 资助 。 主要 对 老年期 痴呆 及 相关 认知障碍 疾病 ， 以及 神经系统 免疫 疾病 进行 临床 诊治 与 发病 机制 研究 。 已 发表 论文 30 余篇 ， 其中 SCI 论文 7 篇 ， 发表 在 Blood 、 Brain Res 、 J Leuoko Cell Biol 等 核心 期刊 。 现为 南京 脑科 医院 神经内科 主任医师 ， 南京 神经 精神病学 研究所 副所长 ， 神经内科 副 主任 。 兼任 南京医科大学 副教授 、 硕士生 导师 。'
    words = [word for word in s.split(" ") if not word in stopwords]
    words2 = [word for word in s2.split(" ") if not word in stopwords]
    print len(words)
    print len(words2)
    print len(set(words))
    words = gen_word_cnt(words)
    words2 = gen_word_cnt(words2)
    
    cnt = 0
    for w in words:
        if w in words2:
            cnt += words[w] * words2[w]
    print cnt
