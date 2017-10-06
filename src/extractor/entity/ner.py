# -*- coding: utf-8 -*-

import sys
from ..ltp import LTP,LTPResult
from ... import IOUtil
import copy
import json


#放在最后，正常输出中文
import uniout

ENTITY_PATH=IOUtil.base_dir+"/src/extractor/entity"

class NamedEntityReg:

	def __init__(self,ltp_base):
		self.__ltp = LTP(ltp_base)

	def recognize(self,sentence,ltp_result,page_info,stanford_result):
		#new_ltp_result=copy.deepcopy(ltp_result)
		new_ltp_result=ltp_result
		new_ltp_result.ner_tags=list(self.__ltp.nertagger.recognize(new_ltp_result.words,new_ltp_result.tags))
		self.__optimize_entitys(new_ltp_result)
		return self.__entity_tuples(new_ltp_result.ner_tags)

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
	def __optimize_segment(self,ltp_result):
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
		result.append(en_tuples)

		#stanford 的seg和pos和ner的个数不同，比如：乔治·R·R·马丁于20世纪60年代末期，即20岁左右的大学时代，开始从事当时热火朝天的科幻故事创作。
		ner_words = [ ner[i][0] for i in range(len(ner)) ]

		#借用LTPResult的text函数
		ltp_result = LTPResult(ner_words,"","","",sentences[stf_index])
		entitys = []
		for t in en_tuples:
			entitys.append(ltp_result.text(t[0],t[1]))
		result.append(entitys)
	return result
		






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

def test_multi(ner):
	while(True):
		text=raw_input("please input text :")
		print "\n"
		if text == "exit":
			break
		
		words=ner.segment(text)
		postag=ner.postag(words)

		ltp_result = LTPResult(words,postag,"","","")
		entitys = ner.recognize(text,ltp_result,"","")
		print entitys,"\n"

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


	#	for en in stanford_result[index]:
	#		print en,"\n"
		#	fw_stf.write(en+"\t")
	#	fw_stf.write("\n\n")
		
	
	fw_ltp.close()
	fw_stf.close()


if __name__ == "__main__":
	ner = NamedEntityReg(IOUtil.base_dir+"/../LTP/ltp_data_v3.4.0")

#	test_multi(ner)

	test_write_file(ner)

	ner.release()

	