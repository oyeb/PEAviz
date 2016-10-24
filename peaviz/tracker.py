#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Track evolution dynamics like individual interactions, fitness statistics. This
information is used to create the Complex Network.
"""
import gephistreamer.graph as graph
import gephistreamer.streamer as streamer

class TrackerHub:
	"""
	@brief      Coordinates all trackers for a (sub) population.
	"""
	@property
	def bucket(self):
		return self._bucket
	
	def __init__(self, streamer=streamer.Streamer(streamer.GephiREST())):
		self.streamer = streamer
		self._bucket = {}

	def register(self, tracker):
		try:
			self._bucket[tracker.index] = tracker
		except:
			raise RuntimeError("Tracker cannot be registered, it has no `identity`!")

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

	def __init__(self, hub=None, parents=None, gen=0, fitness=None, **kwargs):
		self._hub = hub
		self._index = None
		self.preset(parents, gen, fitness, **kwargs)

	def preset(self, parents=None, gen=0, fitness=None, **kwargs):
		self.parents = parents
		self.gen = gen
		self.fitness = fitness
		self.attributes = kwargs

	def setParents(self, parents, gen=None):
		assert(isinstance(parents[0], int))
		self.parents = parents
		if gen:
			self.gen = gen
		else:
			self.gen += 1

	def setFitness(self, fitness, **kwargs):
		self.fitness = fitness
		self.attributes.update(kwargs)

	def deploy(self, ind=None):
		self._index = ind if ind else Tracker._IND_COUNT
		Tracker._IND_COUNT += 1
		self.hub.register(self)
		return self._index
