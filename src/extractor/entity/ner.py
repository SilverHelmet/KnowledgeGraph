# -*- coding: utf-8 -*-

import sys
from ..ltp import LTP,LTPResult
from ... import IOUtil
import copy
import json


class NamedEntityReg:


	def recognize(self,sentence,ltp_result,page_info,stanford_result=None):
		# self.__optimize_entitys(ltp_result)
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


	"""
	将postag词性为nh的词判定为实体Nh
	"""
	def __pos_nh_to_ner_nh(self,postag,raw_entitys):
		new_entitys = list(raw_entitys)
		pos_nh_lists = self.__find_pos_nh_lists(postag)
		for t in pos_nh_lists:
			for i in range(len(t) - 1):
				new_entitys[t[i]] = "I-Nh"
			if len(t) == 2:
				new_entitys[t[0]] = "S-Nh"
			else:
				 new_entitys[t[0]] = "B-Nh"
				 new_entitys[t[len(t)-2]] = "E-Nh"
		return new_entitys
		

	def __find_pos_nh_lists(self,postag):
		L = []
		index = 0
		while index < len(postag):
			t = []
			if postag[index] == "nh":
				while index < len(postag) and postag[index] == "nh":
					t.append(index)
					index += 1
				t.append(index)	
				L.append(t)
			index += 1
		return L

	"""
	对于《》中的词，做强制分词, 同时看做是nz词性,看作实体(如果本来没有识别)
	"""
	def __optimize_segment_v2(self,ltp_result):
		index = 0
		first = -1
		while index < len(ltp_result.words):
			if ltp_result.words[index] == "《":
				first = index
			elif ltp_result.words[index] == "》" and first != -1:
				last = index
				index = first + 1
				while index < last:
					ltp_result.tags[index]="nz"
					ltp_result.ner_tags[index]="I-Nb" # Nb代表文学作品
					index += 1
				if last - first == 2:
					ltp_result.ner_tags[first+1]="S-Nb"	
				elif last - first > 2:
					ltp_result.ner_tags[first+1]="B-Nb"
					ltp_result.ner_tags[last-1]="E-Nb"
				index = first + 2
				first = -1
			index += 1

	def __optimize_segment(self,ltp_result):
		new_words = []
		new_postag = []
		new_entitys = []
		index = 0
		first = -1
		while index < len(ltp_result.words):
			word = ltp_result.words[index]
			pos = ltp_result.tags[index]
			en = ltp_result.ner_tags[index]
			if word == "《":
				first = index
			elif word == "》" and first != -1:
				last = index
				word = ltp_result.text(first + 1,last)
				pos = "nz"
				en = "S-Nb"
				while first < last - 1:
					new_words.pop()
					new_postag.pop()
					new_entitys.pop()
					last -= 1
				first = -1
				index -= 1
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
			if res[1] == "MISC" and (res[2] != "NT" and res[2] != "NR"):
			#if res[1] == "MISC" and res[2] != "NR":
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

	def _reg_non_chinese_entitys(self,ltp_result):

		return











if __name__ == "__main__":
	ner = NamedEntityReg()

	