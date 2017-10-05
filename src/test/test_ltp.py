#encoding:utf-8
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer
import os



s = "刘德华, 1982年7月初涉影坛，相继主演《投奔怒海》、《法外情》、《天若有情》、《暗战》、《无间道》、《盲探》等电影。"
# s = '刘德华（Andy Lau），1961年9月出生于中国香港，中国知名演员、歌手、词作人、制片人、电影人，影视歌多栖发展的代表艺人之一。'
# s = '2017年8月11日，刘德华主演的动作冒险电影《侠盗联盟》上映。'
s = '1992年，刘德华于华纳唱片（香港）发行粤语专辑《真我的风采》'
# s = "2014年，10月18日刘德华以香港残疾人奥委会副主席身分出席仁川举行的2014亚洲残疾人运动会开幕礼，为选手打气。"
# s = "乔治·雷蒙德·理查德·马丁(George Raymond Richard Martin)，欧美奇幻小说大师。"
# s = "《冰与火之歌》(A Song of Ice and Fire)是由美国作家乔治·R·R·马丁所著的严肃奇幻小说系列。"
# s = '2011年，《冰与火之歌》被美国HBO电视网改编成了电视剧《权力的游戏》。'
# s = '美国HBO电视网把《权利的游戏》改编成了《冰与火之歌》'
# s = '刘德华, 主演《天若有情》'
# s = '乔治·R·R·马丁于20世纪60年代末期，即20岁左右的大学时代，开始从事当时热火朝天的科幻故事创作。'
# s = '"乔治·马丁邀请我们参与了一场罕见的幻想盛会，将一个细腻逼真，兼具浪漫与写实的世界呈现在我们眼前。"--芝加哥太阳报'
# s = '任天堂株式会社(日文:任天堂株式会社，平假名:にんてんどうかぶしきがいしゃ)于1947年11月20日成立 。电子游戏业三巨头之一，是具有全球影响力的游戏生产商。'
# s = '天狼星在一些国家的文化中扮演重要角色，在古埃及，天狼星是少数与金字塔相关的星球之一。'
# s = '人们也常用七大王国来代指维斯特洛大陆。'
# s = '虽然开发小组对3D游戏并不熟识，但助理监督宫永真回忆时说，当时小组有一份热情，"想要创造一些新颖、从未有过的东西"。'
# s = '彼德•詹姆斯（Peter James）和尼克•索普（Nick Thorpe）在《远古谜团》（Ancient Mysteries）中写道：“继格里奥列之后，虽然坦普尔认为‘to polo’就是这颗看不见的恒星天狼星B，然而据格里奥列所说，多贡人他们自己则持不同观点。'
# s = '《塞尔达传说:时之笛》的声效亦多获赞许，IGN就将游戏中近藤浩治的作品与著名美国极简主义作曲家菲腊·格拉斯(Philip Glass)相提并论。'
# s = "刘德华（Andy Lau），1961年9月出生于中国香港，中国知名演员、歌手、词作人、制片人、电影人。	"
# s = '半径：3.5m'
# s = '2004年，刘德华先与导演张艺谋合作武侠片《远古谜团》，而后又与导演冯小刚合作《天下无贼》，在票房上获得不错的成绩。'
s = '《新媒体》，美国电影，J.J. Adler导演，Chris Stack、约翰·罗斯曼、BethAnn Bonner主演。'
# s = '经过多年时间，任天堂已成为全球最大的电玩游戏机制造商。除此之外，任天堂亦持有美国职棒大联盟的西雅图水手队股份。'
# s = '刘德华, 中国知名演员、歌手、词作人、制片人、电影人'
# s = '刘德华特别爱读《冰果》'
# s = "《冰与火之歌》是由美国作家乔治所著的小说系列。"
# s = '刘德华1990年凭专辑《可不可以》走红歌坛，演唱过《忘情水》、《中国人》、《冰雨》等歌曲。'
# s = "《芝加哥太阳报》(Chicago Sun-Times)是在美国芝加哥地区出版的日报"
# s = '美国作家乔治马丁'
# s = '星云奖获得者乔治马丁来了'
# s = '《生活大爆炸》是一出美国情景喜剧，此剧由华纳兄弟电视公司和查克·洛尔制片公司共同制作。'
# s = '2013年太平洋台风季泛指在2013年全年内的任何时间，于赤道以北及国际换日线以西的太平洋水域，以及南中国海所产生的热带气旋。'
# s = '《青花瓷》是方文山作词，周杰伦作曲并演唱的歌曲。'
# s = '《新媒体》，美国电影，J.J. Adler导演'
# s = '2017年8月4日，巴黎圣日耳曼官方宣布正式签下了巴西球星内马尔，合约5年。而巴塞罗那官方也承认，内马尔的法律顾问支付了2.22亿欧元的违约金，终止了双方的合同。'
# s = '巴萨与苏亚雷斯续约至2021年达成协议，双方将在2016年12月16日下午1点正式签约，苏神新合同违约金为2亿欧元。'
# s = '莱昂内尔·安德列斯·梅西（西班牙语：Lionel Andrés Messi），1987年6月i24日生于阿根廷圣菲省罗萨里奥，绰号“新马拉多纳”，阿根廷著名足球运动员，司职前锋、边锋和前腰，现效力于西班牙足球甲级联赛巴塞罗那足球俱乐部。'
# s = 'CBS电视网热播剧《生活大爆炸》流出一张主演西蒙·赫尔伯格和史蒂芬·霍金的片场合照，间接证实这位著名物理学家客串该剧的消息，同时，霍金客串的这一集（第五季第21集）已于美国当地时间2012年4月5日晚播出。'
s = '上海乾徽智能科技有限公司创建于1993年，是一家总部位于上海嘉定区专业从事教学仪器研发、生产、销售和服务的高新技术企业。'
segmentor = Segmentor()
base_dir = 'lib/ltp_data_v3.4.0'
segmentor_model = os.path.join(base_dir, 'cws.model')
# segmentor.load(segmentor_model)
segmentor.load_with_lexicon(segmentor_model, os.path.join(base_dir, 'dict/segmentor_dict.txt'))

words = segmentor.segment(s)
print " # ".join(words)
segmentor.release()

print ""
print ""

tagger = Postagger() 
tagger_model = os.path.join(base_dir, 'pos.model')
tagger.load_with_lexicon(tagger_model, os.path.join(base_dir, 'dict/tagger_dict.txt'))
tags = tagger.postag(words)
tags[1] = 'nz'

for word, tag in zip(words, tags):
    print "%s:%s" %(word, tag),




print ""
print ""
print ""

nertagger = NamedEntityRecognizer()
nertagger.load(os.path.join(base_dir, 'ner.model'))
ner_taggs = nertagger.recognize(words, tags)
for word, ner_tag in zip(words, ner_taggs):
    print "%s:%s" %(word, ner_tag),

print ""

parser_model = os.path.join(base_dir, 'parser.model')
parser = Parser()
parser.load(parser_model)
arcs = parser.parse(words, tags)
# print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)
words = ['root'] + list(words)
for idx, arc in enumerate(arcs, start = 1):
    head, rel = arc.head, arc.relation
    print "%s-%s:%s" %(words[idx], words[head], rel)



