
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser

LTP_PATH="../../../../LTP/ltp_data_v3.4.0"
SEG_PATH=LTP_PATH+"/cws.model"
POS_PATH=LTP_PATH+"/pos.model"
REG_PATH=LTP_PATH+"/ner.model"
PARSER_PATH=LTP_PATH+"/parser.model" 

class NamedEntityReg:

	def __init__(self,segmenter_path,postagger_path,recognizer_path,parser_path):
		self.__segmenter=Segmentor()
		self.__segmenter.load(segmenter_path)

		self.__postagger=Postagger()
		self.__postagger.load(postagger_path)

		self.__recognizer=NamedEntityRecognizer()
		self.__recognizer.load(recognizer_path)

		self.__parser=Parser()
		self.__parser.load(parser_path)

	def recognize(self,sentence,nlp_res,page_info):
		words=self.segment(sentence)
		postag=self.postag(words)
		raw_entitys=list(self.__recognizer.recognize(words,postag))
		optimize_entitys=self.__optimize_entitys(postag,raw_entitys)
		return raw_entitys,self.__entity_tuples(optimize_entitys)

	def segment(self,sentence):
		words=self.__segmenter.segment(sentence)
		return list(words)
	
	def postag(self,words):
		return list(self.__postagger.postag(words))

	def parse(self,words,postag):
		pres=self.__parser.parse(words,postag)
		return list((item.head,item.relation) for item in pres)


	def release(self):
		self.__segmenter.release()
		self.__postagger.release()
		self.__recognizer.release()
		self.__parser.release()

	def __entity_tuples(self,entitys):
		tuples=[]
		index=0
		while index < len(entitys):
			if entitys[index] != "O":
				if entitys[index].split("-")[0] == "S":
					tuples.append((index,index+1))
				elif entitys[index].split("-")[0] == "B":
					begin=index
					while entitys[index].split("-")[0] != "E":
						index+=1
					tuples.append((begin,index+1))
			index+=1
		return tuples

	def __optimize_entitys(self,postag,raw_entitys):
		new_entitys=self.__pos_nh_to_ner_nh(postag,raw_entitys)
		return new_entitys


	"""
	将postag词性为nh的词判定为实体Nh
	"""
	def __pos_nh_to_ner_nh(self,postag,raw_entitys):
		new_entitys=raw_entitys
		pos_nh_lists=self.__find_pos_nh_lists(postag)
		for t in pos_nh_lists:
			for i in range(len(t)-1):
				new_entitys[t[i]]='I-Nh'
			if len(t)==2:
				new_entitys[t[0]]='S-Nh'
			else:
				 new_entitys[t[0]]='B-Nh'
				 new_entitys[t[len(t)-2]]='E-Nh'
		return new_entitys
		

	def __find_pos_nh_lists(self,postag):
		L=[]
		index=0
		while index <len(postag):
			t=[]
			if postag[index]=='nh':
				while index < len(postag) and postag[index]=='nh':
					t.append(index)
					index+=1
				t.append(index)				
				L.append(t)
			index+=1
		return L















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
		print(ner.parse(words,postag))
		print("\n")
		print("\n")

	ner.release()
	
	