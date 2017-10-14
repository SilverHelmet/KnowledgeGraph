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
                        return e1.father
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
            if entity_pool[res[0]] == 1:
                self.debuger.debug('found verb', ltp_result.words[res[0]] ,'is an entity! error!')
        return advanced_res
    
if __name__ == "__main__":
    ltp = LTP(None)
    sentence = '1993年，主演刘镇伟执导的浪漫剧情片《天长地久》，刘德华与刘锦玲和吴家丽合作诠释了一段悲剧爱情故事。'
    ltp_result = ltp.parse(sentence)
    info = PrintInfo()
    info.print_ltp(ltp_result)
    e1 = '刘镇伟'
    e2 = '天长地久'
    st, ed = ltp_result.search_word(e1)
    e1 = StrEntity(st, ed)
    st, ed = ltp_result.search_word(e2)
    e2 = StrEntity(st, ed)
    entity_pool = []
    for i in range(ltp_result.length):
        entity_pool.append(0)
    res = VerbRelationExtractor(True)
    tmp1 = res.find_relation(ltp_result, e1, e2, entity_pool)
    for ans in tmp1:
        print ltp_result.words[ans[0]]
