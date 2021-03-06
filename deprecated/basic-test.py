import deap.creator
import deap.base
import deap.tools
import random
import time

import peaviz

trackerHub = peaviz.TrackerHub()

def myFitness(individual):
	fitness = (sum(individual),)
	individual.tracker.setFitness(fitness)
	return fitness

def maker(icls, attr, dimension):
	individual = deap.tools.initRepeat(icls, attr, dimension)
	individual.tracker.deploy()
	return individual

def breed(algorithm, parents):
	for offspring in parents:
		offspring.tracker.setParents([parent.tracker.index for parent in parents])
	for offspring in parents:
		offspring.tracker.deploy()
	return algorithm(*parents)


# add any other default args to the tracker here:
deap.creator.create("tracker", peaviz.Tracker, hub=trackerHub)

# a normal (deap) fitness vector
deap.creator.create("maximize", deap.base.Fitness, weights=(1.0,))

# The individual must have a tracker attribute
deap.creator.create("Individual", list, fitness=deap.creator.maximize, tracker=deap.creator.tracker)

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

POP = toolbox.population(n=10)
CXPB, MUTPB, NGEN = 0.4, 0.1, 35

def show(msg=None, p=POP):
	if msg:
		print(msg)
	for i in p:
		print("%2d %r %r %r" % (i.tracker.index, i.tracker.parents, i.fitness.values, i))

def evalt():
	fitnesses = list(toolbox.map(toolbox.evaluate, POP))
	for ind, fit in zip(POP, fitnesses):
		ind.fitness.values = fit

def sel():
	pick = toolbox.select(POP, len(POP))
	return list(toolbox.map(toolbox.clone, pick))

def cross(pick):
	for c1, c2 in zip(pick[::2], pick[1::2]):
		if random.random() < CXPB:
			toolbox.mate((c1, c2))
			del c1.fitness.values
			del c2.fitness.values

def mut(pick):
	for mut in pick:
		if random.random() < MUTPB:
			toolbox.mutate(mut)
			del mut.fitness.values

def re_eval(pick):
	invalids = [ind for ind in pick if not ind.fitness.valid]
	fitnesses = list(toolbox.map(toolbox.evaluate, invalids))
	for ind, fit in zip(invalids, fitnesses):
		ind.fitness.values = fit

def script():
	evalt()
	show()
	os = sel()
	show('os', os)
	cross(os)
	show('crossed os', os)
	mut(os)
	show('mut os', os)
	re_eval(os)
	show('re-evaluated', os)
	print('\nTrackers:', len(trackerHub), '\n')
	POP[:] = os
	
	show()
	os = sel()
	show('os', os)
	cross(os)
	show('crossed os', os)
	mut(os)
	show('mut os', os)
	re_eval(os)
	show('re-evaluated', os)
	print('\nTrackers:', len(trackerHub))
script()