#encoding: utf-8
from ..ltp import LTP

class PrintInfo:
    def __init__(self):
        pass
    def print_ltp(self,ltp_result, tree):
        print ltp_result.sentence
        print "its root is:", tree.root.word
        for i in range(ltp_result.length):
            print i, ":", ltp_result.words[i], ltp_result.tags[i]
        for i in range(len(ltp_result.arcs)):
            if ltp_result.arcs[i].head == ltp_result.length:
                print 'ROOT', "--", ltp_result.arcs[i].relation, '--',\
                ltp_result.words[i], '(', ltp_result.tags[i], ')'
            else:
                print ltp_result.words[ltp_result.arcs[i].head], '(', \
                ltp_result.tags[ltp_result.arcs[i].head], ')', "--", \
                ltp_result.arcs[i].relation, '--', ltp_result.words[i],\
                '(', ltp_result.tags[i], ')'

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
        self.title = []
        self.root = None
        idx = 0
        for tag, arc, word in zip(ltp_result.tags, ltp_result.arcs, ltp_result.words):
            node = Node(idx, tag, arc, word)
            self.nodes.append(node)
            idx += 1            
        for node, arc in zip(self.nodes, ltp_result.arcs):
            father_idx = arc.head
            if father_idx == self.length:
                self.root = node
                continue
            node.father = self.nodes[father_idx]
            self.nodes[father_idx].children.append(node)
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
        self.entity = None
        self.mark = []
        self.actual_sub = []
        self.concept_sub = []
        self.direct_sub = []
        self.obj = []
        self.att = []
        self.target = []
        self.depth = -1
        self.children = []
        self.search_sub_mark = False
        self.search_obj_mark = False
        self.title = None
        self.environment = []

    def search_depth(self):
        if self.depth != -1:
            pass
        elif self.father is None:
            self.depth = 0
        else:
            self.depth = self.father.search_depth() + 1
        return self.depth
    
if __name__ == "__main__":
    ltp = LTP(None)
    sentence = '1982年，刘德华参演许鞍华指导的影片《怒海》，从此走上了演艺之路。'
    ltp_result = ltp.parse(sentence)
    info = PrintInfo()
    info.print_ltp(ltp_result)
    tree = ParseTree(ltp_result)
    for node in tree.nodes:
        for child in node.children:
            print node.word, "children:", child.word