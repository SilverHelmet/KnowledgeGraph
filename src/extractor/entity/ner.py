# -*- coding: utf-8 -*-

from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
import sys
sys.path.append("..")
import ltp

class NamedEntityReg:

	def __init__(self):

		self.__ltp = LTP("lib/ltp_data_v3.4.0")

	def recognize(self,sentence,LTPResult,page_info):
		words = self.segment(sentence)
		postag = self.postag(words)
		new_words,new_postag = self.__optimize_segment(words,postag)

		raw_entitys = list(self.__recognizer.recognize(new_words,new_postag))

		new_raw_entitys = list(self.__ltp.nertagger.recognize(words,postag))
		print("原实体：",raw_entitys,"\n","新实体",new_raw_entitys,"\n")
		optimize_entitys = self.__optimize_entitys(postag,raw_entitys)
		return raw_entitys,self.__entity_tuples(optimize_entitys)

	def segment(self,sentence):
		words = self.__ltp.segmentor.segment(sentence)
		return list(words)
	
	def postag(self,words):
		return list(self.__ltp.tagger.postag(words))


	def release(self):
		self.__segmenter.release()
		self.__postagger.release()
		self.__recognizer.release()
		self.__parser.release()

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
		return new_words,new_postag
















if __name__ == "__main__":
	ner=NamedEntityReg(SEG_PATH,POS_PATH,REG_PATH,PARSER_PATH)
	while(True):
		text=input("please input text :")
		print("\n")
		if text == "exit":
			break
		print("\n")
		words=ner.segment(text)
		print (words,"\n")
		postag=ner.postag(words)
		print(postag,"\n")
		raw_entitys , entitys = ner.recognize(text,"","")
		print(raw_entitys,"\n")
		print(entitys,"\n")
		print("\n")
		print("\n")

	ner.release()
	
	