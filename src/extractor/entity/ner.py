# -*- coding: utf-8 -*-

import sys
<<<<<<< HEAD
from ..ltp import LTP,LTPResult
from ... import IOUtil
import copy
import json

import chardet
#放在最后，正常输出中文
import uniout

ENTITY_PATH=IOUtil.base_dir+"/src/extractor/entity"
=======
import uniout 
sys.path.append("..")
from ltp import LTP,LTPResult
>>>>>>> f7d9bbef2a64be02ab09551f150d06b383afe1c2

class NamedEntityReg:

	def __init__(self,ltp_base):
		self.__ltp = LTP(ltp_base)

	def recognize(self,sentence,ltp_result,page_info):
		words = ltp_result.words
		postag = ltp_result.tags
		new_words,new_postag = self.__optimize_segment(words,postag)
		raw_entitys = list(self.__ltp.nertagger.recognize(new_words,new_postag))
		optimize_entitys = self.__optimize_entitys(new_postag,raw_entitys)
		return self.__entity_tuples(optimize_entitys)

	def segment(self,sentence):
		words = self.__ltp.segmentor.segment(sentence)
		return list(words)
	
	def postag(self,words):
		return list(self.__ltp.tagger.postag(words))


	def release(self):
		return ""

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

	def __optimize_entitys(self,postag,raw_entitys):
		new_entitys = self.__pos_nh_to_ner_nh(postag,raw_entitys)
		return new_entitys


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
	对于《》中的词，做强制分词, 同时看做是nz词性(如果本来没有识别)
	返回新的分词、新词性列表
	"""
	def __optimize_segment(self,words,postag):
		new_words = list(words)
		new_postag = list(postag)
		index = 0
		first = -1
		while index < len(new_words):
			if new_words[index] == "《":
				first = index
			elif new_words[index] == "》" and first != -1 and index - first > 2:
				last = index
				work_name = ""
				index = first + 1
				while index < last:
					work_name += new_words[index]
					new_words.pop(index)
					new_postag.pop(index)
					last -= 1
				new_words.insert(first + 1,work_name)
				new_postag.insert(first + 1,"nz")
				index = first + 2
				first = -1
			index += 1
<<<<<<< HEAD


def extract_stanford_result(stanford_result,sentences):
	result = []
	for stf_index in range(len(stanford_result)):
		en_tuples = []
		ner = stanford_result[stf_index]["ner"]
		index = 0
		while index < len(ner):
			if ner[index][1] != "O":
				first = index
				while index < len(ner) and ner[index][1] == ner[first][1]:
					index += 1
				en_tuples.append((first,index))
				index -= 1
			index += 1

		#stanford 的seg和pos和ner的个数不同，比如：乔治·R·R·马丁于20世纪60年代末期，即20岁左右的大学时代，开始从事当时热火朝天的科幻故事创作。
		ner_words = [ ner[i][0] for i in range(len(ner)) ]

		#借用LTPResult的text函数
		#ltp_result = LTPResult(ner_words,"","","",sentences[stf_index])
		entitys = []
		for t in en_tuples:
			entitys.append(get_text(ner_words,sentences[stf_index],t[0],t[1]))	
			
		result.append(entitys)
	return result
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
=======
		return new_words,new_postag





>>>>>>> f7d9bbef2a64be02ab09551f150d06b383afe1c2



if __name__ == "__main__":
	ner=NamedEntityReg("../../../../LTP/ltp_data_v3.4.0")
	while(True):
		text=raw_input("please input text :")
		print "\n"
		if text == "exit":
			break
		
		words=ner.segment(text)
		postag=ner.postag(words)

		ltp_resoult = LTPResult(words,postag,"","","")
		entitys = ner.recognize(text,ltp_resoult,"")
		print entitys,"\n"

<<<<<<< HEAD
		words=ltp_result.words
		tags=ltp_result.tags
		ner_tags=ltp_result.ner_tags

		print words,"\n"
		print tags,"\n"
		print ner_tags,"\n"

def test_write_file(ner):
	stanford_result_raw = load_stanford_result(ENTITY_PATH+"/lsx-lhr.line.out.txt")
	text_lines = load_text(ENTITY_PATH+"/lsx-lhr.line.txt")

	fw_ltp = open(ENTITY_PATH+"/ltp_result.txt","w")
	fw_ltp_raw_en = open(ENTITY_PATH+"/ltp_raw_entitys.txt","w")
	fw_stf = open(ENTITY_PATH+"/stf_result.txt","w")

	stanford_result = extract_stanford_result(stanford_result_raw,text_lines)
	for index in range(len(text_lines)):
		if text_lines[index] == "" or text_lines[index] == "\n":
			break
		words = ner.segment(text_lines[index])
		postag = ner.postag(words)

		ltp_result = LTPResult(words,postag,"","",text_lines[index])
		entitys = ner.recognize(text_lines[index],ltp_result,stanford_result[index],"")
		for en in entitys:
			fw_ltp.write( ltp_result.text(en[0],en[1])+"\t")
			
		fw_ltp.write("\n\n")

		for i in range(len(ltp_result.ner_tags)):
			fw_ltp_raw_en.write(words[i]+":"+ltp_result.ner_tags[i]+"  ")
		fw_ltp_raw_en.write("\n\n")


		for en in stanford_result[index]:
			#print en,"\n"
			fw_stf.write(en+"\t")
		fw_stf.write("\n\n")
		
	
	fw_ltp.close()
	fw_stf.close()


if __name__ == "__main__":
	ner = NamedEntityReg(IOUtil.base_dir+"/../LTP/ltp_data_v3.4.0")

#	test_multi(ner)

	test_write_file(ner)

=======
>>>>>>> f7d9bbef2a64be02ab09551f150d06b383afe1c2
	ner.release()

	