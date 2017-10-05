<<<<<<< HEAD
# -*- coding: utf-8 -*-

import sys
import uniout 
sys.path.append("..")
from ltp import LTP,LTPResult

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
		return new_words,new_postag
















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

	ner.release()

=======
# -*- coding: utf-8 -*-

import sys
import uniout 
sys.path.append("..")
from ltp import LTP,LTPResult

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
		return new_words,new_postag
















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

	ner.release()

>>>>>>> 0c2176d9f2b675b1e24930dcf733a83a8d600e52
	