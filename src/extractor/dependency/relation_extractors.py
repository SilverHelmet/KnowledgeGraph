from ..structure import StrRelation

class RelTagExtractor:
    def __init__(self):
        pass

    def find_relation(self, ltp_result, e1, e2, entity_pool):
        rel_range_l = max(min(e1.st, e2.st) - 2, 0)
        rel_range_r = min(max(e1.ed, e2.ed) + 2, ltp_result.length)
        
        rels = []
        for idx in range(rel_range_l, rel_range_r):
            tag =  ltp_result.tags[idx]
            if entity_pool[idx]:
                continue
            if tag == 'v' or tag == 'n':
                rels.append((idx, idx + 1))
        return rels




