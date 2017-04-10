#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Neo4j Adapter.

Nodes can have multiple labels
"""

import py2neo

class Neo4jAdapter:
    """
    @brief      Allows creating and merging nodes on a neo4j instance.
    
    @param[(in)] label  The random seed for this session is used to label all nodes
                        of the graph. Since neo4j allowd 1 graph DB per instance, it
                        must be shared with many graphs.
    """
    def __init__(self, label, host='localhost', port=7474, user='neo4j', passwd=''):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self._graph = None
        self.label = label

    """
    @brief      This is the py2neo Graph object.
    """
    @property
    def graph(self):
        return self._graph

    def connect(self, watch=False):
        self._graph = py2neo.database.Graph(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.passwd
        )
        if watch:
            py2neo.watch('neo4j.bolt')

class NeoNode:

#class NeoNode(py2neo.ogm.GraphObject):
    # __primary_label__ = "I"
    # gene = py2neo.ogm.Property("gene")
    # generation = py2neo.ogm.Property("gen")
    # fitness = py2neo.ogm.Property("fitness")
    # score = py2neo.ogm.Property("score")

    # parents = py2neo.ogm.RelatedFrom("NeoNode", "PARENT_OF")
    # mirror = py2neo.ogm.RelatedTo("NeoNode", "MIRROR")
    pass
    
class Evolve(py2neo.Relationship):
    pass

class ParentOf(py2neo.Relationship):
    pass

if __name__ == '__main__':
    import random
    SEED = 32423
    random.seed(SEED)
    neodb = Neo4jAdapter(str(SEED), passwd='kraken')
    neodb.connect()
    print('Labels')

    for label in neodb.graph.node_labels:
        print(label, neodb.graph.schema.get_indexes(label))
    print('\nRelationships')
    print(neodb.graph.relationship_types)

    i1 = py2neo.Node("I", gene = [1,2,3], gen = 0)
    i2 = py2neo.Node("I", gene = [1], gen = 4)
    i3 = py2neo.Node("I", gene = [4,3], gen = 0)

    r12 = Evolve(i1, i2); r12["gen"] = i2["gen"]
    r23 = ParentOf(i1, i3); r23["gen"] = i3["gen"]

    t = neodb.graph.begin()
    #list(map(t.merge, [i1, i2, i3, r12, r23]))
    t.merge(i1| i2| i3| r12| r23)
    t.commit()
    c = neodb.graph.find("I")
    result = list(c)
    print(type(result),'\n', result)
