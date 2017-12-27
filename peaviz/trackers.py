from peaviz.exceptions import PEAvizTrackerAttributeError

"""
Track evolution dynamics like interactions between individuals, fitness
statistics. This information is used to create the Complex Network.

A :mod:`tracker <peaviz.trackers>` connects with one or more
:mod:`~peaviz.adapters` and
provides a clean interface for tracking of *all* GA programs.

Trackers must:

#. Connect to one of the :mod:`~peaviz.adapters`
#. Bind an individual of the population with the adapter's data structure using
   a (unique) ``integer`` ID.
#. Provide a means to update an individual's
    - fitness vector
    - score
    - parents
#. Provide access the adapter's underlying ``node`` and ``edge``
   objects.
#. Provide a method to save/commit the network in/of the adapter to a
   persistent storage

Todo:
    #. Must allow connection with multiple adapters!
    #. Make definition in glossary for ``fitness``, ``score``.
    #. Expose multiple raw nodes which all represent the same individual.
    #. :strike:`This ain't no base class!`
"""

class TrackerBasic:
    """
    This simple tracker is implemented for the :ref:`default_enc_strategy`.
    """

    #: ``EVOLVE`` Edge type.
    MIRROR_TAG = 'EVOLVE'
    #: ``PARENT_OF`` Edge type.
    PARENT_TAG = 'PARENT_OF'
    __attrs__ = ['adapter']

    def __init__(self, adapter_class, **kwargs):
        """
        **Constructor**

        Args:
            adapter_class (peaviz.adapters.AdapterBase) : The adapter class to
            use with the Tracker
        Keyword Args:
            kwargs: Passed directly to the constructor of ``adapter_class``.
        """

        #:  A concrete implementation of the
        #: :class:`~peaviz.adapters.AdapterBase` interface.
        #:
        #: #. peaviz.adapters.GraphAdapter
        #: #. peaviz.adapters.Neo4jAdapter
        self.adapter = adapter_class(**kwargs)

    def deploy(self, individual, gen=0):
        """
        Binds this ``individual`` with the :attr:`adapter`.

        Args:
            individual: The individual created using the
                    :func:`deap.creator.create() <deap:deap.creator.create>`.
            gen (int):  The generation in which the individual was created.
        Returns:
            int: The (unique) concrete ID of this individual.
        Todo:
            Not every generated individual must be added to the graph ASAP.
        """
        concrete_id = self.adapter.add_node(
            gene=individual,
            gen=gen)
        return concrete_id

    def update_fitness(self, ind_id, fitness):
        r"""
        Used to update/set fitness of an individual that has been
        "\ :meth:`~peaviz.trackers.TrackerBasic.deploy`\ ed".

        Args:
            ind_id (int): The individual (concrete) ID.
            fitness (object): The new fitness.
        Todo:
            Link ``fitness`` from glossary.
        """
        self.adapter.update_fitness(ind_id, fitness)

    def update_score(self, ind_id, score):
        r"""
        Used to update/set fitness of an individual that has been
        "\ :meth:`~peaviz.trackers.TrackerBasic.deploy`\ ed".

        Args:
            ind_id (int): The individual (concrete) ID.
            score (float or int): The new score.
        Todo:
            Link ``score`` from glossary.
        """
        self.adapter.update_score(ind_id, score)

    def set_parents(self, child_id, parent_ids, gen, other_attrs={}):
        """
        Inserts ``PARENT_OF`` edges between the parents and child.

        Args:
            child_id (int): The child ID
            parent_ids (int): The parent IDs (``list``)
            other_attrs: Any other attributes of the edges.

        :type other_attrs: list(dict) or dict

        Note:
            ``other_attrs`` can be used in two ways,

            #. If both edges must have the same attributes, just pass in a
               single dict.
            #. Else provide a list(dict) with dicts in order corresponding to
               the order in ``parent_ids``.
        Returns:
            int: *Concrete* IDs of the edges.
        Raises:
            ~peaviz.exceptions.PEAvizTrackerAttributeError:
                If ``other_attrs`` is of wrong type and/or length.
        """
        if isinstance(other_attrs, dict):
            _other_attrs = [other_attrs]*len(parent_ids)
        elif isinstance(other_attrs, list):
            _other_attrs = other_attrs
        else:
            raise PEAvizTrackerAttributeError()

        edge_ids = []
        for parent_id, other_attr in zip(parent_ids, _other_attrs):
            edge_id = self.add_edge(TrackerBasic.PARENT_TAG,
                                    parent_id,
                                    child_id,
                                    gen,
                                    other_attr)
            edge_ids.append(edge_id)
        return edge_ids

    def check_and_add_mirror(self, new_id, individual, gen, attrs):
        """
        .. warning:: *This method is deprecated?*


        Use this method to insert new individuals into the graph.

        As noted :red:`here`, the generated individual might already exist in
        the graph.

        Todo:
            Remove this along with other ``EVOLVE`` edge crap.

        Args:
            new_id (int): The new id
            individual (int): The individual
            gen (int): The generation
            attrs (dict): Any other attributes for the edge.
        Returns:
            int: *Concrete* ID of the inserted edge, if one was added, else
                 None.
        """
        old_id = self.adapter.get_indivdual(individual)
        if old_id is not None:
            last_id = self.adapter.walk_edge(TrackerBasic.MIRROR_TAG, old_id)
            edge_id = self.add_edge(TrackerBasic.MIRROR_TAG,
                                    last_id,
                                    new_id,
                                    gen,
                                    attrs)
            return edge_id
        else:
            return None

    def add_edge(self, tag, src_id, dest_id, gen, attrs):
        """
        Adds an edge between source and destination individuals of type
        ``tag``.

        Todo:
            Remove ``EVOLVE``.

        Args:
            tag (str): The type of edge, ``PARENT_OF`` or ``EVOLVE``.
            src_id (int): The *concrete* ID of the source individual.
            dest_id (int): The *concrete* ID of the destination individual.
            gen (int): The current generation.
            attrs (dict): Any other attributes for the edge.
        Returns:
            int: *Concrete* ID of the inserted edge.
        """
        attrs['gen'] = gen
        return self.adapter.add_edge(tag, src_id, dest_id, attrs)

    def get_raw_node(self, ind_id):
        """
        Args:
            ind_id (int): The *concrete* ID of the individual.

        .. tip::
            There might be multiple nodes encoding the same individual.

        Returns:
            object: The :attr:`~peaviz.trackers.TrackerBasic.adapter`'s
            underlying ``Node`` object.
        """
        return self.adapter.get_node(ind_id)

    def get_raw_edge(self, edge_id):
        """
        Args:
            edge_id (int): The *concrete* ID of the edge.
        Returns:
            object: The :attr:`~peaviz.trackers.TrackerBasic.adapter`'s
            underlying ``Edge`` object.
        """
        return self.adapter.get_edge(edge_id)

    def save(self):
        """
        Save the :attr:`adapter`'s network/graph representation to persistent
        storage and/or close any resources used by the :attr:`adapter`.
        """
        file_location = self.adapter.save()
        print('GRAPH SAVED TO:', file_location)

    def num_nodes(self):
        """
        Returns:
            int: The number of nodes in the :attr:`adapter`'s network/graph
            representation.
        Note:
            This is not the same as number of individuals evaluated/
            generated by the GA.
        """
        return self.adapter.num_nodes()
