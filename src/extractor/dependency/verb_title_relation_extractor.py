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

    def find_noun_relation(self, e1, e2):
        if e1.depth - e2.depth == 2:
            if e1.rel == 'ATT' and e1.father.rel == 'ATT' and e1.father.father == e2:
                for child in e1.children:
                    if child.rel == 'RAD' and child.word == '的':
                        return e1.father
        elif e2.depth - e1.depth == 2:
            if e2.rel == 'ATT' and e2.father.rel == 'ATT' and e2.father.father == e1:
                for child in e2.children:
                    if child.rel == 'RAD' and child.word == '的':
                        return e2.father
        return None

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

    def judge_title_tag(self, node):
        if node.postag in ['n', 'ns']:
            return True
        return False

    def find_all_COO_title(self, node):
        res = []
        path = self.find_path_to_root(node)
        for p in path:
            if p.rel == 'COO' and self.judge_title_tag(p.father) == True:
                res.append(p.father)
        for child in node.children:
            res += self.trace_down_title_rule2(child)
        return res

    def find_COO_or_ATT_title(self, node):
        res = []
        for child in node.children:
            if child.rel == 'ATT' and self.judge_title_tag(child) == True:
                res += self.trace_down_title_rule1(child)
        return res

    def trace_down_title_rule2(self, node):
        res = []
        if node.rel == 'COO' and self.judge_title_tag(node) == True:
            res.append(node)
        else:
            return []
        for child in node.children:
            res += self.trace_down_title_rule2(child)
        return res

    def trace_down_title_rule1(self, node):
        res = []
        if node.rel in ['ATT', 'COO'] and self.judge_title_tag(node) == True:
            res.append(node)
        else:
            return []
        for child in node.children:
            res += self.trace_down_title_rule1(child)
        return res

    def find_title(self, ltp_result, e, entity_pool):
        tree = ParseTree(ltp_result)
        father, near_verb, verb = self.find_2_verbs(tree, e)
        res1 = self.find_all_COO_title(father)
        res2 = self.find_COO_or_ATT_title(father)
        new_res_1 = new_res_2 = []
        for words in res1:
            #if entity_pool[words.idx] == False:
            new_res_1.append(words)
        for words in res2:
            #if entity_pool[words.idx] == False:
            new_res_2.append(words)
        new_res = new_res_1 + new_res_2
        new_res = set(new_res)
        final_res = []
        for i in new_res:
            final_res.append((i.idx, i.idx + 1))
        '''
        final_res = []
        for i in res:
            final_res.append((res.idx, res.idx + 1))
        '''
        return final_res

    def find_all_COO_father(self, node):
        res = []
        path = self.find_path_to_root(node)
        for node in path:
            if node.rel == 'COO':
                res.append(node.faher)
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

    def find_all_COO(self, node):
        res = self.find_all_COO_father(node) + self.find_all_COO_child(node)
        return res

    def find_rel_sub(self, verb, entity_lis):
        ret = None
        for verb_child in verb.children:
            if verb_child.rel == 'SBV':
                if verb_child in entity_lis:
                    verb.actual_sub.append(verb_child)
                    ret = 'actual'
                    break
                elif verb_child not in entity_lis:
                    verb.concept_sub.append(verb_child)
                    ret = 'concept'
        if ret == 'actual':
            if len(verb.actual_sub) != 1:
                self.debuger.debug('more than one actual sub!')
                return None
            coo_act_lis = self.find_all_COO(verb.actual_sub[0])
            for coo_act_sub in coo_act_lis:
                if coo_act_sub != verb.actual_sub[0]:
                    verb.actual_sub.append(coo_act_sub)
        if ret == 'concept':
            for concept_sub in verb.concept_sub:
                coo_concept_lis = self.find_all_COO(concept_sub)
                for coo_concept_sub in coo_concept_lis:
                    if coo_concept_sub not in verb.concept_sub:
                        verb.concept_sub.append(coo_concept_sub)

        return ret

    def judge_all_ATT(self, path):
        for node in path:
            if node.rel != 'ATT':
                return False
        return True

    def find_all_TARGET(self, verb_lis):
        for verb in verb_lis:
            if verb.rel == 'ATT':
                verb.target.append(verb.father)

    def find_all_ATT(self, entity_lis):
        for entity in entity_lis:
            path = self.find_path_to_root(entity)
            for node in path[:-1]:
                if node.father.postag == 'v':
                    if node.rel in ['ATT', 'ADV', 'CMP']:
                        if entity not in node.father.att:
                            node.father.att.apppend(entity)
                break

    def find_all_OBJ(self, entity_lis):
        for entity in entity_lis:
            path = self.find_path_to_root(entity)
            for node in path[:-1]:
                if node.father.postag == 'v':
                    if node.rel in ['VOB', 'FOB']:
                        if entity not in node.father.obj:
                            node.father.obj.append(entity)
                    break

    def find_special_OBJ(self, entity_lis, verb):
        for child in verb.children:
            if child.rel in ['VOB', 'FOB'] and child.postag == 'v':
                if len(child.actual_sub) != 0:
                    verb.obj += child.actual_sub
                else:
                    verb.obj += self.find_special_OBJ(entity_lis, child)
                    break
        return verb.obj

    def mark_subject(self, verb, entity_lis, tree):
        if self.find_rel_sub(verb, entity_lis) == 'actual':
            return
        else:
            path = self.find_path_to_root(verb)
            for node in path:
                if node.rel not in ['COO', 'VOB']:
                    break
                if node.father.postag == 'v':
                    if self.find_rel_sub(node, entity_lis) == 'actual':
                        return
        res = []
        res_depth = []
        final_res = None
        for concept_sub in verb.concept_sub:
            for entity in entity_lis:
                path1, path2 = tree.find_path(verb.idx, entity.idx)
                if len(path1) == 1 and self.judge_all_ATT(path2) == True:
                    res.append(entity)
                    res_depth.append(entity.depth)
        if len(res_depth) != 0:
            min_depth = min(res_depth)
            final_res = res[res_depth.index(min_depth)]
        if final_res != None:
            verb.actual_sub.append(final_res)
            coo_final_lis = self.find_all_COO(final_res)
            for coo_final in coo_final_lis:
                if coo_final != final_res:
                    verb.actual_sub.append(coo_final)
        return

    def find_tripple(self, ltp_result, e_lis, entity_pool):
        res = []
        entity_lis = []
        verb_lis = []
        tree = ParseTree(ltp_result)
        for node in tree.nodes:
            if node.postag == 'v':
                verb_lis.append(node)
        for e in e_lis:
            entity, near_verb, verb = self.find_2_verbs(tree, e)
            entity_lis.append(entity)
        #judge noun relation
        for i in range(len(entity_lis)):
            for j in range(i + 1, len(entity_lis)):
                tmp_verb = self.find_noun_relation(entity_lis[i], entity_lis[j]);
                if(tmp_verb != None):
                    res.append((entity_lis[i].idx, tmp_verb.idx, entity_lis[j].idx))
        #step one: mark sub
        #for each verb mark
        for verb in verb_lis:
            self.mark_subject(verb, entity_lis, tree)
        #(actual_sub, is, concept_sub)
        for verb in verb_lis:
            if len(verb.actual_sub) != 0 and len(verb.concept_sub) != 0:
                for actual_sub in verb.actual_sub:
                    for concept_sub in verb.concept_sub:
                        res.append((actual_sub.idx, None, concept_sub.idx))
        #step two: renew sub mark
        #concept_sub => actual_sub
        for verb in verb_lis:
            for concept_sub in verb.concept_sub:
                if concept_sub not in verb.actual_sub:
                    verb.actual_sub.append(concept_sub)
        #is relation
        for verb in verb_lis:
            if verb.word == '是' and len(verb.actual_sub) != 0:
                for child in verb.children:
                    if child.rel in ['VOB', 'FOB'] and child not in verb.actual_sub:
                        verb.actual_sub.append(child)
        #step three: confirm the obj, att, target part
        #obj&debug:
        for verb in verb_lis:
            self.find_special_OBJ(entity_lis, verb)
            print '#'*30
            self.debuger.debug("verb", verb.word, "has obj:")
            for obj in verb.obj:
                self.debuger.debug(obj.word)
            print '#'*30
        self.find_all_OBJ(entity_lis)
        for verb in verb_lis:
            self.debuger.debug("verb", verb.word, "has obj:")
            for obj in verb.obj:
                self.debuger.debug(obj.word)
            print '#'*30
        #att:
        self.find_all_ATT(entity_lis)
        #target:
        self.find_all_TARGET(verb_lis)
        #step four: return tripple
        for verb in verb_lis:
            for sub in verb.actual_sub:
                for obj in verb.obj:
                    res.append((sub.idx, verb.idx, obj.idx))
                for att in verb.att:
                    res.append((sub.idx, verb.idx, att.idx))
                for target in verb.target:
                    res.append((sub.idx, verb.idx, target.idx))
            for obj in verb.obj:
                for target in verb.target:
                    res.append((obj.idx, verb.idx, target.idx))
            for att in verb.att:
                for target in verb.target:
                    res.append((att.idx, verb.idx, target.idx))
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

        return res

if __name__ == "__main__":
    ltp = LTP(None)
    ltp_result = ltp.parse("1993年，主演刘镇伟执导的浪漫剧情片《天长地久》，刘德华与刘锦玲和吴家丽合作诠释了一段悲剧爱情故事。")
    info = PrintInfo()
    info.print_ltp(ltp_result)
    tree = ParseTree(ltp_result)
    st, ed = ltp_result.search_word("刘德华")
    if st == -1 and ed == -1:
        print "cannot find word!!", "刘德华"
    e1 = StrEntity(st, ed, None)
    st, ed = ltp_result.search_word("刘锦玲")
    if st == -1 and ed == -1:
        print "cannot find word!!", "刘锦玲"
    e2 = StrEntity(st, ed, None)
    st, ed = ltp_result.search_word("吴家丽")
    if st == -1 and ed == -1:
        print "cannot find word!!", "吴家丽"
    e3 = StrEntity(st, ed, None)
    st, ed = ltp_result.search_word("刘镇伟")
    if st == -1 and ed == -1:
        print "cannot find word!!", "刘镇伟"
    e4 = StrEntity(st, ed, None)
    st, ed = ltp_result.search_word("天长地久")
    if st == -1 and ed == -1:
        print "cannot find word!!", "天长地久"
    e5 = StrEntity(st, ed, None)
    entity_pool = []
    e_lis = [e1, e2, e3, e4, e5]
    for i in range(ltp_result.length):
        entity_pool.append(0)
    res = VerbRelationExtractor(True)
    tripple_res = res.find_tripple(ltp_result, e_lis, entity_pool)
    for k, item in enumerate(tripple_res):
        print 'tripple', k, 'is:'
        if item[1] == None:
            print '(', tree.nodes[item[0]].word, ',', '是', ',', tree.nodes[item[2]].word, ')'
        else:
            print '(', tree.nodes[item[0]].word, ',', tree.nodes[item[1]].word, ',', tree.nodes[item[2]].word, ')'