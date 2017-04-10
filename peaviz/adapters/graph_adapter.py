from .adapter_base import AdapterBase
from graph_tool import Graph, Vertex, Edge
import os.path

class GraphAdapter(AdapterBase):
    def __init__(self, seed_str, name,
        file_extension='gml',
        vertex_schema={
            'gene'    : 'vector<bool>',
            'gen'     : 'int',
            'fitness' : 'vector<long>',
            'score'   : 'long'
        },
        edge_schema={
            'label' : 'string',
            'gen'   : 'int'
        }):

        self.seed = seed_str
        self.name = name
        self.file_extension = file_extension
        self.graph = Graph()

        # Create graph properties
        self.graph.gp.labels = self.graph.new_gp('vector<string>')
        self.graph.gp.labels = [seed_str]

        self.graph.gp.name = self.graph.new_gp('string')
        self.graph.gp.name = self.name

        # Create vertex properties
        for key in vertex_schema:
            self.graph.vp[key] = self.graph.new_vp(vertex_schema[key])

        # Create edge properties
        for key in edge_schema:
            self.graph.ep[key] = self.graph.new_ep(edge_schema[key])

    def add_node(self, gene, gen=0, attrs={}):
        v = self.graph.add_vertex()
        self.graph.vp.gene[v] = gene
        self.graph.vp.gen[v]  = gen
        self.set_props(v, attrs)

        return self.graph.vertex_index[v]

    def add_edge(self, TAG, srcID, destID, attrs={}):
        e = self.graph.add_edge(srcID, destID)
        self.graph.ep.label[e] = TAG
        for key in attrs:
            self.graph.ep[key][e] = attrs[key]
        return self.graph.edge_index[e]
            
    def getNode(self, nodeID):
        return self.graph.vertex(nodeID)

    def getEdge(self, edgeID):
        return self.graph.edge(edgeID)

    def fetchIndividual(self, individual):
        targets = graph_tool.util.find_vertex(self.graph, self.graph.vp.gene, individual)
        # find the last node, the one with highest `gen`
        if targets:
            # guaranteed to be in order!!
            return self.graph.vertex_index[targets[-1]]
        else:
            return None

    def walk_edge(self, TAG, startID):
        pass

    def update_fitness(self, nodeID, fitness):
        v = self.graph.vertex(nodeID)
        self.set_props(v, {'fitness' : fitness})

    def update_score(self, nodeID, score):
        v = self.graph.vertex(nodeID)
        self.set_props(v, {'score' : score})

    def set_props(self, v, attrs):
        for key in attrs:
            self.graph.vp[key][v] = attrs[key]

    def save(self):
        filename = os.path.join('graphs', self.name) + '.' + self.file_extension
        self.graph.save(filename)
        return filename
