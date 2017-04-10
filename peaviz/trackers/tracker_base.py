#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Track evolution dynamics like individual interactions, fitness statistics. This
information is used to create the Complex Network.

As long as DEAP individuals remember their concrete ID, this should work :)
"""

class PEAvizTrackerAttributeError(TypeError):
    """
    Supplied attribute is not of expected type (list, dict) or in case of list
    is of incorrect size
    """

class TrackerBase:

    MIRROR_TAG = 'EVOLVE'
    PARENT_TAG = 'PARENT_OF'

    def __init__(self, adapterClass, **kwargs):
        """
        @brief      Constructs the object.
        
        @param      adapterClass  The adapter class to use
        @param      kwargs        The arguments to the adapter class constructor
        """
        self.adapter = adapterClass(**kwargs)

    def deploy(self, individual, gen=0):
        """
        @brief      Creates a binding uusing the Adapter to a concrete Node
                    object.
        
        @param      individual  The individual (DEAP objects are usually the genes) is set as the **gene**
        @param      gen         The generation in which the individual was created.
        
        @return     The **concrete ID** of this individual.
        """
        concreteID = self.adapter.add_node(
            gene = individual,
            gen  = gen)
        return concreteID

    def updateFitness(self, indID, fitness):
        """
        @brief      Used to update/set fitness of an individual that has been
                    **deployed**.
        
        @param      indID    The individual ID
        @param      fitness  The new fitness
        """
        self.adapter.update_fitness(indID, fitness)

    def setParents(self, childID, parentIDs, gen, otherAttrs):
        """
        @brief      Inserts PARENT_OF edges between the parents and child.
        
        @param      childID     The child ID
        @param      parentIDs   The parent IDs (``list``)
        @param      otherAttrs  The attributes of the edges. This must be a
                                ``list`` of ``dict``s or a single ``dict``. If
                                ``list`` then otherAttrs are set per edge in
                                same order as in ``parentIDs`` else, the single
                                ``dict`` is applied to both edges.
        
        @return     Returns _concrete IDs_ of the edges.
        """
        if type(otherAttrs) == dict:
            _otherAttrs = [otherAttrs]*len(parentIDs)
        elif type(otherAttrs) == list:
            _otherAttrs = otherAttrs
        else:
            raise PEAvizTrackerAttributeError()

        edgeIDs = []
        for parentID, otherAttr in zip(parentIDs, _otherAttrs):
            edgeID = self.add_edge(TrackerBase.PARENT_TAG, parentID, childID, gen, otherAttr)
            edgeIDs.append(edgeID)
        return edgeIDs

    def checkAndAddMirror(self, newID, individual, gen, otherAttrs):
        """
        @brief      Checks with adapter if this individual already exists. If
                    so, adds an appropriate edge to maintain the chain of EVOLVE nodes.
        
        @param      newID       The new id
        @param      individual  The individual
        @param      gen         The generation
        @param      otherAttrs  The attributes
        
        @return     Edge ID if an edge was added, else None
        """
        oldID = self.adapter.fetchIndivdual(individual)
        if oldID is not None:
            lastID = self.adapter.walk_edge(MIRROR_TAG, oldID)
            edgeID = self.add_edge(TrackerBase.MIRROR_TAG, lastID, newID, otherAttrs)
            return edgeID
        else:
            return None

    def add_edge(self, TAG, srcID, destID, gen, attrs):
        attrs['gen'] = gen
        return self.adapter.add_edge(TAG, srcID, destID, attrs)

    def getRawNode(self, indID):
        return self.adapter.getNode(indID)

    def getRawEdge(self, edgeID):
        return self.adapter.getEdge(edgeID)

    def save(self):
        file_location = self.adapter.save()
        print('GRAPH SAVED TO:', file_location)
