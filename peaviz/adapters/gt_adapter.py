"""
The :mod:`~peaviz.adapters.gt_adapter` contains the
:class:`~peaviz.adapters.gt_adapter.GraphToolAdapter` and other utilities
required for its functioning.
"""

import os.path
import graph_tool.util
from graph_tool import Graph
from peaviz.exceptions import PEAvizAdapterAttributeError

class GraphToolAdapter:
    """
    This adapter uses the excellent :mod:`graph_tool` module's graph data
    structure for its operations.
    """
    def __init__(self, seed_string, name,
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

        #: In order to note different versions of graph generated for every
        #: execution, the seed for the :mod:`random` module is saved as an
        #: attribute of the :class:`~graph_tool.Graph`.
        self.seed = seed_string

        #: The (relative) path where the graph is saved.
        self.filename = name

        #: The file format to use.
        #:
        #: .. seealso::
        #:    ``graph-tool`` docs'
        #: `Graph IO <https://graph-tool.skewed.de/static/doc/quickstart.html#graph-i-o>`_
        #: and :meth:`graph_tool.Graph.save`.
        self.file_extension = file_extension
        self._graph = Graph()

        # Create graph properties
        self.graph.gp.labels = self.graph.new_graph_property('vector<string>')
        self.graph.gp.labels = [seed_string] # currently just the seed :/

        self.graph.gp.name = self.graph.new_graph_property('string')
        self.graph.gp.name = self.filename

        # Create vertex properties
        self._vertex_schema = vertex_schema
        self._edge_schema = edge_schema
        for key in vertex_schema:
            self.graph.vp[key] = self.graph.new_vertex_property(
                vertex_schema[key])

        # Create edge properties
        for key in edge_schema:
            self.graph.ep[key] = self.graph.new_edge_property(edge_schema[key])

    @property
    def graph(self):
        """
        The :class:`graph_tool.Graph` instance of this adapter.
        """
        return self._graph

    @property
    def vertex_schema(self):
        """
        The schema defines all attributes of a node in the graph.
        For example::

            vertex_schema = {
                 'gene'    : 'vector<bool>',
                 'gen'     : 'int',
                 'fitness' : 'vector<long>',
                 'score'   : 'long'
            }

        This will create 4 attributes with ``gene`` and ``fitness`` being
        arrays of ``booleans`` and ``long int`` respectively for all nodes.

        .. note:: This is the default schema.

        .. seealso::
           `graph-tool Quickstart <https://graph-tool.skewed.de/static/doc/quickstart.html#sec-property-maps>`_
           and :class:`graph_tool.PropertyMap`.
        """
        return self._vertex_schema

    @property
    def edge_schema(self):
        """
        The schema defines all attributes of an edge in the graph.
        For example::

            edge_schema={
                'label' : 'string',
                'gen'   : 'int'
            }

        This will create 2 attributes with ``gene`` and ``fitness`` being
        arrays of ``booleans`` and ``long int`` respectively for all edges.

        .. note:: This is the default schema.

        .. seealso::
           :attr:`vertex_schema`.
        """
        return self._edge_schema

    def add_node(self, gene, gen=0, attrs=None):
        """
        Adds a node, setting the ``gene`` and ``gen`` properties. The other
        properties are set using :meth:`update_fitness` and
        :meth:`update_score`.

        Args:
            gene (object): The gene
            gen (int): The generation in which this node is being inserted.
            attrs (dict or None): Any other attributes for this node

        Returns:
            int: The *concrete* ID of the inserted node.
        Raises:
            PEAvizAdapterAttributeError: If provided ``attrs`` is **neither**
            ``dict nor ``None``.
        """
        vertex = self.graph.add_vertex()
        self.graph.vp.gene[vertex] = gene
        self.graph.vp.gen[vertex] = gen
        set_props(self.graph.vp, vertex, attrs)
        return self.graph.vertex_index[vertex]

    def add_edge(self, tag, src_id, dest_id, attrs=None):
        """
        Adds a directed edge, setting the primary label as ``tag`` from node
        identified by ``src_id`` to the one identified by ``dest_id``.

        Args:
            gene (object): The gene
            tag (str): The gene
            src_id (int): The node identified by ``src_id``.
            dest_id (int): The node identified by ``dest_id``.
            attrs (dict or None): Any other attributes for this node

        Returns:
            int: The *concrete* ID of the inserted edge.
        Raises:
            PEAvizAdapterAttributeError: If provided ``attrs`` is **neither**
            ``dict nor ``None``.
        """
        edge = self.graph.add_edge(src_id, dest_id)
        self.graph.ep.label[edge] = tag
        set_props(self.graph.ep, edge, attrs)
        return self.graph.edge_index[edge]

    def get_node(self, node_id):
        """
        Args:
            node_id (int):  The *concrete* ID of the node to fetch.
        Returns:
            graph_tool.Vertex: The node.
        """
        return self.graph.vertex(node_id)

    def get_edge(self, edge_id):
        """
        Args:
            edge_id (int):  The *concrete* ID of the edge to fetch.
        Returns:
            graph_tool.Edge: The edge.
        """
        return self.graph.edge(edge_id)

    def get_individual(self, gene):
        """
        Fetches the :class:`~graph_tool.Vertex` which represents the given
        ``gene``.

        Args:
            gene (object): The ``gene``.
        Returns:
            graph_tool.Vertex: The node that represents the given
            ``gene``.

            .. tip:: In case of multiple nodes with the same ``gene``, the one
            inserted last is returned.
        """
        targets = graph_tool.util.find_vertex(self.graph,
                                              self.graph.vp.gene,
                                              gene)
        # find the last node, the one with highest `gen`
        if targets is not None:
            # guaranteed to be in order!!
            return self.graph.vertex_index[targets[-1]]
        else:
            return None

    def walk_edge(self, tag, start_id):
        """
        Traverse all nodes via edges with primary label as ``tag`` starting
        from the node identified by ``start_id`` till the node without any
        *out-edge* with label ``tag`` is reached and return it.

        Args:
            tag (str): The primary label of the edges which are to be
            traversed.
            start_id (int): The *concrete* ID of the node where the *walk* is
                            initiated.
        Returns:
            graph_tool.Vertex: The last :class:`~graph_tool.Vertex` that was
            *walked* upon.
        """
        pass

    def update_fitness(self, node_id, fitness):
        """
        Used to update/set fitness attribute of a node.

        Args:
            node_id (int): The individual (concrete) ID.
            fitness (object): The (new) fitness.
        Todo:
            Link ``fitness`` from glossary.
        """
        vertex = self.graph.vertex(node_id)
        set_props(self.graph.vp, vertex, {'fitness' : fitness})

    def update_score(self, node_id, score):
        """
        Used to update/set score attribute of a node.

        Args:
            node_id (int): The individual (concrete) ID.
            score (object): The (new) score.
        Todo:
            Link ``score`` from glossary.
        """
        vertex = self.graph.vertex(node_id)
        set_props(self.graph.vp, vertex, {'score' : score})

    def save(self):
        """
        Save the graph to a file of type :attr:`file_extension`

        Returns:
            str: Path to the saved file.
        """
        filename = os.path.join('graphs', self.filename) + '.%s' % self.file_extension
        self.graph.save(filename)
        return filename

    def num_nodes(self):
        """
        Returns:
            int: The number of nodes in the graph.
        Note:
            This is not the same as number of individuals evaluated/
            generated by the GA.
        """
        return self.graph.num_vertices()

def set_props(property_map, entity, attrs):
    """
    Saves the ``attrs`` in ``entity`` 's corresponding ``property_map``.

    Args:
        property_map (graph_tool.PropertyMap): The property map.
        entity (graph_tool.Vertex or graph_tool.Edge): The entity.
        attrs (dict or None): The attributes to save.
    """
    if attrs is None:
        return
    elif isinstance(attrs, dict):
        for key in attrs:
            property_map[key][entity] = attrs[key]
    else:
        raise PEAvizAdapterAttributeError()
