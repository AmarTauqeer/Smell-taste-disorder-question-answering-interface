from typing import Tuple


class Graph:

    def __init__(self):
        self.node_neighbors = {}  # Pairing: Node to Neighbors
        self.edge_attr = {}
        self.node_attr = {}
        self.triplets = None
        self.id = None
        self.linearQg = None

    def get_edge_vec(self, edge: Tuple[str, str]):
        return self.edge_attr.get(edge)['vec']

    def get_node_vec(self, node: str):
        return self.node_attr.get(node)['vec']

    def get_edge_label(self, edge: Tuple[str, str]):
        return self.edge_attr.get(edge)['label']

    def get_node_label(self, node: str):
        return self.node_attr.get(node)['label']

    def get_edges_for_node(self, node: str):
        edge_list = []
        for e in self.edges():
            if node in e:
                edge_list.append(e)
        return edge_list

    def nodes(self):
        return list(self.node_neighbors.keys())

    def neighbors(self, node):
        return list(self.node_neighbors[node])

    def edges(self):
        return [a for a in self.edge_attr.keys()]

    def has_node(self, node):
        return node in self.node_neighbors

    def add_node(self, node: str, label='', vec=None):
        if vec is None:
            vec = []
        if not node in self.node_neighbors:
            self.node_neighbors[node] = set()
            self.node_attr[node] = {"label": label, "vec": vec}

    # edge consists of (node_id, node_id)
    def add_edge(self, edge: Tuple[str, str], label='', vec=None, uri=""):
        if vec is None:
            vec = []
        u, v = edge
        if v not in self.node_neighbors[u] and u not in self.node_neighbors[v]:
            self.node_neighbors[u].add(v)
            if u != v:
                self.node_neighbors[v].add(u)
            self.edge_attr[(u, v)] = {"label": label, "vec": vec, "uri": uri}

    def del_node(self, node: str):
        for each in list(self.neighbors(node)):
            if (each != node):
                self.del_edge((each, node))
        del (self.node_neighbors[node])
        del (self.node_attr[node])

    def del_edge(self, edge: Tuple[str, str]):
        u, v = edge
        self.node_neighbors[u].remove(v)
        self.del_edge_labeling((u, v))
        if (u != v):
            self.node_neighbors[v].remove(u)
            self.del_edge_labeling((v, u))

    def has_edge(self, edge: Tuple[str, str]):
        u, v = edge
        return (u, v) in self.edge_attr and (v, u) in self.edge_attr

    def node_order(self, node: str):
        return len(self.neighbors(node))

    def del_edge_labeling(self, edge):
        self.edge_attr[edge].remove()

    def get_dash_graph(self, nr_of_displayed_nodes):
        nodes = []
        inserted_nodes = set()
        current_nr = 0
        for v in self.node_neighbors:
            if current_nr > nr_of_displayed_nodes:
                break
            nodes.append({'data': {'id': v, 'label': self.node_attr[v]['label']}})
            inserted_nodes.add(v)
            current_nr += 1

        for e in self.edge_attr:
            # print("e[0] {} e[1] {} self.edge_attr[e] {}".format(e[0],e[1],self.edge_attr[e]))
            if e[0] in inserted_nodes and e[1] in inserted_nodes:
                nodes.append({'data': {'source': e[0], 'target': e[1], 'label': self.edge_attr[e]['label'], 'uri': self.edge_attr[e]['uri']}})
        return nodes
