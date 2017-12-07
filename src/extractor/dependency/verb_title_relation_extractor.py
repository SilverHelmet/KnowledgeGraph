#encoding: utf-8
from tree import ParseTree, Debug, PrintInfo
from ..ltp import LTP
from ..structure import StrEntity
from src.extractor.entity.ner import NamedEntityReg
from src.extractor.docprocessor import DocProcessor, ParagraphInfo
class VerbRelationExtractor:
    def __init__(self, debug_flag = False):
        self.debuger = Debug(debug_flag)
        self.nationality_dic = []
        self.profession_dic = []
        #name = ["nationality.txt", "full_profession.txt", "province.txt", "langauge.txt", "citytown.txt"]
        with open("result/rel_extraction/dict/nationality.txt", "r") as f:
            self.nationality_dic = f.readlines()
        for i in range(len(self.nationality_dic)):
            self.nationality_dic[i] = self.nationality_dic[i].replace("\n","")
        with open("result/rel_extraction/dict/full_profession.txt", "r") as f:
            self.profession_dic = f.readlines()
        for i in range(len(self.profession_dic)):
            self.profession_dic[i] = self.profession_dic[i].replace("\n","")
        self.nationality_dic = set(self.nationality_dic)
        self.profession_dic = set(self.profession_dic)
      
    def find_path_to_root(self, node):
        path = [node]
        while node.father != None:
            node = node.father
            path.append(node)
        return path
    
    def find_COO_path(self, node):
        path = [node]
        while node.father != None and node.rel == 'COO':
            path.append(node.father)
            node = node.father
        return path

    def find_coo_father(self, nodes):
        coo_father = []
        process_father = []
        index_father = []
        final_res = []
        res = []
        for i in range(len(nodes)):
            coo_father.append(self.find_path_to_root(nodes[i]))
        for i in range(len(nodes)):
            process_father.append([])
            for j in range(len(coo_father[i])):
                process_father[i].append(coo_father[i][j].idx)  
        for i in range(len(nodes)):
            index_father += process_father[i]
        father = set(index_father)
        for num in father:
            if(index_father.count(num) == len(nodes)):
                final_res.append(num)
        for i in final_res:
            res.append(process_father[0].index(i))
        return process_father[0][min(res)]
    
    def find_entity_path(self, ltp_result, e1, e2, entity_pool):
        tree = ParseTree(ltp_result)
        node_list_1 = tree.nodes[e1.st : e1.ed]
        node_list_2 = tree.nodes[e2.st : e2.ed]
        w1 = self.find_coo_father(node_list_1)
        w2 = self.find_coo_father(node_list_2)
        p1 = self.find_path_to_root(tree.nodes[w1])
        p2 = self.find_path_to_root(tree.nodes[w2])
        return p1, p2
    
    def judge_coo(self, verb1, verb2):
        path1 = self.find_COO_path(verb1)
        path2 = self.find_COO_path(verb2)
        if verb2 in path1 or verb1 in path2:
            return True
        return False
    
    def judge_if_special(self, node):
        if node.word in ['例如','比如','包括','如','像']:
            return True
        else:
            return False 

    def judge_one_SBV(self, near_verb1, near_verb2):
        if near_verb1.rel == 'SBV' and near_verb2.rel != 'SBV':
            if self.judge_if_special(near_verb2.father) == False:
                return near_verb2.father
            elif self.judge_if_special(near_verb2.father) == True:
                return near_verb1.father
        elif near_verb2.rel == 'SBV' and near_verb1.rel != 'SBV': 
            if self.judge_if_special(near_verb1.father) == False:
                return near_verb1.father
            elif self.judge_if_special(near_verb1.father) == True:
                return near_verb2.father

    def judge_one_VOB(self, verb1, verb2):
        if verb1.rel == 'VOB' and verb1.father == verb2:
            return True
        if verb2.rel == 'VOB' and verb2.father == verb1:
            return True
        return False

    def find_nearest_verb(self, path):
        res = []
        if len(path) == 1:
            return [None, None]
        for node in path:
            if node.father == None:
                return [None, None]
            elif node.father.postag == 'v':
                res.append(node)
                res.append(node.father)
                break
        return res

    def find_2_verbs(self, tree, e):
        node_list = tree.nodes[e.st : e.ed]
        w = self. find_coo_father(node_list)
        p = self.find_path_to_root(tree.nodes[w])
        near_verb = self.find_nearest_verb(p)[0]      
        verb = self.find_nearest_verb(p)[1]
        return tree.nodes[w], near_verb, verb

    def judge_entity_relation(self, near_verb, verb):
        if verb == None and near_verb == None:
            return None
        else:
            if near_verb.rel == 'SBV':
                return 'sub'
            elif near_verb.rel in ['VOB', 'FOB']:
                return 'obj'
            elif near_verb.rel in ['ADV', 'ATT', 'CMP']:
                return 'dec'
            return None

    def deal_with_isA(self, verb, rel, father, string):
        if verb == None or rel != 'SBV':
            return
        path = self.find_COO_path(verb)
        for verbs in path:
            if verbs.word == '是':
                for child in verbs.children:
                    if child.rel in ['FOB', 'VOB'] and child.mark == None:
                        child.mark = string

    def find_by_ATT_rule(self, verb, rel, father):
        if verb == None:
            return
        if rel in ['FOB', 'VOB']:
            return None
        path = self.find_path_to_root(verb)
        for verbs in path:
            if verbs.rel not in {'ATT', 'COO'}:
                return None
            else:
                if verbs.father == father:
                    return verb
                elif verbs.father.mark in ['first_entity', 'second_entity']:
                    return verb
        return None

    def find_relation(self, ltp_result, e1, e2, entity_pool):
        advanced_res = []
        tree = ParseTree(ltp_result)
        father1, near_verb1, verb1 = self.find_2_verbs(tree, e1)
        father2, near_verb2, verb2 = self.find_2_verbs(tree, e2)
        noun_res = self.find_noun_relation(father1, father2, tree)
        if noun_res != None:
            self.debuger.debug("find \"noun\"reslation")
            advanced_res.append((noun_res.idx, noun_res.idx + 1))
            return advanced_res
        rel1 = self.judge_entity_relation(near_verb1, verb1)
        rel2 = self.judge_entity_relation(near_verb2, verb2)
        if rel1 == None or rel2 == None:
            self.debuger.debug("can't find nearest verb!")
        elif rel1 == rel2:
            self.debuger.debug("the relation to verb is same! not found!")
        elif verb1 == verb2:
            self.debuger.debug("same verb found!")
            advanced_res.append((verb1.idx, verb1.idx + 1))
            return advanced_res
        else:
            if_coo = self.judge_coo(verb1, verb2)
            if_one_VOB = self.judge_one_VOB(verb1, verb2)
            if if_coo or if_one_VOB :
                one_SBV = self.judge_one_SBV(near_verb1, near_verb2)
                if one_SBV != None:
                    self.debuger.debug("coo verbs and one SBV found!")
                    advanced_res.append((one_SBV.idx, one_SBV.idx + 1))
                    return advanced_res
                self.debuger.debug("coo verbs but not one SBV! not found!")
        if near_verb1 != None:
            self.deal_with_isA(verb1, near_verb1.rel, father1, 'first_entity')
        if near_verb2 != None:
            self.deal_with_isA(verb2, near_verb2.rel, father2, 'second_entity')
        ATT_rule_res1 = ATT_rule_res2 = None
        if near_verb1 != None:
            ATT_rule_res1 = self.find_by_ATT_rule(verb1, near_verb1.rel, father2)
        if near_verb2 != None:
            ATT_rule_res2 = self.find_by_ATT_rule(verb2, near_verb2.rel, father1)
        if ATT_rule_res1 != None:
            self.debuger.debug("first eneity: find by ATT rule!")
            advanced_res.append((ATT_rule_res1.idx,ATT_rule_res1.idx + 1))
        elif ATT_rule_res2 != None:
            self.debuger.debug("second eneity: find by ATT rule!")
            advanced_res.append((ATT_rule_res2.idx,ATT_rule_res2.idx + 1))
        for res in advanced_res:
            if entity_pool[res[0]] == True:
                self.debuger.debug('found verb', ltp_result.words[res[0]] ,'is an entity! error!')
        return advanced_res

    def find_noun_relation(self, e1, e2, tree):
        if e1.depth - e2.depth == 2:
            flag = 0
            if e1.rel == 'ATT' and e1.father.rel == 'ATT' and e1.father.father == e2:
                if tree.nodes[e1.father.idx - 1].word == '的':
                    flag = 1
                for child in e1.children:
                    if child.rel == 'RAD' and child.word == '的':
                        flag = 1
            if flag == 1:
                self.debuger.debug("-"*20)
                self.debuger.debug("find noun relation!")
                self.debuger.debug(e1.word, e1.father.word, e2.word)
                self.debuger.debug("-"*20)
                return e1.father
        elif e2.depth - e1.depth == 2:
            flag = 0
            if e2.rel == 'ATT' and e2.father.rel == 'ATT' and e2.father.father == e1:
                if tree.nodes[e2.father.idx - 1].word == '的':
                    flag = 1
                for child in e2.children:
                    if child.rel == 'RAD' and child.word == '的':
                        flag = 1
            if flag == 1:
                self.debuger.debug("-"*20)
                self.debuger.debug("find noun relation!")
                self.debuger.debug(e2.word, e2.father.word, e1.word)
                self.debuger.debug("-"*20)
                return e2.father
        return None

    def find_ATT_or_COO_path(self, node):
        res = []
        path = self.find_path_to_root(node)
        for node in path:
            if node.rel in ['ATT', 'COO']:
                res.append(node.father)
            else:
                break
        return res

    def find_ATT_path(self, node):
        res = []
        path = self.find_path_to_root(node)
        for node in path:
            if node.rel == 'ATT':
                res.append(node.father)
            else:
                break
        return res

    def find_all_COO_father(self, node):
        res = []
        path = self.find_path_to_root(node)
        for node in path:
            if node.rel == 'COO':
                res.append(node.father)
            else:
                break
        return res

    def find_all_COO_child(self, node):
        res = []
        for child in node.children:
            if child.rel == 'COO':
                res.append(child)
                res += self.find_all_COO_child(child)
        return res

    def find_all_ATT_child(self, node):
        res = []
        for child in node.children:
            if child.rel == 'ATT':
                res.append(child)
                res += self.find_all_ATT_child(child)
        return res

    def find_all_COO(self, node, postag = None):
        res = self.find_all_COO_father(node) + self.find_all_COO_child(node)
        final_res = []
        if postag == None:
            final_res = res
        if postag != None:
            for node in res:
                if node.postag in postag:
                    final_res.append(node)
        return final_res

    def judge_all_ATT(self, path):
        for node in path:
            if node.rel != 'ATT':
                return False
        return True

    def find_direct_rel(self, node, rel, postag = None, if_use_entity = None, if_use_title = None):
        res = []
        for child in node.children:
            if child.rel in rel:
                if (if_use_entity == True and child.entity == None)\
                or (if_use_entity == False and child.entity != None):
                    continue
                if (if_use_title == True and child.title == None)\
                or (if_use_title == False and child.title != None):
                    continue
                if postag != None and child.postag not in postag:
                    continue
                res.append(child)
        return res

    def get_environment_rule_1(self, verb_lis):
        for verb in verb_lis:
            for child in verb.children:
                 if child.postag == 'n' and child.rel == 'VOB' and child.entity == None:
                    verb.environment.append(child)
                    self.debuger.debug("environment of verb", verb.word, child.word, "found!")

    def find_all_TARGET(self, verb_lis, entity_lis):
        for verb in verb_lis:
            if verb.rel != 'ATT':
                continue
            path = [verb.father]
            path += self.find_ATT_or_COO_path(verb.father)
            for node in path:
                if node.title != None:
                    continue
                if (node.entity != None) or (len(node.mark) != 0 and node.postag == 'n'):
                    verb.target.append(node)

    def find_all_ATT(self, entity_lis):
        for entity in entity_lis:
            if entity.title != None:
                continue
            path = self.find_path_to_root(entity)
            for node in path[:-1]:
                if node.father.postag == 'v':
                    if node.rel in ['ATT', 'ADV', 'CMP']:
                        if entity not in node.father.att:
                            node.father.att.append(entity)
                    break

    def find_normal_verb_OBJ(self, verb, entity_lis):
        res = []
        for child in verb.children:
            if child.postag != 'v':
                if child in entity_lis and child.title == None:
                    res.append(child)
                res += self.find_normal_verb_OBJ(child, entity_lis)
        return res

    def find_verb_OBJ(self, verb, entity_lis):
        if verb.search_obj_mark == True:
            self.debuger.debug("the object of verb", verb.word ,"has been found!")
            return verb.obj
        obj_res = []
        if_special_obj = False
        path = self.find_all_COO(verb)
        for node in path:
            if node.entity != None:
                obj_res.append(node)
        for child in verb.children:
            if child.postag == 'v' and child.rel in ['VOB', 'FOB']:
                if_special_obj = True
                direct_entity_sub = []
                for verb_child in child.children:
                    if verb_child.rel == 'SBV' and verb_child.entity != None and verb_child.title == None:
                        direct_entity_sub.append(verb_child)
                        verb.environment += self.find_direct_rel(child, ['VOB'], ['n', 'nd', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz'], False)
                        #self.debuger.debug("environment of verb", verb.word, verb.environment.word, "found")
                #direct_entity_sub = self.find_direct_rel(child, ['SBV'], None, True, False)
                if len(direct_entity_sub) != 0:
                    obj_res += direct_entity_sub
                else:
                    obj_res += self.find_verb_OBJ(child, entity_lis)
        if if_special_obj == False:
            self.debuger.debug("the object of verb", verb.word, "has normal object")
            for child in verb.children:
                if child.rel in ['VOB', 'FOB']:
                    if child in entity_lis and child.title == None:
                        obj_res.append(child)
                    obj_res += self.find_normal_verb_OBJ(child, entity_lis)
        verb.search_obj_mark = True
        verb.obj = obj_res
        return obj_res

    def find_actualsub_by_ATT(self, verb, entity_lis, ltp_result, old_concept_res, actual_res):
        self.debuger.debug("verb", verb.word, "start finding sub by att!")
        for node in  old_concept_res:
            self.debuger.debug("verb", verb.word, "concept word:", node.word)
        concept_res = old_concept_res
        for concept_sub in old_concept_res:
            res =[]
            for entity in entity_lis:
                self.debuger.debug("for entity:", entity.word)
                if entity.depth > concept_sub.depth:
                    path = self.find_ATT_path(entity)
                    if concept_sub in path:
                        res.append(entity)                 
                '''
                path1, path2 = tree.find_path(concept_sub.idx, entity.idx)
                self.debuger.debug("entity:", entity.word,"concept_sub",concept_sub.word)
                for node in path1:
                    self.debuger.debug("path1:", node.word)
                self.debuger.debug("path2:")
                for node in path2:
                    self.debuger.debug(node.word, node.rel)
                if len(path1) == 1 and self.judge_all_ATT(path2[:-1]) == True:
                    res.append(entity)
                    res_depth.append(entity.depth)
                    self.debuger.debug("entity:", entity.word,"verb",verb.word,"ATT find!")
                else:
                    self.debuger.debug("entity:", entity.word,"verb",verb.word,"ATT not find!")
                '''
            final_res = None
            min_depth = 100
            for item in res:
                if item.depth < min_depth:
                    min_depth = item.depth
                    final_res = item
            if final_res != None: 
                if final_res.entity != None:
                    self.debuger.debug("final_res is:", self.deal_with_print(final_res.entity, ltp_result))
                    concept_res.remove(concept_sub)
                    tmp_res = [final_res]
                    tmp_res += self.find_all_COO(final_res)
                    for coo_final in tmp_res:
                        if coo_final.entity != None and coo_final not in actual_res:
                            actual_res.append(coo_final) 
                            self.debuger.debug("add new item to actual_sub:", self.deal_with_print(coo_final.entity, ltp_result))              
        old_concept_res = concept_res
        '''
        if final_res != None:
            res.append(final_res)
            coo_final_lis = self.find_all_COO(final_res)
            for coo_final in coo_final_lis:
                if coo_final not in res:
                    res.append(coo_final)
                    self.debuger.debug("coo_final_res.word")
        '''

    def find_rel_sub(self, verb, entity_lis, ltp_result):
        if verb.search_sub_mark == True:
            return verb.concept_sub, verb.actual_sub
        concept_res = []
        actual_res = []
        #find all direct sub
        for child in verb.children:
            if child.rel == 'SBV':
                verb.direct_sub.append(child)
        for sub in verb.direct_sub:
            coo_direct_lis = self.find_all_COO(sub)
            for direct_sub in coo_direct_lis:
                if direct_sub not in verb.direct_sub:
                    verb.direct_sub.append(direct_sub)
        for sub in verb.direct_sub:
            if sub.entity != None:
                actual_res.append(sub)
            else:
                concept_res.append(sub)
        for node in verb.children:
            if node.entity != None and node.postag != 'nt' and node.rel == 'ATT':
                flag = 0
                for child in node.children:
                    if child.rel == 'RAD' and child.word == '的':
                        flag = 1
                        break
                if flag == 0 and node not in actual_res:
                    actual_res.append(node)
        self.find_actualsub_by_ATT(verb, entity_lis, ltp_result, concept_res, actual_res)
        #recursion 
        if len(actual_res) ==  0 and len(concept_res) == 0:
            path = self.find_path_to_root(verb)
            for node in path:
                if node.rel not in ['COO', 'VOB']:
                    break
                if node.father.postag == 'v':
                    con_res, act_res = self.find_rel_sub(node.father, entity_lis, ltp_result)
                    actual_res = act_res
                    concept_res = con_res
                    break
        #renew
        verb.search_sub_mark = True
        verb.actual_sub = actual_res
        verb.concept_sub = concept_res
        return concept_res, actual_res

    def deal_with_res(self, res, verb, e1, e2, ltp_result):
        op1 = []
        op2 = []
        res1 = []
        res2 = []
        r1 = []
        if verb != None:
            r2 = verb.word
        r3 = []
        if len(e1.mark) != 0:
            op1 = e1.mark
        else:
            op1 = [e1]
        if len(e2.mark) != 0:
            op2 = e2.mark
        else:
            op2 = [e2]
        for i in op1:
            if i.entity != None:
                res1.append(i.entity)
                r1.append(ltp_result.text(i.entity.st, i.entity.ed))
            else:
                res1.append(i.idx)
                r1.append(i.word)
        for i in op2:
            if i.entity != None:
                res2.append(i.entity)
                r3.append(ltp_result.text(i.entity.st, i.entity.ed))
            else:
                res2.append(i.idx)
                r3.append(i.word)
        for i in range(len(res1)):
            for j in range(len(res2)):
                if verb != None:
                    res.append((res1[i], verb.idx, res2[j]))
                    self.debuger.debug(r1[i], r2, r3[j])
                else:
                    res.append((res1[i], None, res2[j]))
                    self.debuger.debug(r1[i], "是", r3[j])

    def premark_entity(self, tree, e_lis, ltp_result):
        self.debuger.debug('|'*40)
        for e in e_lis:
            node_list = tree.nodes[e.st : e.ed]
            for node in node_list:
                node.entity = e
                self.debuger.debug("node", node.word ,"mark as entity:", ltp_result.text(e.st, e.ed))
        self.debuger.debug('|'*40)

    def deal_with_print(self, node, ltp_result):
        res = None
        if isinstance(node, StrEntity) == True:
            res = ltp_result.text(node.st, node.ed)
        else:
            res = node.word
        return res

    def  deal_with_quadruple(self, node, ltp_result):
        res_1 = None
        res_2 = None
        res_3 = None
        if isinstance(node[0], StrEntity) == True:
            res_1 = ltp_result.text(node[0].st, node[0].ed)
        elif isinstance(node[0], int) == True:
            res_1 = ltp_result.text(node[0], node[0]+1)
        elif isinstance(node[0], str) == True:
            res_1 = node[0]
        if node[1] == None:
            res_2 = "是"
        elif isinstance(node[1], int) == True:
            res_2 = ltp_result.text(node[1], node[1]+1)
        elif isinstance(node[1], str) == True:
            res_2 = node[1]
        if isinstance(node[2], StrEntity) == True:
            res_3 = ltp_result.text(node[2].st, node[2].ed)
        elif isinstance(node[2], int) == True:
            res_3 = ltp_result.text(node[2], node[2]+1)
        if node[3] == None:
            res = (res_1, res_2, res_3, "no environment")
        else:
            res_4 = ltp_result.text(node[3], node[3]+1)
            res = (res_1, res_2, res_3, res_4)
        return res

    def judge_remove_equal(self, node, ltp_result):
        ret = False
        #flag = 0
        res_1 = None
        res_2 = None
        if isinstance(node[1], str) == True: #deal with title_res
            return False
        '''
        if (tripple[1] != None and ltp_result.text(tripple[1], tripple[1]+1) == "是") or (tripple[1] == None):
            flag =1
        '''
        #if flag == 1:
        #self.debuger.debug("verb is \"is\"")
        if isinstance(node[0], StrEntity) == True:
            res_1 = ltp_result.text(node[0].st, node[0].ed)
        elif isinstance(node[0], int) == True:
            res_1 = ltp_result.text(node[0], node[0]+1)
        elif isinstance(node[0], str) == True:
            res_1 = node[0]
        if isinstance(node[2], StrEntity) == True:
            res_2 = ltp_result.text(node[2].st, node[2].ed)
        elif isinstance(node[2], int) == True:
            res_2 = ltp_result.text(node[2], node[2]+1)
        '''
        r = self. deal_with_quadruple(tripple, ltp_result)
        r1 = r[0]
        r2 = r[2]
        '''
        self.debuger.debug("res_1 is ",res_1)
        self.debuger.debug("res_2 is ",res_2)
        if res_1 == res_2:
            ret = True
            self.debuger.debug("tripple (a, is, a) is removed!")
        return ret

    def find_title(self, tree, ltp_result):
        res = []
        for node in tree.nodes:
            if node.entity != None and node.postag in ['n', 'nd', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz']:
                children = self.find_all_ATT_child(node)
                for child in children:
                    if child.postag not in ['n', 'nd', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz']:
                        continue
                    node_str = ltp_result.text(node.entity.st, node.entity.ed)
                    if child.word in self.nationality_dic and child.word not in node_str:
                        child.title = node.entity
                        self.debuger.debug("finding title relation: nationality")
                        self.debuger.debug("child:", child.word)
                        self.debuger.debug("father:", node_str)
                        res.append((child.word, "nationality", node.entity))
                    elif child.word in self.profession_dic and child.word not in node_str:
                        child.title = node.entity
                        self.debuger.debug("finding title relation: profession")
                        self.debuger.debug("child:", child.word)
                        self.debuger.debug("father:", node_str)
                        res.append((child.word, "profession", node.entity))
        return res

    def get_quintuple(self, triple):
        appendix = None
        res = []
        for item in triple:
            if isinstance(item[1], str) == True:
                if item[1] in ['nationality', 'profession']:
                    appendix = "title"
                else:
                    appendix = "coo_noun_type"
            else:
                if isinstance(item[2], int) == True:
                    appendix = "not_entity"
                elif isinstance(item[2], StrEntity) == True:
                    appendix = "entity"
            res.append((item[0], item[1], item[2], item[3], appendix))
        return res

    def add_environment(self, triples, tree):
        new_triples = []
        for item in triples:
            if isinstance(item[1], int) == True and tree.nodes[item[1]].postag == 'v':
                envir = [node.idx for node in tree.nodes[item[1]].environment]
                if len(envir) == 0:
                    new_triples.append((item[0], item[1], item[2], None))
                else:
                    for e in envir:
                        new_triples.append((item[0], item[1], item[2], e))
            else:
                new_triples.append((item[0], item[1], item[2], None))
        return new_triples

    def replace_pronoun(self, tree, ltp_result):
        for k in range(len(tree.nodes) - 1, -1, -1):
            node = tree.nodes[k]
            if node.postag == 'r':
                if node.word == '它':
                    for i in range(k-1, -1, -1):
                        if tree.nodes[i].postag != 'nh' and tree.nodes[i].entity != None:
                            node.father.children.remove(node)
                            node.word = tree.nodes[i].word
                            node.postag = tree.nodes[i].postag
                            node.nertag = tree.nodes[i].nertag
                            node.entity = tree.nodes[i].entity
                            node.title = tree.nodes[i].title
                            node.actual_sub = tree.nodes[i].actual_sub
                            node.concept_sub = tree.nodes[i].concept_sub
                            node.direct_sub = tree.nodes[i].direct_sub
                            node.obj = tree.nodes[i].obj
                            node.att = tree.nodes[i].att
                            node.target = tree.nodes[i].target
                            node.mark = tree.nodes[i].mark
                            node.father.children.append(node)
                            for j in node.children:
                                j.father = node
                                self.debuger.debug('*'*20)
                                self.debuger.debug(j.word, "father has been changed as:", ltp_result.text(tree.nodes[i].entity.st, tree.nodes[i].entity.ed))
                            #node = tree.nodes[i]
                            self.debuger.debug("replace 它 as:",\
                            ltp_result.text(tree.nodes[i].entity.st, tree.nodes[i].entity.ed))
                            self.debuger.debug('*'*40)
                            break
                elif node.word in ['他', '她']:
                    for i in range(k-1, -1, -1):
                        if tree.nodes[i].postag == 'nh':
                            node.father.children.remove(node)
                            node.word = tree.nodes[i].word
                            node.postag = tree.nodes[i].postag
                            node.nertag = tree.nodes[i].nertag
                            node.entity = tree.nodes[i].entity
                            node.title = tree.nodes[i].title
                            node.actual_sub = tree.nodes[i].actual_sub
                            node.concept_sub = tree.nodes[i].concept_sub
                            node.direct_sub = tree.nodes[i].direct_sub
                            node.obj = tree.nodes[i].obj
                            node.att = tree.nodes[i].att
                            node.target = tree.nodes[i].target
                            node.mark = tree.nodes[i].mark
                            node.father.children.append(node)
                            for j in node.children:
                                j.father = node
                                self.debuger.debug('*'*20)
                                self.debuger.debug(j.word, " father has been changed as:", tree.nodes[i].word)
                            #node = tree.nodes[i]
                            #self.debuger.debug("node's new father is:", node.father.word)
                            self.debuger.debug("replace 他/她", "as:", tree.nodes[i].word)
                            self.debuger.debug('*'*40)
                            break                 

    def judge_if_has_verb(self, tree):
        for node in tree.nodes:
            if node.postag == 'v':
                return True
        return False

    def find_ATT_part(self, node, tree, ltp_result):
        ed = node.idx
        st = node.idx
        for i in range(node.idx - 1, -1, -1):
            tmp_node = tree.nodes[i + 1]
            if tree.nodes[i].rel != 'ATT' or tree.nodes[i].father != tmp_node:
                st = i + 1
                break
        return ltp_result.text(st, ed + 1)

    def find_coo_noun_relation(self, tree, ltp_result):
        res = []
        #step one: find central word
        central_word = None
        if tree.root.entity != None:
            central_word = tree.root
        for node in tree.nodes:
            if node.entity != None:
                central_word = node
                break
        if central_word != None:
            self.debuger.debug("central word found: ", \
            self.deal_with_print(central_word.entity, ltp_result))
        else:
            self.debuger.debug("cannot find central word(entity)!")
            return []
        #step two: find coo-central word
        path = self.find_all_COO(central_word, ['n', 'nd', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz'])
        for node in path:
            nodes = self.find_direct_rel(node, ['ATT'], None, None, False)
            rel = []
            if len(nodes) == 0:
                rel = ["是"]
            for child in nodes:
                rel.append(self.find_ATT_part(child, tree, ltp_result))
            for r in rel:
                res.append((central_word.entity, r, node.idx))
        return res

    def find_tripple(self, ltp_result, e_lis):
        res = []
        entity_lis = []
        verb_lis = []
        tree = ParseTree(ltp_result)
        self.premark_entity(tree, e_lis, ltp_result)#mark every word in entity
        for node in tree.nodes:
            if node.postag == 'v':
                verb_lis.append(node)
        for e in e_lis:
            entity, near_verb, verb = self.find_2_verbs(tree, e)
            entity_lis.append(entity)
        #pronoun replacement
        self.replace_pronoun(tree, ltp_result)
        #find noun relation
        noun_res =[]
        for i in range(len(entity_lis)):
            for j in range(i + 1, len(entity_lis)):
                tmp_verb = self.find_noun_relation(entity_lis[i], entity_lis[j], tree);
                if(tmp_verb != None):
                    noun_res.append((entity_lis[i].entity, tmp_verb.idx, entity_lis[j].entity))
                    self.debuger.debug("noun relation found!")
        self.debuger.debug("noun_res:")
        for tmp in noun_res:
            self.debuger.debug(ltp_result.text(tmp[0].st, tmp[0].ed), \
            ltp_result.text(tmp[1], tmp[1] + 1), ltp_result.text(tmp[2].st, tmp[2].ed))
        #find title relation
        title_res = self.find_title(tree, ltp_result)
        self.debuger.debug("title_res:")
        for tmp in title_res:
            self.debuger.debug(tmp[0], tmp[1], ltp_result.text(tmp[2].st, tmp[2].ed))
        tmp_coo_noun_res = []
        coo_noun_res = []
        extra_title_res = []
        if self.judge_if_has_verb(tree) == False:
            tmp_coo_noun_res = self.find_coo_noun_relation(tree, ltp_result)
        for item in tmp_coo_noun_res:
            if tree.nodes[item[2]].entity != None:
                coo_noun_res.append(item)
            else:
                if tree.nodes[item[2]].word in self.nationality_dic:
                    extra_title_res.append((tree.nodes[item[2]].word, "nationality", item[0]))
                elif tree.nodes[item[2]].word in self.profession_dic:
                    extra_title_res.append((tree.nodes[item[2]].word, "profession", item[0]))
        for item in extra_title_res:
            if item not in title_res:
                title_res.append(item)
        #step one: find sub realation
        for verb in verb_lis:
            self.debuger.debug("verb", verb.word, "start finding its sub!")
            self.find_rel_sub(verb, entity_lis, ltp_result)
        #step two: renew sub mark(has 2 type)
        
        #type1: (actual_sub, is, concept_sub)
        '''
        for verb in verb_lis:
            if len(verb.actual_sub) != 0 and len(verb.concept_sub) != 0:
                for actual_sub in verb.actual_sub:
                    for concept_sub in verb.concept_sub:
                        if concept_sub.postag not in ['n', 'nd', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz']:
                            continue
                        if actual_sub.entity != None:
                            if concept_sub.entity != None:
                                res.append((actual_sub.entity, None, concept_sub.entity))
                            else:
                                res.append((actual_sub.entity, None, concept_sub.idx))
                        else:
                            if concept_sub.entity != None:
                                res.append((actual_sub.idx, None, concept_sub.entity))
                            else:
                                res.append((actual_sub.idx, None, concept_sub.idx))
                        self.debuger.debug("is relation found:(actual_sub, is, concept_sub)")
        '''
        #type2: (actual_sub, is, direct_obj_of_is)
        is_res = []
        for verb in verb_lis:
            if verb.word == '是' and len(verb.actual_sub) != 0:
                for child in verb.children:
                    if child.rel in ['VOB', 'FOB'] and child not in verb.actual_sub \
                    and child.postag in ['n', 'nd', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz']:
                        for actual_sub in verb.actual_sub:
                            if actual_sub.title != None or child.title != None:
                                continue
                            child.mark.append(actual_sub)
                            if actual_sub.entity != None:
                                if child.entity != None:
                                    is_res.append((actual_sub.entity, None, child.entity))
                                else:
                                    is_res.append((actual_sub.entity, None, child.idx))
                            else:
                                if child.entity != None:
                                    is_res.append((actual_sub.idx, None, child.entity))
                                else:
                                    is_res.append((actual_sub.idx, None, child.idx))
                            self.debuger.debug("is relation found:(actual_sub, is, direct_obj_of_is)")
        '''
        self.debuger.debug("is_res:")
        for tmp in is_res:
            r = self. deal_with_quadruple(tmp, ltp_result)
            r1 = r[0]
            r2 = r[2]
            self.debuger.debug(r1, "是", r2)
        '''
        #step three: confirm the obj, att, target part
        #obj&debug:
        self.debuger.debug("start finding environment!")
        self.get_environment_rule_1(verb_lis)
        for verb in verb_lis:
            self.debuger.debug("#"*30)
            self.debuger.debug("verb", verb.word, "start finding object!")
            self.find_verb_OBJ(verb, entity_lis)
        #att:
        self.find_all_ATT(entity_lis)
        #target:
        self.find_all_TARGET(verb_lis, entity_lis)
        #step four: return tripple
        sub_verb_obj = []
        sub_verb_att = []
        sub_verb_target = []
        obj_verb_target = []
        att_verb_target = []
        self.debuger.debug("start return tripple!")
        for verb in verb_lis:
            self.debuger.debug("for verb", verb.word)
            for sub in verb.actual_sub:
                for obj in verb.obj:
                    self.debuger.debug("-"*20)
                    self.debuger.debug("sub-verb-obj relation found!")
                    self.deal_with_res(sub_verb_obj, verb, sub, obj, ltp_result)
                    self.debuger.debug("-"*20)
                for att in verb.att:
                    self.debuger.debug("-"*20)
                    self.debuger.debug("sub-verb-att relation found!")
                    self.deal_with_res(sub_verb_att, verb, sub, att, ltp_result)
                    self.debuger.debug("-"*20)
                for target in verb.target:
                    self.debuger.debug("-"*20)
                    self.debuger.debug("sub-verb-target relation found!")
                    self.deal_with_res(sub_verb_target, verb, sub, target, ltp_result)
                    self.debuger.debug("-"*20)
            if len(verb.actual_sub) == 0:
                for obj in verb.obj:
                    for target in verb.target:
                        self.debuger.debug("-"*20)
                        self.debuger.debug("obj-verb-target relation found!")
                        self.deal_with_res(obj_verb_target, verb, obj, target, ltp_result)
                        self.debuger.debug("-"*20)
                for att in verb.att:
                    for target in verb.target:
                        self.debuger.debug("-"*20)
                        self.debuger.debug("att-verb-target relation found!")
                        self.deal_with_res(att_verb_target, verb, att, target, ltp_result)
                        self.debuger.debug("-"*20)
        #debug
        for verb in verb_lis:
            self.debuger.debug("verb", verb.word, "has actual_sub:")
            for actual_sub in verb.actual_sub:
                self.debuger.debug(self.deal_with_print(actual_sub, ltp_result))
            self.debuger.debug("verb", verb.word, "has concept_sub:")
            for concept_sub in verb.concept_sub:
                self.debuger.debug(self.deal_with_print(concept_sub, ltp_result))
            self.debuger.debug("verb", verb.word, "has obj:")
            for obj in verb.obj:
                self.debuger.debug(self.deal_with_print(obj, ltp_result))
            self.debuger.debug("verb", verb.word, "has att:")
            for att in verb.att:
                self.debuger.debug(self.deal_with_print(att, ltp_result))
            self.debuger.debug("verb", verb.word, "has target:")
            for target in verb.target:
                self.debuger.debug(self.deal_with_print(target, ltp_result))
            self.debuger.debug('-'*40)
        for node in tree.nodes:
            self.debuger.debug("node", node.word, "has mark:")
            for mark in node.mark:
                tmp = self.deal_with_print(mark, ltp_result)
                self.debuger.debug(tmp)

        res = noun_res + title_res + coo_noun_res +sub_verb_obj + sub_verb_att + \
        sub_verb_target + obj_verb_target + att_verb_target #leave out is_relation
        res = set(res)
        final_res = []
        for i in res:
            if self.judge_remove_equal(i, ltp_result) == False:
                final_res.append(i)
        final_res = self.add_environment(final_res, tree)
        final_res = self.get_quintuple(final_res)
        return final_res

if __name__ == "__main__":
    '''
    ltp = LTP(None)
    s = "1988年，主演由王家卫执导的黑帮片《旺角卡门》[4]，塑造了一个重情重义的江湖混混华仔形象，使其首次获得香港电影金像奖最佳男主角提名。".encode('utf-8')
    ltp_result = ltp.parse(sentence)
    ner = NamedEntityReg(process_bracket_flag = True, add_time_entity = True)
    es = ner.recognize(sentence, ltp_result, None, None)
    '''
    sentence = "任天堂推出了Donkey Kong的续集——Donkey Kong Jr.，同样是一款街机游戏。".encode('utf-8')
    doc_processor = DocProcessor()
    ltp_result, _ = doc_processor.parse_sentence(sentence, ParagraphInfo(3, ['刘德华'], '刘德华', False, True))
    ner = NamedEntityReg(process_bracket_flag = True, add_time_entity = True)
    es = ner.recognize(sentence, ltp_result, None, None)
    tree = ParseTree(ltp_result)
    info = PrintInfo()
    info.print_ltp(ltp_result, tree)
    e_lis = []
    '''
    e_lis.append(StrEntity(5, 6, None))
    e_lis.append(StrEntity(17, 18, None))
    e_lis.append(StrEntity(25, 26, None))
    e_lis.append(StrEntity(3, 4, None))
    e_lis.append(StrEntity(27, 28, None))
    e_lis.append(StrEntity(0, 2, None))
    e_lis.append(StrEntity(22, 24, None))
    '''
    test = VerbRelationExtractor(True)
    tripple_res = test.find_tripple(ltp_result, es)
    #print tripple_res
    r1 = None
    r2 = None
    r3 = None
    ret = []
    tmp_tripple_res = []
    extrainfo = []
    for item in tripple_res:
        tmp_tripple_res.append((item[0], item[1], item[2], item[3]))
        extrainfo.append(item[4])
    tripple_res = tmp_tripple_res
    for k, item in enumerate(tripple_res):
        ret.append(test. deal_with_quadruple(item, ltp_result))
    #ret = set(ret)
    for k, triple in enumerate(ret):
        print '\t%s' %('\t'.join(triple)), '\t', extrainfo[k]