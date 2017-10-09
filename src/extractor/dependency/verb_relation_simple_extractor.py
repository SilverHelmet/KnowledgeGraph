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
    
    def find_relation(self, ltp_result, e1, e2, entity_pool):
        simple_res = []
        p1, p2 = self.find_entity_path(ltp_result, e1, e2, entity_pool)
        coo_p = p1 + p2[:-1]
        for node in coo_p:
            if node.postag == 'v':
                if entity_pool[node.idx] == 1:
                    self.debuger.debug('found verb', ltp_result.words[res[0]] ,'is an entity! error!')
                    pass
                else:
                    simple_res.append((node.idx, node.idx + 1))
        return simple_res

if __name__ == "__main__":
    ltp = LTP(None)
    sentence = '1982年，刘德华参演许鞍华指导的影片《怒海》，从此走上了演艺之路。'
    ltp_result = ltp.parse(sentence)
    info = PrintInfo()
    info.print_ltp(ltp_result)
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