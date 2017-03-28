#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Track evolution dynamics like individual interactions, fitness statistics. This
information is used to create the Complex Network.
"""
import random
import gephistreamer.graph as graph
import gephistreamer.streamer as streamer

def compact_str(container):
	if type(container) in [list, tuple, set]:
		return "["+",".join(str(item) for item in container)+"]"
	else:
		return container # because it might not be a container...

class TrackerHub:
	"""
	@brief      Coordinates all trackers for a (sub) population.
	"""	
	def __init__(self, streamer=streamer.Streamer(streamer.GephiREST())):
		self.streamer = streamer
		self._bucket = {}

	@property
	def bucket(self):
		return self._bucket

	def register(self, tracker):
		try:
			self._bucket[tracker.index] = tracker
		except:
			raise RuntimeError("Tracker cannot be registered, it has no `identity`!")

	def emitNode(self, node):
		response = self.streamer.add_node(node)
		if response.status_code != 200:
			print("Gephi GraphStream error. [status=%d]" % response.status)
		return response

	def emitEdge(self, edge):
		response = self.streamer.add_edge(edge)
		if response.status_code != 200:
			print("Gephi GraphStream error. [status=%d]" % response.status)
		return response

	def __getitem__(self, tracker_index):
		return self.bucket.get(tracker_index, None)

	def __len__(self):
		return len(self.bucket)

class Tracker:
	_IND_COUNT = 0

	@property
	def hub(self):
		return self._hub
	@hub.setter
	def hub(self, newHub):
		self._hub = newHub

	@property
	def index(self):
		return self._index

	def __init__(self, hub=None, parents=tuple(), gen=0, fitness=tuple(), **kwargs):
		self._hub = hub
		self._index = None
		self.preset(parents, gen, fitness, **kwargs)

	def preset(self, parents=None, gen=0, fitness=None, **kwargs):
		self.parents = parents
		self.gen = gen
		self.fitness = fitness
		self.attributes = kwargs

	def setParents(self, parents, gen=None, transmit=True):
		assert(isinstance(parents[0], int))
		self.parents = parents
		if gen:
			self.gen = gen
		else:
			self.gen += 1
		if transmit:
			self.insertEdge()

	def insertNode(self, location=None, pop_size=500):
		x_extent = y_extent = pop_size
		attributes = {'gen'     : self.gen,
					  'fitness' : sum(self.fitness),
					  'parents' : compact_str(self.parents),
					  'x'       : random.randint(-x_extent, x_extent),
					  'y'       : random.randint(-y_extent, y_extent)
					 }
		if location is not None:
			if (type(location) in [tuple, list] and len(location) == 2):
				attributes['x'], attributes['y'] = location
			# else, the randomized coordinates which have been set already

		if self.attributes:
			# need to flatten attributes, GraphStream API rejects `actions` if
			# Node attribute-values are compound JSON types (like [] or {})
			for k in self.attributes:
				# this will (correctly) overwrite
				attributes.update(k, compact_str(self.attributes[k]))

		node = graph.Node(str(self.index), **attributes)
		response = self.hub.emitNode(node)
		#print(response.content)

	def insertEdge(self, directed=True, **kwargs):
		for parent in self.parents:
			assert(isinstance(parent, int))
			eid = str(self.index) + '>' + str(parent)
			edge = graph.Edge(str(self.index), str(parent), eid=eid, directed=directed, **kwargs)
			self.hub.emitEdge(edge)

	def setFitness(self, fitness, **kwargs):
		self.fitness = fitness
		self.attributes.update(kwargs)

	def deploy(self, ind=None, transmit=True):
		self._index = ind if ind else Tracker._IND_COUNT
		Tracker._IND_COUNT += 1
		self.hub.register(self)
		if transmit:
			self.insertNode()
		return self._index
