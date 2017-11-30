#encoding: utf-8
from tree import ParseTree, Debug, PrintInfo
from ..ltp import LTP
from ..structure import StrEntity

class VerbRelationExtractor:
    def __init__(self, debug_flag = False):
        self.debuger = Debug(debug_flag)
        pass
      
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
        noun_res = self.find_noun_relation(father1, father2)
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



    def find_noun_relation(self, e1, e2):
        if e1.depth - e2.depth == 2:
            if e1.rel == 'ATT' and e1.father.rel == 'ATT' and e1.father.father == e2:
                for child in e1.children:
                    if child.rel == 'RAD' and child.word == '的':
                        self.debuger.debug("-"*20)
                        self.debuger.debug("find noun relation!")
                        self.debuger.debug(e1.word, e1.father.word, e2.word)
                        self.debuger.debug("-"*20)
                        return e1.father
        elif e2.depth - e1.depth == 2:
            if e2.rel == 'ATT' and e2.father.rel == 'ATT' and e2.father.father == e1:
                for child in e2.children:
                    if child.rel == 'RAD' and child.word == '的':
                        self.debuger.debug("-"*20)
                        self.debuger.debug("find noun relation!")
                        self.debuger.debug(e2.word, e2.father.word, e1.word)
                        self.debuger.debug("-"*20)
                        return e2.father
        return None

    def find_direct_SBV_entity(self, verb, entity_lis):
        res = []
        for child in verb.children:
            if child.rel == 'SBV' and child in entity_lis and child.title == None:
                res.append(child)
        return res

    def find_ATT_or_COO_path(self, node):
        res = []
        path = self.find_path_to_root(node)
        for node in path:
            if node.rel in ['ATT', 'COO']:
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

    def find_all_COO(self, node):
        res = self.find_all_COO_father(node) + self.find_all_COO_child(node)
        return res

    def judge_all_ATT(self, path):
        for node in path:
            if node.rel != 'ATT':
                return False
        return True

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
        for child in verb.children:
            if child.postag == 'v' and child.rel in ['VOB', 'FOB']:
                if_special_obj = True
                direct_sub = self.find_direct_SBV_entity(child, entity_lis)
                if len(direct_sub) != 0:
                    obj_res += direct_sub
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

    def find_actualsub_by_ATT(self, verb, entity_lis, tree, old_concept_res):
        self.debuger.debug("verb", verb.word, "start finding sub by att!")
        res = []
        res_depth = []
        final_res = None
        for node in  old_concept_res:
            self.debuger.debug("verb", verb.word, "concept word:", node.word)
        for concept_sub in old_concept_res:
            for entity in entity_lis:
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
        if len(res_depth) != 0:
            min_depth = min(res_depth)
            final_res = res[res_depth.index(min_depth)]
            self.debuger.debug("final_res.word")
        if final_res != None:
            res.append(final_res)
            coo_final_lis = self.find_all_COO(final_res)
            for coo_final in coo_final_lis:
                if coo_final not in res:
                    res.append(coo_final)
                    self.debuger.debug("coo_final_res.word")
        return res

    def find_rel_sub(self, verb, entity_lis, tree):
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
        tmp_res = self.find_actualsub_by_ATT(verb, entity_lis, tree, concept_res)
        for res in tmp_res:
            if res.entity != None:
                actual_res.append(res)
        for res in tmp_res:
            if res in concept_res:
                concept_res.remove(res)
        #recursion 
        if len(actual_res) ==  0 and len(concept_res) == 0:
            path = self.find_path_to_root(verb)
            for node in path:
                if node.rel not in ['COO', 'VOB']:
                    break
                if node.father.postag == 'v':
                    con_res, act_res = self.find_rel_sub(node.father, entity_lis, tree)
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

    def build_dict(self):
        self.nationality_dic = []
        self.profession_dic = []
        #name = ["nationality.txt", "full_profession.txt", "province.txt", "langauge.txt", "citytown.txt"]
        name = ["", ""]
        with open("result/rel_extraction/dict/nationality.txt", "r") as f:
            self.nationality_dic = f.readlines()
        for i in range(len(self.nationality_dic)):
            self.nationality_dic[i] = self.nationality_dic[i].replace("\n","")
        with open("result/rel_extraction/dict/full_profession.txt", "r") as f:
            self.profession_dic = f.readlines()
        for i in range(len(self.profession_dic)):
            self.profession_dic[i] = self.profession_dic[i].replace("\n","")

    def deal_with_print(self, node, ltp_result):
        res = None
        if isinstance(node, StrEntity) == True:
            res = ltp_result.text(node.st, node.ed)
        else:
            res = node.word
        return res

    def deal_with_tripple(self, node, ltp_result):
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
        res = (res_1, res_2, res_3)
        return res

    def judge_remove_is(self, tripple, ltp_result):
        ret = False
        flag = 0
        if isinstance(tripple[1], str) == True: #deal with title_res
            return False
        if (tripple[1] != None and ltp_result.text(tripple[1], tripple[1]+1) == "是") or (tripple[1] == None):
            flag =1
        if flag == 1:
            self.debuger.debug("verb is \"is\"")
            r = self.deal_with_tripple(tripple, ltp_result)
            r1 = r[0]
            r2 = r[2]
            self.debuger.debug("r1 is ",r1)
            self.debuger.debug("r2 is ",r2)
            if r1 == r2:
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
        #find noun relation
        noun_res =[]
        for i in range(len(entity_lis)):
            for j in range(i + 1, len(entity_lis)):
                tmp_verb = self.find_noun_relation(entity_lis[i], entity_lis[j]);
                if(tmp_verb != None):
                    noun_res.append((entity_lis[i].entity, tmp_verb.idx, entity_lis[j].entity))
                    self.debuger.debug("noun relation found!")
        self.debuger.debug("noun_res:")
        for tmp in noun_res:
            self.debuger.debug(ltp_result.text(tmp[0].st, tmp[0].ed), \
            ltp_result.text(tmp[1], tmp[1] + 1), ltp_result.text(tmp[2].st, tmp[2].ed))
        #find title relation
        title_res = []
        self.build_dict()
        title_res = self.find_title(tree, ltp_result)
        self.debuger.debug("title_res:")
        for tmp in title_res:
            self.debuger.debug(tmp[0], tmp[1], ltp_result.text(tmp[2].st, tmp[2].ed))

        #step one: find sub realation
        for verb in verb_lis:
            self.debuger.debug("verb", verb.word, "start finding its sub!")
            self.find_rel_sub(verb, entity_lis, tree)
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
        self.debuger.debug("is_res:")
        for tmp in is_res:
            r = self.deal_with_tripple(tmp, ltp_result)
            r1 = r[0]
            r2 = r[2]
            self.debuger.debug(r1, "是", r2)
        #step three: confirm the obj, att, target part
        #obj&debug:
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
                self.debuger.debug(actual_sub.word)
            self.debuger.debug("verb", verb.word, "has concept_sub:")
            for concept_sub in verb.concept_sub:
                self.debuger.debug(concept_sub.word)
            self.debuger.debug("verb", verb.word, "has obj:")
            for obj in verb.obj:
                self.debuger.debug(obj.word)
            self.debuger.debug("verb", verb.word, "has att:")
            for att in verb.att:
                self.debuger.debug(att.word)
            self.debuger.debug("verb", verb.word, "has target:")
            for target in verb.target:
                self.debuger.debug(target.word)
            self.debuger.debug('-'*40)
        for node in tree.nodes:
            self.debuger.debug("node", node.word, "has mark:")
            for mark in node.mark:
                tmp = self.deal_with_print(mark, ltp_result)
                self.debuger.debug(tmp)
        res = noun_res + title_res + is_res + sub_verb_obj + sub_verb_att + \
        sub_verb_target + obj_verb_target + att_verb_target
        res = set(res)
        final_res = []
        for i in res:
            if self.judge_remove_is(i, ltp_result) == False:
                final_res.append(i)
        return final_res

if __name__ == "__main__":
    ltp = LTP(None)
    ltp_result = ltp.parse("2017年8月4日，巴黎圣日耳曼官方宣布正式签下了巴西球星内马尔，合约5年。而巴塞罗那官方也承认，内马尔的法律顾问支付了2.22亿欧元的违约金，终止了双方的合同。")
    info = PrintInfo()
    info.print_ltp(ltp_result)
    tree = ParseTree(ltp_result)
    string = ["巴黎圣日耳曼官方","巴塞罗那官方","内马尔","巴西球星","2017年8月4日"]
    e_lis = []
    for s in string:
        st, ed = ltp_result.search_word(s)
        if st == -1 and ed == -1:
            print "cannot find word!!", s
        else:
            e_lis.append(StrEntity(st, ed, None))
    test = VerbRelationExtractor(True)
    tripple_res = test.find_tripple(ltp_result, e_lis)
    #print tripple_res
    r1 = None
    r2 = None
    r3 = None
    ret = []
    for k, item in enumerate(tripple_res):
        ret.append(test.deal_with_tripple(item, ltp_result))
    ret = set(ret)
    for triple in ret:
        print '\t%s' %('\t'.join(triple))