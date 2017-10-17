# -*- coding: utf-8 -*-

from .ner import NamedEntityReg
from ... import IOUtil
# from ..test_ner import Estimator 
from ..ltp import LTP,LTPResult
import copy
import json

#放在最后，正常输出中文
import uniout

ENTITY_PATH=IOUtil.base_dir+"/src/extractor/entity"
MY_FOLDER=IOUtil.base_dir+"/../test_file"

"""
Nh 人名
Ns 地名
Ni 机构名（orhanization)
Nb 著作名，在《》里的如 生活大爆炸
Nz 其他实体（由词性nz转化来的实体）
"""

def extract_stanford_result(stf_result_jsons,sentences):
	results = []
	for stf_index in range(len(stf_result_jsons)):
		en_tuples = []
		en_pos  = []
		ner = stf_result_jsons[stf_index]["ner"]

		index = 0
		while index < len(ner):
			if ner[index][1] != "O":
				en_label = ner[index][1]
				pos_label = stf_result_jsons[stf_index]["pos"][index][1]
				first = index
				while index < len(ner) and ner[index][1] == ner[first][1]:
					index += 1
				en_tuples.append((first,index,en_label,pos_label))  #(start,end,en_label,pos_label)
				index -= 1
			index += 1

		#stanford 的seg和pos和ner的个数不同，比如：乔治·R·R·马丁于20世纪60年代末期，即20岁左右的大学时代，开始从事当时热火朝天的科幻故事创作。
		ner_words = [ ner[i][0].encode("utf-8") for i in range(len(ner)) ]

		#借用LTPResult的text函数
		ltp_result = LTPResult(ner_words,"","","",sentences[stf_index])
		entitys = []
		for t in en_tuples:
			text = ltp_result.text(t[0],t[1])
			entitys.append((text,t[2],t[3]))
		results.append(entitys)
	return results
"""		
	

def get_text(words,sentence,start,end):
	index1 = sentence.find(words[start])
	index2 = 0
	if end >= len(words):
		index2 = len(sentence)
	else:
		index2 = sentence.find(words[end],index1) + len(words[end])
	return sentence[0 : 2 ]
"""

def load_stanford_result(file_name):
	stanford_result = []
	with open(file_name,"r") as f:
		for line in f.readlines():
			stanford_result.append(json.loads(line))
	return stanford_result


def load_text(file_name):
	text_lines = []
	with open(file_name,"r") as f:
		text_lines = copy.deepcopy(f.readlines())
	return text_lines

def load_labled_entitys(file_name):
	lines_entitys = []
	with open(file_name,"r") as f:
		for line in f:
			entitys = [e for e in line.split("\t") if e.strip() != "" ]
			lines_entitys.append(entitys)
	return lines_entitys

def test_multi(ltp,ner):
	while(True):
		text=raw_input("please input text :")
		print "\n"
		if text == "exit":
			break

		ltp_result = ltp.parse(text)
		entitys = ner.recognize(text,ltp_result,"")
		print entitys,"\n"

		words = ltp_result.words
		tags = ltp_result.tags
		ner_tags = ltp_result.ner_tags

		for i in range(len(words)):
			print "%s:%s:%s " %(words[i],tags[i],ner_tags[i]),
		print "\n"
		# print words,"\n"
		# print tags,"\n"
		# print ner_tags,"\n"

def test_write_file(ltp,ner):
	stanford_result_raw = load_stanford_result(MY_FOLDER+"/lsx-lhr.line.out.txt")
	text_lines = load_text(MY_FOLDER+"/lsx-lhr.line.txt")

	fw_ltp = open(MY_FOLDER+"/ltp_result.txt","w")
	fw_ltp_raw_en = open(MY_FOLDER+"/ltp_raw_entitys.txt","w")
	fw_stf = open(MY_FOLDER+"/stf_result.txt","w")

	fw_ltp_all_res = open(MY_FOLDER+"/stf_all_result.txt","w")

	stanford_result = extract_stanford_result(stanford_result_raw,text_lines)
	for index in range(len(text_lines)):
		line = text_lines[index]
		if line == "" or line == "\n":
			break

		ltp_result = ltp.parse(line)

		entitys = ner.recognize(line,ltp_result,"",stanford_result[index])
		for en in entitys:
			fw_ltp.write( ltp_result.text(en[0],en[1])+"\t")
		fw_ltp.write("\n\n")

		for i in range(len(ltp_result.ner_tags)):
			fw_ltp_raw_en.write(ltp_result.words[i]+":"+ltp_result.ner_tags[i]+"  ")
		fw_ltp_raw_en.write("\n\n")


		for en in stanford_result[index]:
			#print en,"\n"
			fw_stf.write(en[0]+":"+en[1]+"\t")
		fw_stf.write("\n\n")
		
		for i in range(len(ltp_result.words)):
			fw_ltp_all_res.write(ltp_result.words[i]+":"+ltp_result.tags[i]+":"+ltp_result.ner_tags[i]+"\t")
		fw_ltp_all_res.write("\n\n")
	
	fw_ltp.close()
	fw_stf.close()

def write_test(ltp,ner):
	fw_ltp_all_res = open(MY_FOLDER+"/stf_non_chinese_result.txt","w")
	text_lines = load_text(MY_FOLDER+"/non-chinese-case.txt")
	for index in range(len(text_lines)):
		line = text_lines[index]
		ltp_result = ltp.parse(line)

		entitys = ner.recognize(line,ltp_result,"")
		for i in range(len(ltp_result.words)):
			fw_ltp_all_res.write(ltp_result.words[i]+":"+ltp_result.tags[i]+":"+ltp_result.ner_tags[i]+"\t")
		fw_ltp_all_res.write("\n\n")
	fw_ltp_all_res.close()

def std_ltp_out(ltp,ner):
	lines = load_text(MY_FOLDER+"/update_all.line.txt")
	std_result_raw = load_stanford_result(MY_FOLDER+"/update_all.line.out.txt")
	std_result = extract_stanford_result(std_result_raw,lines)
	lines_labled_entitys = load_labled_entitys(MY_FOLDER+"/update_all.line.marks.txt")

	fw_stf_ltp = open(MY_FOLDER+"/stf_ltp_out.txt","w")
	
	for index,line in enumerate(lines):
		ltp_result = ltp.parse(line.encode("utf-8"))
		# ner_tuples = ner.recognize(line,ltp_result,"")
		ner_tuples = ner.recognize(line,ltp_result,"",std_result[index])

		ltp_ner_entitys = []
		for en_t in ner_tuples:
			ltp_ner_entitys.append(ltp_result.text(en_t[0],en_t[1]))

		ltp_ner_str = ""
		for en in ltp_ner_entitys:
			ltp_ner_str += en + " "

		fw_stf_ltp.write(line+"\n")

		mar_ens = ""
		for m_e in lines_labled_entitys[index]:
			mar_ens += m_e + ","
		fw_stf_ltp.write(mar_ens+"\n\n")

		for i,p in enumerate(ltp_result.tags):
			fw_stf_ltp.write(ltp_result.words[i]+":"+ltp_result.tags[i]+":"+ltp_result.ner_tags[i]+" ")
		fw_stf_ltp.write("\n"+ltp_ner_str+"\n\n")

	
		for e in std_result[index]:
			fw_stf_ltp.write("%s:%s:%s\t" % (e[0],e[1],e[2]))
		fw_stf_ltp.write("\n-----------------------------------------------------------\n")

	fw_stf_ltp.close()

def test(ltp,ner):
	lines = load_text(MY_FOLDER+"/update_all.line.txt")

	std_result_raw = load_stanford_result(MY_FOLDER+"/update_all.line.out.txt")
	std_result = extract_stanford_result(std_result_raw,lines)

	lines_labled_entitys = load_labled_entitys(MY_FOLDER+"/update_all.line.marks.txt")

	fw_miss = open(MY_FOLDER+"/miss.txt","w")
	fw_miss_1 = open(MY_FOLDER+"/miss_1.txt","w")
	fw_miss_2 = open(MY_FOLDER+"/miss_2.txt","w")
	fw_miss_3 = open(MY_FOLDER+"/miss_3.txt","w")
	fw_miss_4 = open(MY_FOLDER+"/miss_4.txt","w")

	fw_reg_en = open(MY_FOLDER+"/reg_entitys.txt","w")
	fw_stf_en = open(MY_FOLDER+"/stf_en.txt","w")
	fw_nz = open(MY_FOLDER+"/nz.txt","w")
	

	for s_e in std_result:
		for e in s_e:
			fw_stf_en.write("%s:%s:%s\t" % (e[0],e[1],e[2]))
		fw_stf_en.write("\n")
	


	est = Estimator()
	for index,line in enumerate(lines):
		ltp_result = ltp.parse(line.encode("utf-8"))
		ner_tuples = ner.recognize(line,ltp_result,"",std_result[index])
		ner_entitys = []
		for en_t in ner_tuples:
			ner_entitys.append(ltp_result.text(en_t[0],en_t[1]))
		miss_type = est.add(ltp_result,lines_labled_entitys[index],ner_entitys)

		ner_str = ""
		for en in ner_entitys:
			ner_str += en + " "

		isnz = False
		for i,p in enumerate(ltp_result.tags):
			fw_reg_en.write(ltp_result.words[i]+":"+ltp_result.tags[i]+":"+ltp_result.ner_tags[i]+" ")
			if p == "nz":
				isnz=True
				fw_nz.write(ltp_result.words[i]+":"+ltp_result.tags[i]+":"+ltp_result.ner_tags[i]+" ")
		fw_reg_en.write("\n"+ner_str+"\n\n")
		if isnz :
			fw_nz.write("\n"+ltp_result.sentence+"\n")

		if len(miss_type) > 0:
			msg = []
			w_p_n = ""
			for i,p in enumerate(ltp_result.tags):
				msg.append((ltp_result.words[i],p))
				w_p_n += ltp_result.words[i]+":"+ltp_result.tags[i]+":"+ltp_result.ner_tags[i]+" "
				fw_miss.write(ltp_result.words[i]+":"+ltp_result.tags[i]+":"+ltp_result.ner_tags[i]+" ")
				

			miss_str = ""
			miss_str_2 = ""
			miss_str_3 = ""
			miss_str_4 = ""
			miss_str_1 = ""
			
			for m_en,m_t in miss_type.items():
				miss_str += m_en +":" +str(m_t) + " "
				if m_t == 1:
					miss_str_1 += m_en +":" +str(m_t) + " "
				elif m_t == 2:
					miss_str_2 += m_en +":" +str(m_t) + " "
				elif m_t == 3:
					miss_str_3 += m_en +":" +str(m_t) + " "
				else:
					miss_str_4 += m_en +":" +str(m_t) + " "
					
			fw_miss.write("\n"+ner_str+"\n"+miss_str+"\n\n")
			
			if miss_str_1 != "":
				fw_miss_1.write(w_p_n+"\n"+ner_str+"\n"+miss_str_1+"\n\n")
			if miss_str_2 != "":
				fw_miss_2.write(w_p_n+"\n"+ner_str+"\n"+miss_str_2+"\n\n")
			if miss_str_3 != "":
				fw_miss_3.write(w_p_n+"\n"+ner_str+"\n"+miss_str_3+"\n\n")
			if miss_str_4 != "":
				fw_miss_4.write(w_p_n+"\n"+ner_str+"\n"+miss_str_4+"\n\n")
			# print msg,"\n",ner_entitys,"\n",miss_type,"\n"
		

	est.estimation.print_info()
	fw_miss.close()
	fw_reg_en.close()

if __name__ == "__main__":
	ner = NamedEntityReg()
	ltp = LTP(IOUtil.base_dir+"/../LTP/ltp_data_v3.4.0_lsx",True)
	test(ltp,ner)
	# test_multi(ltp,ner)

	# std_ltp_out(ltp,ner)