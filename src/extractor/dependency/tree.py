#encoding: utf-8
from ..ltp import LTP, LTPResult
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
                self.root = Node
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
    def find_path_to_root(self, node):
        path = [node]
        while node.father != None:
            node = node.father
            path.append(node)
        return path
    def find_index(self, word):
        unigram = []
        bigram = []
        trigram = []
        quagram = []
        fifgram = []
        for i in range(self.length):
            unigram.append(self.nodes[i].word)
        for i in range(self.length - 1):
            bigram.append(''.join(unigram[i : i + 2]))
        for i in range(self.length - 2):
            trigram.append(''.join(unigram[i : i + 3]))
        for i in range(self.length - 3):
            quagram.append(''.join(unigram[i : i + 4]))
        for i in range(self.length - 4):
           	fifgram.append(''.join(unigram[i : i + 5]))
        if word in unigram:
            return [1, unigram.index(word)]
        elif word in bigram:
            return [2, bigram.index(word)]
        elif word in trigram:
            return [3, trigram.index(word)]
        elif word in quagram:
            return [4, quagram.index(word)]
        elif word in fifgram:
            return [5, fifgram.index(word)]
        else:
            return [0, None]
        
    def find_coo_father(self, lis):
        if lis[0] == 0:
            return -1
        else:
            lens = lis[0]
            st_index = lis[1]
            words = []
            for i in range(lens):
                words.append(self.nodes[st_index + i])
            coo_father = []
            final_res = []
            res = []
            for i in range(lens):
                coo_father.append(self.find_path_to_root(words[i]))
            process_father = []
            for i in range(lens):
                process_father.append([])
                for j in range(len(coo_father[i])):
                    process_father[i].append(coo_father[i][j].idx)
            index_father = []
            for i in range(lens):
                index_father += process_father[i]
            father = set(index_father)
            for num in father:
                if(index_father.count(num) == lens):
                    final_res.append(num)
            for i in final_res:
                res.append(process_father[0].index(i))
            return process_father[0][min(res)]
        
    def find_path_verbs(self, word1, word2):
        w1 = self.find_coo_father(self.find_index(word1))
        w2 = self.find_coo_father(self.find_index(word2))
        res = []
        if w1 == -1:
            print word1, "not recognized!"
        if w2 == -2:
            print word2, "not recognized!"
        else:
            p1, p2 = self.find_path(w1, w2)
            p_all = p1 + p2[:-1]
            for p in p_all:
                if p.postag == 'v':
                    res.append(p.word)
        return res
        
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
    path_verbs = tree.find_path_verbs( "同名专辑", "一首歌曲")
    for i in range(len(path_verbs)):
        print "verb",i,":", path_verbs[i]
    tree.find_index("一首歌曲")
    path1, path2 = tree.find_path(1, 4)
    for node in path1:
        print "%s -%s- %s" %(node.word, node.rel, node.postag)
    print ""
    for node in path2:
        print "%s -%s- %s" %(node.word, node.rel, node.postag)
    
