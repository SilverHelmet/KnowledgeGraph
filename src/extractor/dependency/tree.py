#encoding: utf-8
from ..ltp import LTP, LTPResult
from ..structure import StrEntity

class Debug:
    def __init__(self, flag):
        self.flag = flag
        
    def debug(self, *l):
        if self.flag:
            l = map(str, l)
            print("\t".join(l))
        else:
            pass

class ParseTree:
    def __init__(self, ltp_result):
        self.length = ltp_result.length
        self.nodes = []
        idx = 0
        for tag, arc, word in zip(ltp_result.tags, ltp_result.arcs, ltp_result.words):
            node = Node(idx, tag, arc, word)
            self.nodes.append(node)
            idx += 1            
        for node, arc in zip(self.nodes, ltp_result.arcs):
            father_idx = arc.head
            if father_idx == self.length:
                continue
            node.father = self.nodes[father_idx]
        self.calc_depth()

    def calc_depth(self):
        for node in self.nodes:
            node.search_depth()

    def find_LCA(self, n1_idx, n2_idx):
        n1 = self.nodes[n1_idx]
        n2 = self.nodes[n2_idx]
        while n1.idx != n2.idx:
            if n1.depth > n2.depth:
                n1 = n1.father
            elif n1.depth < n2.depth:
                n2 = n2.father
            else:
                n1 = n1.father
                n2 = n2.father
        return n1

    def find_path(self, n1_idx, n2_idx):
        lca = self.find_LCA(n1_idx, n2_idx)
        n1 = self.nodes[n1_idx]
        n2 = self.nodes[n2_idx]
        path1 = self.find_path_to_father(n1, lca)
        path2 = self.find_path_to_father(n2, lca)
        return path1, path2

    def find_path_to_father(self, node, father):
        path = [node]
        while node.idx != father.idx:
            node = node.father
            path.append(node)
        return path
    
class Node:
    def __init__(self, idx, postag, arc, word = None, nertag = None):
        self.idx = idx
        self.postag = postag
        self.rel = arc.relation
        self.word = word
        self.nertag = nertag
        self.father = None
        self.depth = -1

    def search_depth(self):
        if self.depth != -1:
            pass
        elif self.father is None:
            self.depth = 0
        else:
            self.depth = self.father.search_depth() + 1
        return self.depth
'''
输入的参数是(ltp_result, e1, e2, entity_pool)
e1, e2是struecture.py 下面的 StrEntity类型 有st和ed属性，代表一个识别的实体
'''
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

    def find_relation(self, ltp_result, e1, e2, entity_pool):
        simple_res = []
        tree = ParseTree(ltp_result)
        node_list_1 = tree.nodes[e1.st : e1.ed]
        node_list_2 = tree.nodes[e2.st : e2.ed]
        w1 = self.find_coo_father(node_list_1)
        w2 = self.find_coo_father(node_list_2)
        p1 = self.find_path_to_root(tree.nodes[w1])
        p2 = self.find_path_to_root(tree.nodes[w2])
        coo_p = p1 + p2[:-1]
        for node in coo_p:
            if node.postag == 'v':
                if entity_pool[node.idx] == 1:
                    pass
                else:
                    simple_res.append((node.idx, node.idx + 1))
        return simple_res
    
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
    
    def extract_relation(self, ltp_result, e1, e2, entity_pool):
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
        return advanced_res
    
if __name__ == "__main__":
    ltp = LTP(None)
    sentence = '任天堂株式会社(日文:任天堂株式会社，平假名:にんてんどうかぶしきがいしゃ)于1947年11月20日成立 。'
    ltp_result = ltp.parse(sentence)
    for i in range(ltp_result.length):
        print i, ":", ltp_result.words[i], ltp_result.tags[i]
    for i in range(len(ltp_result.arcs)):
        if ltp_result.arcs[i].head == ltp_result.length:
            print 'ROOT', "--", ltp_result.arcs[i].relation, '--',ltp_result.words[i], '(', ltp_result.tags[i], ')'
        else:
            print ltp_result.words[ltp_result.arcs[i].head], '(', ltp_result.tags[ltp_result.arcs[i].head], ')', "--", ltp_result.arcs[i].relation, '--', ltp_result.words[i], '(', ltp_result.tags[i], ')'
    print sentence
    e1 = '任天堂'
    e2 = '1947年11月20日'
    st, ed = ltp_result.search_word(e1)
    e1 = StrEntity(st, ed)
    st, ed = ltp_result.search_word(e2)
    e2 = StrEntity(st, ed)
    entity_pool = []
    for i in range(ltp_result.length):
        entity_pool.append(0)
    res = VerbRelationExtractor(True)
    tmp1 = res.find_relation(ltp_result, e1, e2, entity_pool)
    tmp2 = res.extract_relation(ltp_result, e1, e2, entity_pool)
    print tmp1
    print tmp2
    