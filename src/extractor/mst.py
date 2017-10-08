class Edge:
    def __init__(self, u, v, w, eid):
        self.u = u
        self.v = v
        self.w = w
        self.eid = eid

def get_father(u, father_map):
    u_father = father_map[u]
    if u_father == u:
        return u
    u_father = get_father(u_father, father_map)
    father_map[u] = u_father
    return u_father
        
def perform_MST(edges):
    father_map = {}
    for e in edges:
        father_map[e.u] = e.u
        father_map[e.v] = e.v   

    edges.sort(key = lambda x: x.w, reverse = True)

    mst_edges = []
    for e in edges:
        u = e.u
        v = e.v
        u_father = get_father(u, father_map)
        v_father = get_father(v, father_map)
        if u_father != v_father:
            mst_edges.append(e)
            father_map[u_father] = v_father

    return mst_edges

if __name__ == "__main__":
    edges = [
        Edge(1, 2, 10, -1),
        Edge(1, 5, 2, -3),
        Edge(2, 5, 3, -2),
        
        Edge(2, 7, -1, -10)
    ]

    edges = mst(edges)
    for e in edges:
        print e.w, e.eid

    
