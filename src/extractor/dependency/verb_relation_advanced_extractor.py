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
        if verb1.father != None:
            if verb1.father == verb2 and verb1.rel == 'COO':
                return True
        if verb2.father != None:
            if verb2.father == verb1 and verb2.rel == 'COO':
                return True
        return False
    
    def judge_one_SBV(self, near_verb1, near_verb2):
        if near_verb1.rel == 'SBV' and near_verb2.rel != 'SBV':
            return near_verb2.father
        elif near_verb2.rel == 'SBV' and near_verb1.rel != 'SBV': 
            return near_verb1.father
        return None

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
    
    def find_relation(self, ltp_result, e1, e2, entity_pool):
        advanced_res = []
        tree = ParseTree(ltp_result)
        node_list_1 = tree.nodes[e1.st : e1.ed]
        node_list_2 = tree.nodes[e2.st : e2.ed]
        w1 = self.find_coo_father(node_list_1)
        w2 = self.find_coo_father(node_list_2)
        p1 = self.find_path_to_root(tree.nodes[w1])
        p2 = self.find_path_to_root(tree.nodes[w2])
        near_verb1 = self.find_nearest_verb(p1)[0]      
        verb1 = self.find_nearest_verb(p1)[1]
        near_verb2 = self.find_nearest_verb(p2)[0]
        verb2 = self.find_nearest_verb(p2)[1]
        if verb1 == None or verb2 == None:
            self.debuger.debug("can't find nearest verb!")
        elif near_verb1.rel == near_verb2.rel:
            self.debuger.debug("the relation to verb is same! not found!")
        elif verb1 == verb2:
            self.debuger.debug("same verb found!")
            advanced_res.append((verb1.idx, verb1.idx + 1))
        else:
            if self.judge_coo(verb1, verb2):
                one_SBV = self.judge_one_SBV(near_verb1, near_verb2)
                if one_SBV != None:
                    self.debuger.debug("coo verbs and one SBV found!")
                    advanced_res.append((one_SBV.idx, one_SBV.idx + 1))
                else:
                    self.debuger.debug("coo verbs but not one SBV! not found!")
            else:
                self.debuger.debug("other situation not found!")
        for res in advanced_res:
            if entity_pool[res[0]] == 1:
                self.debuger.debug('found verb', ltp_result.words[res[0]] ,'is an entity! error!')
        return advanced_res
    
if __name__ == "__main__":
    ltp = LTP(None)
    sentence = '1982年，刘德华参演许鞍华指导的影片《怒海》，从此走上了演艺之路。'
    ltp_result = ltp.parse(sentence)
    info = PrintInfo()
    info.print_ltp(ltp_result)
    print sentence
    e1 = '刘德华'
    e2 = '怒海'
    st, ed = ltp_result.search_word(e1)
    e1 = StrEntity(st, ed)
    st, ed = ltp_result.search_word(e2)
    e2 = StrEntity(st, ed)
    entity_pool = []
    for i in range(ltp_result.length):
        entity_pool.append(0)
    res = VerbRelationExtractor(True)
    tmp1 = res.find_relation(ltp_result, e1, e2, entity_pool)
    print ltp_result.words[tmp1[0][0]]
