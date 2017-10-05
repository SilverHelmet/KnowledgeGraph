
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser

LTP_PATH="LTP/ltp_data_v3.4.0"
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
		raw_entitys=list(self.__recognizer.recognize(words,self.postag(words)))
		return raw_entitys,self.optimize_entitys(raw_entitys)

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

	def optimize_entitys(self,raw_entitys):
		return list( (st,st+1)  for st in range(len(raw_entitys) ) if raw_entitys[st] != "O" )



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

	