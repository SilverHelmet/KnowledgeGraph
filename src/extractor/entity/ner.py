# -*- coding: utf-8 -*-
import sys
from ..ltp import LTPResult
from src import IOUtil
from src.extractor.resource import Resource
import copy
import json
import re
from ..structure import StrEntity
from src.mapping.fb_date import BaikeDatetime


class NamedEntityPostProcessor:
	re_year = re.compile(r'^\d{2,4}年$')
	def __init__(self, name_dict, process_bracket_flag, add_time_entity):
		self.dict = name_dict
		self.process_bracket_flag = process_bracket_flag
		self.add_time_entity = add_time_entity
		self.ltp = Resource.get_singleton().get_ltp()

	def decide_etype(self, str_entities, st, ed):
		etype = str_entities[st][2]
		if etype != "Ns":
			return etype
		for i in range(st + 1, ed):
			etype = str_entities[i][2]
			if etype != "Ns":
				return etype
		return "Ns"

	def merge_neighbor(self, ltp_result, str_entities):
		st = 0
		new_str_entities = []
		while st < len(str_entities):
			ed = st + 1
			while ed < len(str_entities) and str_entities[ed][0] == str_entities[ed - 1][1]:
				ed += 1
			
			etype = self.decide_etype(str_entities, st, ed)
			new_str_entities.append((str_entities[st][0], str_entities[ed-1][1], etype))
			st = ed
		return new_str_entities
				
	def get_ATT_common_father(self, is_leaf, arcs, st, ed):	
		father = arcs[st].head
		if father < ed:
			return []
		for i in range(st, father):
			if not is_leaf[i]:
				return []
			if arcs[i].head != father:
				return []
			if arcs[i].relation != "ATT":
				return []
		
		if arcs[father].relation == "ATT":
			ff = arcs[father].head
			if ff <= father + 2 and ff > father:
				valid = True
				for i in range(father+1, ff):
					if not arcs[i].relation == "ATT" or not arcs[i].head == ff:
						valid = False
				if valid:
					return [ff, father]
		return [father]

	def up_ATT_extension(self, ltp_result, str_entities):
		new_str_entities = []
		entity_pool = [False] * ltp_result.length
		is_leaf = [True] * (ltp_result.length + 1)
		for arc in ltp_result.arcs:
			head = arc.head
			is_leaf[head] = False 
		for str_entity in str_entities:
			st, ed, etype = str_entity
			if entity_pool[st]:
				continue

			ancestors = self.get_ATT_common_father(is_leaf, ltp_result.arcs, st, ed)
			extension = False
			for ancestor in ancestors:
				text = ltp_result.text(st, ancestor + 1)
				if text in self.dict:
					ed = ancestor + 1
					etype = 'Ni'
					extension = True
					break
			if not extension and etype == "Ns":
				for ancestor in ancestors:
					if ltp_result.tags[ancestor] != 'nh':
						ed = ancestor + 1
						etype = "Ns-ATT"
						# print 'Ns-ATT', ltp_result.text(st, ed), st, ed
						break
			
			for i in range(st, ed):
				entity_pool[i] = True
			new_str_entities.append((st, ed, etype))
		return new_str_entities

	def is_mq(self, ltp_result, idx):
		if idx < 0:
			return False
		if ltp_result.tags[idx] != 'm' or ltp_result.tags[idx + 1] != 'q':
			return False
		# if ltp_result.words[idx + 1] != '届':
		# 	return False
		if ltp_result.arcs[idx].relation != "ATT" or ltp_result.arcs[idx+1].relation != "ATT":
			return False
			
		return True

	def is_year(self, ltp_result, idx):
		if idx < 0:
			return False
		if ltp_result.arcs[idx].relation != "ATT":
			return False
		return NamedEntityPostProcessor.re_year.match(ltp_result.words[idx]) is not None

	def force_ATT(self, ltp_result, st, ed, tail):
		for i in range(st, ed):
			head = ltp_result.arcs[i].head
			if head < st or head > tail:
				ltp_result.arcs[i].head = tail

	def merge_by_next(self, ltp_result, e_next, str_entities):
		need_update = False
		for i in range(ltp_result.length):
			if e_next[i] != i + 1:
				need_update = True

		if not need_update:
			return str_entities

		entity_st_map = {}
		for e in str_entities:
			entity_st_map[e[0]] = e

		new_words = []
		new_tags = []
		new_ner_tags = []
		new_str_entities = []
		length = 0
		st = 0
		l = 0
		while st < ltp_result.length:
			
			ed = e_next[st]
			if ed == st + 1:
				new_words.append(ltp_result.words[st])
				new_tags.append(ltp_result.tags[st])
				new_ner_tags.append(ltp_result.ner_tags[st])
			else:
				new_words.append(ltp_result.text(st, ed))
				# new_tags.append(ltp_result.tags[ed-1])
				new_tags.append('nz')
				new_ner_tags.append("S-Nz")

			if st in entity_st_map:
				e_st, e_ed, etype = entity_st_map[st]
				if ed == st + 1:
					new_str_entities.append((l, l + e_ed - e_st, etype ))
				else:
					new_str_entities.append((l, l + 1, etype))

			l += 1
			st = ed

		ltp_result.update(new_words, new_tags, new_ner_tags)
		ltp_result.update_parsing_tree(self.ltp)
		
		return new_str_entities

		
	def down_ATT_extension(self, ltp_result, str_entities):
		entity_pool = [False] * ltp_result.length
		new_str_entities = []
		e_next = []
		for i in range(ltp_result.length):
			e_next.append(i + 1)
		for i in range(len(str_entities)-1, -1, -1):
			st, ed, etype = str_entities[i]
			if entity_pool[ed - 1]:
				continue

			
			ori_st = st
			while st > 0:
				arc = ltp_result.arcs[st-1]
				if arc.relation == 'ATT' and arc.head >= st and arc.head < ed:
					st -= 1
				else:
					break

			order = (0, -1)
			if self.is_mq(ltp_result, st - 2):
				st -= 2
				order = (st, st + 2)
			if self.is_year(ltp_result, st - 1):
				st -= 1
				order = (st, st + 1)

			extension = False
			if  st < ori_st:
				text = ltp_result.text(st, ed)
				if text in self.dict:
					extension = True
				else:
					st = ori_st

			
			if extension and order[1] != -1:
				e_next[st] = ed

			for idx in range(st, ed):
				entity_pool[idx] = True
			new_str_entities.append((st, ed, etype))

		new_str_entities.reverse()
		new_str_entities = self.merge_by_next(ltp_result, e_next, new_str_entities)
		return new_str_entities

	def process_bracket(self, ltp_result, str_entities, ltp):
		brackets = []

		left_pos = -1
		index = 0
		for index in range(ltp_result.length):
			word = ltp_result.words[index]
			if word == "(" or  word ==  "（":
				left_pos = index
			elif word == ')' or word == '）':
				if left_pos != -1:
					brackets.append((left_pos, index))
					left_pos = -1

		if len(brackets) == 0:
			return str_entities

		new_str_entities = []
		for str_entity in str_entities:
			st = str_entity.st
			ed = str_entity.ed
			left_bracket_cnt = 0
			right_bracket_cnt = 0
			for i in range(st, ed):
				if ltp_result.words[i] in ['(', '（']:
					left_bracket_cnt += 1
				if ltp_result.words[i] in [')', '）']:
					right_bracket_cnt += 1
			if left_bracket_cnt != right_bracket_cnt:
				continue
			new_str_entities.append(str_entity)
		str_entities = new_str_entities

		word_pos2entity_pos = [-1] * ltp_result.length
		for idx, str_entity in enumerate(str_entities):
			st = str_entity.st
			ed = str_entity.ed
			for i in range(st, ed):
				word_pos2entity_pos[i] = idx

		in_bracket = [False] * ltp_result.length
		for left, right in brackets:
			left_entity_pos = -1
			if left - 1 >= 0:
				left_entity_pos = word_pos2entity_pos[left - 1]
			if ltp_result.tags[left-1] == 'wp'and left -2 >= 0:
				left_entity_pos = word_pos2entity_pos[left - 2]

			right_entity_pos = -1
			if right + 1 < ltp_result.length:
				right_entity_pos = word_pos2entity_pos[right + 1]

			if left_entity_pos != -1 and (right_entity_pos == left_entity_pos or right + 1 == ltp_result.length):
				continue
			entity_pos_set = set()
			for i in range(left, right + 1):
				in_bracket[i] = True
				if word_pos2entity_pos[i] != -1:
					entity_pos_set.add(word_pos2entity_pos[i])
			
			if left_entity_pos != -1:
				left_entity = str_entities[left_entity_pos]
				if left_entity_pos != right_entity_pos:
					for e_pos in entity_pos_set:
						bracket_entity = str_entities[e_pos]
						left_entity.add_name(ltp_result.text(bracket_entity.st, bracket_entity.ed))

		
		new_words = []
		new_postags = []
		new_ner_tags = []
		new_str_entities = []
		now_e_idx = 0
		bias = 0

		for i in range(ltp_result.length):
			if not in_bracket[i]:
				new_words.append(ltp_result.words[i])
				new_postags.append(ltp_result.tags[i])
				new_ner_tags.append(ltp_result.ner_tags[i])

				entity_pos = word_pos2entity_pos[i]
				if entity_pos != -1 and str_entities[entity_pos].st == i:
					entity = str_entities[entity_pos]
					entity.st -= bias
					# entity.ed -= bias
					new_str_entities.append(entity)
				if entity_pos != -1 and str_entities[entity_pos].ed - 1 == i:
					entity = str_entities[entity_pos]
					entity.ed -= bias

			else:
				bias += 1

		
		ltp_result.update(new_words, new_postags, new_ner_tags)
		ltp_result.update_parsing_tree(ltp)

		return new_str_entities

	def parse_time_entity(self, ltp_result, str_entities):
		entity_pool = [False] * ltp_result.length
		for e in str_entities:
			st = e.st
			ed = e.ed
			for i in range(st, ed):
				entity_pool[i] = True

		st = 0
		time_entities = []
		while st < ltp_result.length:
			if ltp_result.tags[st] == 'nt':
				tokens = []
				ed = st
				while ed < ltp_result.length:
					if ltp_result.tags[ed] == 'nt':
						tokens.append(ltp_result.words[ed])
						ed += 1
					elif ltp_result.tags[ed] == 'wp' and ltp_result.words[ed] in [',', '，']:
						ed += 1
					else:
						break
				if ltp_result.tags[ed-1] == 'wp':
					ed -= 1
				text = "".join(tokens)
				baike_time = BaikeDatetime.parse(text, strict = True, search_mod = True)
				valid = baike_time is not None
				for i in range(st, ed):
					if entity_pool[i]:
						valid = False
				if valid:
					entity = StrEntity(st, ed, 'Nt')
					entity.add_time_obj(baike_time)
					time_entities.append(entity)
				st = ed
			st += 1
		return time_entities

	def add_abbrev(self, ltp_result, str_entities):
		entity_pool = [False] * ltp_result.length
		for st, ed, etype in str_entities:
			for i in range(st, ed):
				entity_pool[i] = True
		
		add_flag = False
		for i in range(ltp_result.length):
			if not entity_pool[i] and ltp_result.tags[i] == 'j' and ltp_result.words[i] in self.dict:
				# print 'add j', ltp_result.words[i]
				str_entities.append((i, i + 1, 'Nz'))
				ltp_result.ner_tags[i] = 'nz'
				add_flag = True

		if add_flag:
			str_entities.sort(key = lambda x: x[0])

		return str_entities

	def process(self, ltp_result, str_entities, ltp):
		str_entities = self.add_abbrev(ltp_result, str_entities)
		str_entities = self.merge_neighbor(ltp_result, str_entities)
		str_entities = self.up_ATT_extension(ltp_result, str_entities)
		str_entities = self.down_ATT_extension(ltp_result, str_entities)
		

		str_entities = [StrEntity(st, ed, etype) for st, ed, etype in str_entities]
		if self.process_bracket_flag:
			str_entities = self.process_bracket(ltp_result, str_entities, ltp)

		

		if self.add_time_entity:
			str_entities.extend(self.parse_time_entity(ltp_result, str_entities))

		str_entities.sort(key = lambda x:x.st)
		return str_entities


stf_ltp_en_dist = {"PERSON":"Nh" , "LOCATION":"Ns" , "ORGANIZATION":"Ni" ,"MISC":"Nm" 
,"GPE":"Ns" ,"DEMONYM":"Nh","FACILITY":"Ns"}


class NamedEntityReg:
	re_eng = re.compile(r"^[a-zA-Z.]+$")

	def __init__(self, name_dict = None, process_bracket_flag = True, add_time_entity = True):
		resource = Resource.get_singleton()
		if name_dict is None:
			name_dict = resource.get_vertical_domain_baike_dict()
		self.ltp = resource.get_ltp()
		self.post_processor = NamedEntityPostProcessor(name_dict, process_bracket_flag, add_time_entity)

		

	def recognize(self,sentence,ltp_result,page_info,stanford_result=None):
		self.__optimize_entitys(ltp_result)
		if stanford_result:
			self.__blend_with_stanford(ltp_result,stanford_result)

		self.__combine(ltp_result)
		str_entities = self.__entity_tuples(ltp_result.ner_tags)

		ltp_result.update_parsing_tree(self.ltp)
		if len(ltp_result.arcs) == 0:
			return []
		str_entities = self.post_processor.process(ltp_result, str_entities, self.ltp)
		if len(ltp_result.arcs) == 0:
			return []
		return str_entities


	def __entity_tuples(self,entitys):
		tuples = []
		index = 0
		while index < len(entitys):
			if entitys[index] != "O":
				if entitys[index].split("-")[0] == "S":
					tuples.append((index,index+1,entitys[index].split("-")[1]))
				elif entitys[index].split("-")[0] == "B":
					begin = index
					while index + 1 < len(entitys) and entitys[index].split("-")[0] != "E":
						index += 1
					tuples.append((begin,index+1,entitys[begin].split("-")[1]))
					
			index += 1
		return tuples

	def __combine(self,ltp_result):
		new_words = []
		new_postag = []
		new_entitys = []
		entitys = ltp_result.ner_tags
		first = -1
		index = 0
		while index < len(entitys):
			word = ltp_result.words[index]
			pos = ltp_result.tags[index]
			en = ltp_result.ner_tags[index]
			b = True
			if entitys[index] != "O":
				
				if entitys[index].split("-")[0] == "B":
					first = index
				elif entitys[index].split("-")[0] == "E" and first != -1:
					# add by lihaoran, don't combine Ns and Ni
					e_type = entitys[index].split('-')[1]
					if e_type != 'Ns' and e_type != 'Ni':		
						last = index + 1
						word = ltp_result.text(first,last)
						pos = ltp_result.tags[first]
						
						en = "S-" + entitys[first].split("-")[1]
						while first < last - 1:
							if pos != ltp_result.tags[last - 1]:
								b = False
							new_words.pop()
							new_postag.pop()
							new_entitys.pop()
							last -= 1
						first = -1

			new_words.append(word)
			# modifies by lihaoran, use postag nh for person
			if b or en == 'S-Nh':
				new_postag.append(pos)
			else:
				new_postag.append("nz")				
			new_entitys.append(en)
			index += 1
		#更新
		ltp_result.update(new_words,new_postag,new_entitys)
				

	def __optimize_entitys(self,ltp_result):
		self.__optimize_segment(ltp_result)
		self.__reg_non_chinese_entitys(ltp_result)
		ltp_result.ner_tags = self.__pos_nh_to_ner_nh(ltp_result.tags,ltp_result.ner_tags)
		self.__pos_nz_to_ner(ltp_result)

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

	def __pos_nz_to_ner(self, ltp_result):
		for index , pos in enumerate(ltp_result.tags):
			if pos == "nz" and ltp_result.ner_tags[index] == "O":
				ltp_result.ner_tags[index] = "S-Nz"
		pass


	"""
	对于《》中的词，做强制分词, 同时看做是nz词性,看作实体(如果本来没有识别)
	"""	
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
		new_std_result = copy.deepcopy(std_result)
		for index,res in enumerate(new_std_result):
			if res[1] == "MISC" and res[2] != "NR" and res[2] != "NN":
				continue
			else:
				b = False
				for li,lw in enumerate(ltp_result.words):
					if res[0] == lw and ltp_result.ner_tags[li] == "O":
						ltp_result.ner_tags[li] = "S-"+stf_ltp_en_dist[res[1]]
						b = True
				


	def __reg_non_chinese_entitys(self,ltp_result):
		self.__reg_pos_ws_entitys(ltp_result)
		return

	def __reg_entitys_non_chinese_other_name(self,ltp_result):

		return

	# check whether can make [first, last) as a new entity 
	def valid_new_entity(self, ltp_result, st, ed):
		cnts = {"B": 0, "E": 0, "I": 0}
		for i in range(st, ed):
			tag = ltp_result.ner_tags[i][0]
			if tag in cnts:
				cnts[tag] += 1
		if cnts["B"] != cnts["E"]:
			return False
		if cnts['I'] > 0 and cnts['B'] == 0:
			return False
		return True



	def __reg_pos_ws_entitys(self,ltp_result):
		index = 0
		first = -1
		while index < len(ltp_result.tags):
			if ltp_result.tags[index] == "ws":
				first = index
				while index < len(ltp_result.tags) and (ltp_result.tags[index] == "ws" or self.re_eng.match(ltp_result.words[index])):
					# ltp_result.ner_tags[index] = "I-Nf"
					index += 1

				# Nintendo 64
				if index < len(ltp_result.tags) and ltp_result.tags[index] == "m":
					# ltp_result.ner_tags[index] = "I-Nf"
					index += 1

				if index < len(ltp_result.tags) and  (ltp_result.words[index] in ["'", '.', ':', '&']):
					ltp_result.tags[index] = "ws"
					while index < len(ltp_result.tags) and (ltp_result.tags[index] == "ws" or self.re_eng.match(ltp_result.words[index])):
						# ltp_result.ner_tags[index] = "I-Nf"
						index += 1

				last = index

				# add by lihaoran
				if self.valid_new_entity(ltp_result, first, last):
					for i in range(first, last):
						ltp_result.ner_tags[i] == "I-Nf"
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
		return we_begin_indaex - wb_end_index

	# def __combine_single_big_dot(self,ltp_result):
	# 	for index , word in enumerate(ltp_result.words):
	# 		if word == "•" and (ltp_result.ner_tags[index] == "E-Nh" or ltp_result.ner_tags[index] == "O"):
	# 			if index == 0 or index == len(ltp_result.words) - 1:
	# 				continue
	# 			elif ltp_result.ner_tags[index - 1] != "O" and ltp_result.ner_tags[index +1] != "O" \
	# 			and ltp_result.ner_tags[index - 1].split("-")[1] == "Nh" and ltp_result.ner_tags[index + 1].split("-")[1] == "Nh":
	# 				ltp_result.ner_tags[index] = "I-Nh"

	# 				if ltp_result.ner_tags[index - 1].split("-")[0] == "S":
	# 					ltp_result.ner_tags[index - 1] = "B-Nh"
	# 				else:
	# 					ltp_result.ner_tags[index - 1] = "I-Nh"
					
	# 				if ltp_result.ner_tags[index + 1].split("-")[0] == "S":
	# 					ltp_result.ner_tags[index + 1] = "E-Nh"
	# 				else:
	# 					ltp_result.ner_tags[index + 1] = "I-Nh"

	# def __combine_attach_big_dot(self,ltp_result):
	# 	index = ltp_result.words.index("•")
	# 	# while index 

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
	ner = NamedEntityReg(LTP(None))

	