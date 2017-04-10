import deap.creator
import deap.base
import deap.tools
import deap.algorithms
import random
import time

import peaviz.trackers
import peaviz.adapters
import peaviz.algorithms

SEED = 64
CXPB, MUTPB, NGEN = 1, 0.1, 35
POP = []
TRACKER = None

def myFitness(individual):
	fitness = (sum(individual),)
	TRACKER.updateFitness(individual.cid, fitness)
	return fitness

def maker(icls, attr, dimension):
	individual = deap.tools.initRepeat(icls, attr, dimension)
	individual.cid = TRACKER.deploy(individual)
	return individual

def breed(algorithm, *parents):
	children = algorithm(*parents)
	for child in children:
		child.cid = TRACKER.deploy(child)
	return children

def real_breed(algorithm, *parents, generation, otherAttrs):
	children = algorithm(*parents) # parents is modified in-place.
	                               # children is a shallow copy of parents
	# need to evaluate it here, as later steps will modify cid!
	parentConcreteIds = list(map(lambda p: p.cid, parents))
	# this does not set Cids but just creates nodes in the adapter
	newConcreteIds = map(TRACKER.deploy, children)

	for child, newCid in zip(children, newConcreteIds):
		child.cid = newCid
		edgeIDs = TRACKER.setParents(
			newCid,
			parentConcreteIds,
			generation, otherAttrs)
		# print('made (%03d, %03d) --%03d, %03d--> *(%03d)*' % (parentConcreteIds[0], parentConcreteIds[1], edgeIDs[0], edgeIDs[1], child.cid))
	return children


random.seed(SEED)
deap.creator.create("concreteID", int)

# a normal (deap) fitness vector
deap.creator.create("maximize", deap.base.Fitness, weights=(1.0,))

# The individual must have a tracker attribute
deap.creator.create("Individual", list, fitness=deap.creator.maximize, cid=deap.creator.concreteID)

toolbox = deap.base.Toolbox()
toolbox.register("attr", random.randint, 0, 1)

# `maker` takes responsibility to properly configure the tracker
toolbox.register("individual", maker, deap.creator.Individual, toolbox.attr, 4)
toolbox.register("population", deap.tools.initRepeat, list, toolbox.individual)

# `myFitness` is a simple function, which additionall keeps the tracker updated
toolbox.register("evaluate", myFitness)
# `breed` basically runs the custom/deap crossover algorithm, and updates the generation history in the trackers
toolbox.register("mate", breed, deap.tools.cxTwoPoint)
toolbox.register("mutate", deap.tools.mutFlipBit, indpb=0.05)
toolbox.register("select", deap.tools.selTournament, tournsize=3)

def show(msg, p, verbose=False):
	l = []
	if msg:
		print(msg)
	if verbose:
		for i in p:
			node = TRACKER.getRawNode(i.cid)
			l.append(node)
			print(
				"%3d %r" % (i.cid, l[-1]),
				i.fitness.values,
				i)

def evalt():
	fitnesses = list(toolbox.map(toolbox.evaluate, POP))
	for ind, fit in zip(POP, fitnesses):
		ind.fitness.values = fit

def sel():
	pick = toolbox.select(POP, len(POP))
	return list(toolbox.map(toolbox.clone, pick))

def re_eval(pick):
	invalids = [ind for ind in pick if not ind.fitness.valid]
	fitnesses = list(toolbox.map(toolbox.evaluate, invalids))
	for ind, fit in zip(invalids, fitnesses):
		ind.fitness.values = fit

def adapter_base_test(verbose=False):
	print('TRACKER_BASE')
	global POP, TRACKER
	TRACKER = peaviz.trackers.TrackerBase(peaviz.adapters.AdapterBase)
	POP = toolbox.population(n=10)

	evalt()
	show('evaluated', POP, verbose=verbose)
	os = sel()
	show('selection', os, verbose=verbose)
	deap.algorithms.varAnd(os, toolbox, CXPB, MUTPB)
	show('offspring', os, verbose=verbose)
	re_eval(os)
	show('re-evaluated', os, verbose=verbose)
	print('True!!\n')

def adapter_graph_test(seed_str, name, file_extension='gml', verbose=False):
	def list_nodes():
		for node in TRACKER.adapter.graph.vertices():
			print(
				'%3d' % int(node),
				'gen:', TRACKER.adapter.graph.vp.gen[node],
				TRACKER.adapter.graph.vp.gene[node].a,
				'f:', TRACKER.adapter.graph.vp.fitness[node].a,
				's:', TRACKER.adapter.graph.vp.score[node])
		print('-'*20)
	def list_edges():
		for edge_descr in TRACKER.adapter.graph.get_edges():
			edge = TRACKER.adapter.graph.edge(edge_descr[0], edge_descr[1])
			print(
				'%3d' % edge_descr[2],
				'%3d --%s-> %3d' % (
					edge_descr[0],
					TRACKER.adapter.graph.ep.label[edge],
					edge_descr[1]),
				'in gen: %3d' % TRACKER.adapter.graph.ep.gen[edge])
		print('-'*20)

	print('GRAPH_ADAPTER')

	toolbox.register("mate", real_breed, deap.tools.cxTwoPoint)
	global POP, TRACKER
	TRACKER = peaviz.trackers.TrackerBase(peaviz.adapters.GraphAdapter, seed_str=seed_str, name=name)
	POP = toolbox.population(n=10)

	show('init', POP, verbose=False)
	evalt()
	show('evaluated', POP, verbose=False)
	selected = sel()
	show('selection', selected, verbose=verbose)
	offspring = peaviz.algorithms.varAnd(selected, toolbox, CXPB, MUTPB, 1, {})
	show('offspring', offspring, verbose=False)
	re_eval(offspring)
	show('re-evaluated', offspring, verbose=verbose)
	
	list_nodes()
	list_edges()
	
	POP = offspring[:]
	selected = sel()
	show('selection', selected, verbose=False)
	offspring = peaviz.algorithms.varAnd(selected, toolbox, CXPB, MUTPB, 2, {})
	show('offspring', offspring, verbose=False)
	re_eval(offspring)
	show('re-evaluated', offspring, verbose=False)

	list_nodes()
	list_edges()
	TRACKER.save()
	# print('True!!')

if __name__ == '__main__':
	adapter_base_test()
	adapter_graph_test(str(SEED), 'foobar', 'gml', verbose=True)
