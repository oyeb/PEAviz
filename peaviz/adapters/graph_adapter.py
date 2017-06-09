import os.path
from graph_tool import Graph
from peaviz.exceptions import PEAvizAdapterAttributeError

class GraphAdapter:
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

    def add_node(self, gene, gen=0, attrs=None):
        vertex = self.graph.add_vertex()
        self.graph.vp.gene[vertex] = gene
        self.graph.vp.gen[vertex] = gen
        self.set_props(vertex, attrs)

        return self.graph.vertex_index[vertex]

    def add_edge(self, tag, src_id, dest_id, attrs=None):
        edge = self.graph.add_edge(src_id, dest_id)
        self.graph.ep.label[edge] = tag
        if attrs is None:
            pass
        elif isinstance(attrs, dict):
            #: .. todo:: Very slow loop :(
            for key in attrs:
                self.graph.ep[key][edge] = attrs[key]
        else:
            raise PEAvizAdapterAttributeError()
        return self.graph.edge_index[edge]

    def get_node(self, node_id):
        return self.graph.vertex(node_id)

    def get_edge(self, edge_id):
        return self.graph.edge(edge_id)

    def get_individual(self, gene):
        targets = graph_tool.util.find_vertex(self.graph, self.graph.vp.gene, gene)
        # find the last node, the one with highest `gen`
        if targets is not None:
            # guaranteed to be in order!!
            return self.graph.vertex_index[targets[-1]]
        else:
            return None

    def walk_edge(self, tag, start_id):
        pass

    def update_fitness(self, node_id, fitness):
        vertex = self.graph.vertex(node_id)
        self.set_props(vertex, {'fitness' : fitness})

    def update_score(self, node_id, score):
        vertex = self.graph.vertex(node_id)
        self.set_props(vertex, {'score' : score})

    def set_props(self, vertex, attrs):
        if attrs is None:
            return
        elif isinstance(attrs, dict):
            for key in attrs:
                self.graph.vp[key][vertex] = attrs[key]
        else:
            raise PEAvizAdapterAttributeError()

    def save(self):
        filename = os.path.join('graphs', self.name) + '.' + self.file_extension
        self.graph.save(filename)
        return filename

    def num_nodes(self):
        return self.graph.num_vertices()
