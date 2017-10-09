# -*- coding: utf-8 -*-

import sys
from ..ltp import LTP,LTPResult
from ... import IOUtil
import copy
import json
import re
class NamedEntityReg:


	def recognize(self,sentence,ltp_result,page_info,stanford_result=None):
		self.__optimize_entitys(ltp_result)
		if stanford_result:
			self.__blend_with_stanford(ltp_result,stanford_result)
		return self.__entity_tuples(ltp_result.ner_tags)


	def __entity_tuples(self,entitys):
		tuples = []
		index = 0
		while index < len(entitys):
			if entitys[index] != "O":
				if entitys[index].split("-")[0] == "S":
					tuples.append((index,index+1))
				elif entitys[index].split("-")[0] == "B":
					begin = index
					while entitys[index].split("-")[0] != "E":
						index += 1
					tuples.append((begin,index+1))
			index += 1
		return tuples

	def __optimize_entitys(self,ltp_result):
		self.__optimize_segment(ltp_result)
		ltp_result.ner_tags = self.__pos_nh_to_ner_nh(ltp_result.tags,ltp_result.ner_tags)
		self.__reg_non_chinese_entitys(ltp_result)

	"""
	将postag词性为nh的词判定为实体Nh
	"""
	def __pos_nh_to_ner_nh(self,postag,raw_entitys):
		new_entitys = list(raw_entitys)
		pos_nh_lists = self.__find_pos_nh_lists(postag,raw_entitys)
		for t in pos_nh_lists:
			for i in range(len(t) - 1):
				new_entitys[t[i]] = "I-Nh"
			if len(t) == 2:
				new_entitys[t[0]] = "S-Nh"
			else:
				 new_entitys[t[0]] = "B-Nh"
				 new_entitys[t[len(t)-2]] = "E-Nh"
		return new_entitys
		

	def __find_pos_nh_lists(self,postag,entitys):
		L = []
		index = 0
		while index < len(postag):
			t = []
			if postag[index] == "nh" and entitys[index] == "O":
				while index < len(postag) and postag[index] == "nh"  and entitys[index] == "O":
					t.append(index)
					index += 1
				t.append(index)	
				L.append(t)
			index += 1
		return L

	"""
	对于《》中的词，做强制分词, 同时看做是nz词性,看作实体(如果本来没有识别)
	"""
	def __optimize_segment(self,ltp_result):
		self.__optimize_by_punct(ltp_result,"《","》","*","nz","S-Nb")
		
	# def __optimize_segment(self,ltp_result):
	# 	new_words = []
	# 	new_postag = []
	# 	new_entitys = []
	# 	index = 0
	# 	first = -1
	# 	while index < len(ltp_result.words):
	# 		word = ltp_result.words[index]
	# 		pos = ltp_result.tags[index]
	# 		en = ltp_result.ner_tags[index]
	# 		if word == "《":
	# 			first = index
	# 		elif word == "》" and first != -1:
	# 			last = index
	# 			word = ltp_result.text(first + 1,last)
	# 			pos = "nz"
	# 			en = "S-Nb"
	# 			while first < last - 1:
	# 				new_words.pop()
	# 				new_postag.pop()
	# 				new_entitys.pop()
	# 				last -= 1
	# 			first = -1
	# 			index -= 1
	# 		new_words.append(word)
	# 		new_postag.append(pos)
	# 		new_entitys.append(en)
	# 		index += 1
	# 	#更新
	# 	ltp_result.update(new_words,new_postag,new_entitys)

	"""
	ltp_result:
	p_left:左符号，如《
	p_right:右符号，如》
	pos_label：p_left，p_right内原词性
	pos_set:p_left，p_right内新词性
	en_set:p_left，p_right内实体类型
	"""
	def __optimize_by_punct(self,ltp_result,p_left,p_right,pos_label,pos_set,en_set):
		new_words = []
		new_postag = []
		new_entitys = []
		index = 0
		first = -1
		while index < len(ltp_result.words):
			word = ltp_result.words[index]
			pos = ltp_result.tags[index]
			en = ltp_result.ner_tags[index]
			if word == p_left:
				first = index
			elif word == p_right and first != -1:
				last = index

				is_pos_label = True

				#检查p_left，p_right内是否包含词性非pos_label类型的词
				if pos_label != "*": # "*"表示所有pos类型都替换
					ti = first + 1
					while ti < last:
						if ltp_result.tags[ti] != pos_label:
							is_pos_label = False
							break
						ti += 1

				if is_pos_label:
					word = ltp_result.text(first + 1,last)
					pos = pos_set
					en = en_set
					while first < last - 1:
						new_words.pop()
						new_postag.pop()
						new_entitys.pop()
						last -= 1
					first = -1
					index -= 1
				else:
					first = -1

			new_words.append(word)
			new_postag.append(pos)
			new_entitys.append(en)
			index += 1
		#更新
		ltp_result.update(new_words,new_postag,new_entitys)
		

	"""
	std_result是一行文本的Stanford结果，[(entitys,en_label,pos_label),...,]
	"""
	def __blend_with_stanford(self,ltp_result,std_result):
		#fw_error = open(MY_FOLDER+"/stf_ltp_error.txt","a")
		#fw_add = open(MY_FOLDER+"/stf_ltp_add.txt","a")

		new_std_result = copy.deepcopy(std_result)
		for index,res in enumerate(new_std_result):
			# if res[1] == "MISC" and (res[2] != "NT" and res[2] != "NR"):
			if res[1] == "MISC" and res[2] != "NR":
				continue
			elif res[0] not in ltp_result.words :
				#fw_error.write(ltp_result.sentence+"\n"+",".join(ltp_result.words)+"\n"+res[0]+"\n\n")			
				continue
			else:
				b = True
				for ltp_index,ltp_en in enumerate(ltp_result.words):
					if ltp_en in res[0]  and ltp_result.ner_tags[ltp_index] != "O" :
						#fw_error.write(ltp_result.sentence+"\t"+ltp_en+":"+ltp_result.ner_tags[ltp_index]+"\n"+res[0]+"\n\n")
						b = False
						break
				if b:
					ltp_result.ner_tags[ltp_result.words.index(res[0])] = "S-"+res[1]
					ltp_result.tags[ltp_result.words.index(res[0])] = "STD-"+res[2]
					#fw_add.write(ltp_result.sentence+"\t"+res[0]+"\n")
					#fw_add.write(res[0]+":"+res[1]+":"+res[2]+"\n")

		#fw_error.close()
		#fw_add.close()

	def __reg_non_chinese_entitys(self,ltp_result):
		# self.__optimize_by_punct(ltp_result,"(",")","ws","ws","S-Nf") #Nf表示外文实体
		# self.__optimize_by_punct(ltp_result,"（","）","ws","ws","S-Nf")
		self.__reg_pos_ws_entitys(ltp_result)
		return

	def __reg_entitys_non_chinese_other_name(self,ltp_result):

		return

	def __reg_pos_ws_entitys(self,ltp_result):
		index = 0
		first = -1
		while index < len(ltp_result.tags):
			if ltp_result.tags[index] == "ws":
				first = index
				while index < len(ltp_result.tags) and ltp_result.tags[index] == "ws":
					ltp_result.ner_tags[index] = "I-Nf"
					index += 1

				# Nintendo 64
				if index < len(ltp_result.tags) and ltp_result.tags[index] == "m":
					ltp_result.ner_tags[index] = "I-Nf"
					index += 1

				# Pokémon  é  d'Ossó ó
				# 无法判断：Lluís d'Ossó的 ó     能判断Real Unión 的 ó
				#乔治·R·R·马丁 不能加入·
				# if index < len(ltp_result.tags) and  is_other(ltp_result.words[index].decode("utf-8")) and self.__get_words_dist(ltp_result.sentence,ltp_result.words[index - 1],ltp_result.words[index]) == 1:
				# 	ltp_result.tags[index] = "ws"
				# 	while index < len(ltp_result.tags) and ltp_result.tags[index] == "ws":
				# 		ltp_result.ner_tags[index] = "I-Nf"
				# 		index += 1

				last = index
				if last - first == 1:
					if len(ltp_result.words[first].decode("utf-8")) >= 3:
						ltp_result.ner_tags[first] = "S-Nf"
				else:
					ltp_result.ner_tags[first] = "B-Nf"
					ltp_result.ner_tags[last - 1] = "E-Nf"
				index = last
			index += 1

	def __get_words_dist(self,sentence,wb,we):
		wb_end_index = sentence.index(wb) + len(wb) - 1
		we_begin_index = sentence.index(we,wb_end_index)
		return we_begin_index - wb_end_index
		

def is_chinese(uchar):
	"""判断一个unicode是否是汉字"""
	if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
		return True
	else:
		return False
 
def is_number(uchar):
	"""判断一个unicode是否是数字"""
	if uchar >= u'\u0030' and uchar<=u'\u0039':
		return True
	else:
		return False
 
def is_alphabet(uchar):
	"""判断一个unicode是否是英文字母"""
	if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
		return True
	else:
		return False
 
def is_other(uchar):
	"""判断是否非汉字，数字和英文字符"""
	uchar = re.sub("[\s+\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"),uchar)
	if len(uchar) == 0 or uchar == "".decode("utf-8"):
		return False
	if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
		return True
	else:
		return False






if __name__ == "__main__":
	ner = NamedEntityReg()

	