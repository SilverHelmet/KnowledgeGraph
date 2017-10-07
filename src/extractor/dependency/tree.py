#encoding: utf-8
from ..ltp import LTP
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



if __name__ == "__main__":
    ltp = LTP(None)
    sentence = '《忘情水》是刘德华演唱的一首歌曲，由陈耀川作曲、李安修作词，收录在刘德华1994年推出的同名专辑《忘情水》中。'
    ltp_result = ltp.parse(sentence)

    tree = ParseTree(ltp_result)
    path1, path2 = tree.find_path(1, 4)
    for node in path1:
        print "%s -%s-" %(node.word, node.rel)
    print ""
    for node in path2:
        print "%s -%s-" %(node.word, node.rel)
    
