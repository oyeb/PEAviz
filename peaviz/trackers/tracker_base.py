#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PEAvizTrackerAttributeError(TypeError):
    """
    Supplied attribute is not of type (``list`` or ``dict``) or the ``list``
    is of incorrect size.
    """

class TrackerBase:
    """
    A tracker connects with one or multiple adapters and this super class
    provides a clean, unified interface for tracking of all GA programs.

    Trackers must:
    
    #. Bind an individual of the population with the :attr:`adapter`'s data 
       structure using a (unique) ``integer`` ID.
    #. Provide a means to update an individual's

        - fitness vector
        - score
        - parents
    #. Provide access the :attr:`adapter`'s underlying ``node`` and ``edge``
       objects.
    #. Provide a method to save/commit the network in/of the :attr:`adapter` to a
       persistent storage

    Todo:
        #. :red:`This ain't no base class!`
        #. Must allow connection with multiple adapters!
        #. Make definition in glossary for ``fitness``, ``score``.
        #. Expose multiple raw nodes which all represent the same individual.
    """

    #: ``EVOLVE`` Edge type.
    MIRROR_TAG = 'EVOLVE'
    #: ``PARENT_OF`` Edge type.
    PARENT_TAG = 'PARENT_OF'

    __attrs__ = ['adapter']

    def __init__(self, adapterClass, **kwargs):
        """
        **Constructor**

        Args:
            adapterClass (peaviz.adapters.AdapterBase) : The adapter class to use with the Tracker
        Keyword Args: 
            kwargs: Passed directly to the constructor of ``adapterClass``.
        """

        #:  A concrete implementation of the
        #: :class:`~peaviz.adapters.AdapterBase` interface.
        #:
        #: #. peaviz.adapters.GraphAdapter
        #: #. peaviz.adapters.Neo4jAdapter
        self.adapter = adapterClass(**kwargs)

    def deploy(self, individual, gen=0):
        """
        Binds this ``individual`` with the :attr:`adapter`.
        
        Args:
            individual: The individual created using the :func:`deap.creator.create() <deap:deap.creator.create>`.
            gen (int):  The generation in which the individual was created.
        
        Returns:
            int: The (unique) concrete ID of this individual.
        """
        concreteID = self.adapter.add_node(
            gene = individual,
            gen  = gen)
        return concreteID

    def updateFitness(self, indID, fitness):
        """
        Used to update/set fitness of an individual that has been 
        "\ :meth:`~peaviz.trackers.TrackerBase.deploy`\ ed".
        
        Args:
            indID (int): The individual (concrete) ID.
            fitness: The new fitness.

        Todo:
            Link ``fitness`` from glossary.
        """
        self.adapter.update_fitness(indID, fitness)

    def updateScore(self, indID, score):
        """
        Used to update/set fitness of an individual that has been
        "\ :meth:`~peaviz.trackers.TrackerBase.deploy`\ ed".
        
        Args:
            indID (int): The individual (concrete) ID.
            fitness: The new score.

        Todo:
            Link ``score`` from glossary.
        """
        self.adapter.update_score(indID, score)

    def setParents(self, childID, parentIDs, gen, otherAttrs={}):
        """
        Inserts ``PARENT_OF`` edges between the parents and child.
        
        Args:
            childID (int): The child ID
            parentIDs (int): The parent IDs (``list``)
            otherAttrs: The attributes of the edges

        :type otherAttrs: list(dict) or dict
        
        Note:
            ``otherAttrs`` can be used in two ways,

            #. If both edges must have the same attributes, just pass in a single dict.
            #. Else provide a list(dict) with dicts in order corresponding to
               the order in ``parentIDs``.
        
        Returns:
            int: *Concrete* IDs of the edges.
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

    def checkAndAddMirror(self, newID, individual, gen, attrs):
        """
        .. warning:: *This method is deprecated?*


        Use this method to insert new individuals into the graph.

        As noted :red:`here`, the generated individual might already exist in
        the graph.

        Todo:
            Remove this along with other ``EVOLVE`` edge crap.

        Args:        
            newID (int): The new id
            individual (int): The individual
            gen (int): The generation
            attrs (dict): Any other attributes for the edge.
        
        Returns:
            int: *Concrete* ID of the inserted edge, if one was added, else None.
        """
        oldID = self.adapter.fetchIndivdual(individual)
        if oldID is not None:
            lastID = self.adapter.walk_edge(MIRROR_TAG, oldID)
            edgeID = self.add_edge(TrackerBase.MIRROR_TAG, lastID, newID, otherAttrs)
            return edgeID
        else:
            return None

    def add_edge(self, TAG, srcID, destID, gen, attrs):
        """
        Adds an edge between source and destination individuals of type
        ``TAG``.

        Todo:
            Remove ``EVOLVE``.

        Args:
            TAG (str): The type of edge, ``PARENT_OF`` or ``EVOLVE``.
            srcID (int): The *concrete* ID of the source individual.
            destID (int): The *concrete* ID of the destination individual.
            gen (int): The current generation.
            attrs (dict): Any other attributes for the edge.
        
        Returns:
            int: *Concrete* ID of the inserted edge.
        """
        attrs['gen'] = gen
        return self.adapter.add_edge(TAG, srcID, destID, attrs)

    def getRawNode(self, indID):
        """        
        Args:
            indID (int): The *concrete* ID of the individual.

        .. tip::
            There might be multiple nodes encoding the same individual.

        Returns:
            object: The :attr:`adapter <peaviz.trackers.TrackerBase.adapter>`'s
            underlying ``Node`` object.
        """
        return self.adapter.getNode(indID)

    def getRawEdge(self, edgeID):
        """
        Args:
            edgeID (int): The *concrete* ID of the edge.

        Returns:
            object: The :attr:`adapter <peaviz.trackers.TrackerBase.adapter>`'s
            underlying ``Edge`` object.
        """
        return self.adapter.getEdge(edgeID)

    def save(self):
        """
        Save the :attr:`adapter`'s network/graph representation to persistent 
        storage and/or close any resources used by the :attr:`adapter`.
        """
        file_location = self.adapter.save()
        print('GRAPH SAVED TO:', file_location)

    def numNodes(self):
        """
        Returns:
            int: The number of nodes in the :attr:`adapter`'s network/graph
            representation.

        Note:
            This is not the same as number of individuals evaluated/
            generated by the GA.
        """
        return self.adapter.numNodes()
