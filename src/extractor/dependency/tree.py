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
class RelationExtractor:
    def __init__(self):
        pass
      
    def find_path_to_root(self, node):
        path = [node]
        while node.father != None:
            node = node.father
            path.append(node)
        return path
    
    def find_index(self, tree, word):
        unigram = []
        bigram = []
        trigram = []
        quagram = []
        fifgram = []
        sixgram = []
        lens = tree.length
        for i in range(lens):
            unigram.append(tree.nodes[i].word)
        for i in range(lens - 1):
            bigram.append(''.join(unigram[i : i + 2]))
        for i in range(lens - 2):
            trigram.append(''.join(unigram[i : i + 3]))
        for i in range(lens - 3):
            quagram.append(''.join(unigram[i : i + 4]))
        for i in range(lens - 4):
            fifgram.append(''.join(unigram[i : i + 5]))
        for i in range(lens - 5):
            sixgram.append(''.join(unigram[i : i + 6]))
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
        elif word in sixgram:
            return [6, sixgram.index(word)]
        else:
            return [0, None]
        
    def find_coo_father(self, tree, lis):
        if lis[0] == 0:
            return -1
        else:
            lens = lis[0]
            st_index = lis[1]
            words = []
            for i in range(lens):
                words.append(tree.nodes[st_index + i])
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
        
    def find_path_verbs(self, ltp_result, e1, e2, entity_pool):
        tree = ParseTree(ltp_result)
        word1 = word2 = ''
        for i in range(e1.st, e1.ed):
            word1 += tree.nodes[i].word
        for i in range(e2.st, e2.ed):
            word2 += tree.nodes[i].word
        w1 = self.find_coo_father(tree, self.find_index(tree, word1))
        w2 = self.find_coo_father(tree, self.find_index(tree, word2))
        simple_res = []
        if w1 == -1:
            print word1, "not recognized!"
        if w2 == -1:
            print word2, "not recognized!"
        else:
            p1 = self.find_path_to_root(tree.nodes[w1])
            p2 = self.find_path_to_root(tree.nodes[w2])
            coo_p = p1 + p2[:-1]
            for node in coo_p:
                if node.postag == 'v':
                    if entity_pool[node.idx] == 1:
                        print node.word,": extract verb is an entity! error!"
                    else:
                        simple_res.append([(node.idx, node.idx + 1)])
        return simple_res
    
class prenode:
    def __init__(self, st, ed):
        self.st = st
        self.ed = ed
        
if __name__ == "__main__":
    ltp = LTP(None)
    sentence = '《冰与火之歌》(A Song of Ice and Fire)是由美国作家乔治·R·R·马丁所著的严肃奇幻小说系列。'
    ltp_result = ltp.parse(sentence)
    for i in range(ltp_result.length):
        print i, ":", ltp_result.words[i]
    e1 = prenode(1, 6)
    e2 = prenode(17, 18)
    entity_pool = [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    res = RelationExtractor()
    tmp = res.find_path_verbs(ltp_result, e1, e2, entity_pool)
    print tmp
    '''
    simple_res = SimpleExtract(ltp_result, e1, e2, entity_pool)
    print '*' * 25
    print "simple res :"
    for i in range(len(simple_res)):
        print "verb", i, ":", tree.nodes[simple_res[i][0]].word
    '''