import deap.creator
import deap.base
import deap.tools
import random
import time

IND_COUNT=0

def myFitness(individual):
	return (sum(individual),)

def maker(icls, attr, dimension, pid=None):
	global IND_COUNT
	ind = deap.tools.initRepeat(icls, attr, dimension)
	ind.id = IND_COUNT
	ind.pid=pid
	IND_COUNT += 1
	return ind

def copulate(algorithm, p1, p2):
	global IND_COUNT
	p1.pid = (p1.id, p2.id)
	p2.pid = (p1.id, p2.id)
	#print('crossing: %d <-> %d' % (p1.id, p2.id))
	p1.id = IND_COUNT
	IND_COUNT += 1
	p2.id = IND_COUNT
	IND_COUNT += 1
	return algorithm(p1, p2)

def pmutate(algorithm, ind, **kwargs):
	print('mutating: %d' % ind.id)
	return algorithm(ind, indpb=kwargs['indpb'])

deap.creator.create("maximize", deap.base.Fitness, weights=(1.0,))
deap.creator.create("Individual", list, fitness=deap.creator.maximize, id=int, pid=int)

toolbox = deap.base.Toolbox()
toolbox.register("attr", random.randint, 0, 1)

toolbox.register("individual", maker, deap.creator.Individual, toolbox.attr, 4)
toolbox.register("population", deap.tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", myFitness)
toolbox.register("mate", copulate, deap.tools.cxTwoPoint)
toolbox.register("mutate", deap.tools.mutFlipBit, indpb=0.05)
toolbox.register("select", deap.tools.selTournament, tournsize=3)

POP = toolbox.population(n=10)
CXPB, MUTPB, NGEN = 0.4, 0.1, 35

def show(msg=None, p=POP):
	if msg:
		print(msg)
	for i in p:
		print("%2d %r %r %r" % (i.id, i.pid, i.fitness.values, i))

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
			toolbox.mate(c1, c2)
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

def main():
	random.seed(time.time())
	pop = toolbox.population(n=200)

	fitnesses = list(toolbox.map(toolbox.evaluate, pop))
	for ind, fit in zip(pop, fitnesses):
		ind.fitness.values = fit

	for g in range(NGEN):
		print("--G %2d" % g)
		pick = toolbox.select(pop, len(pop))
		pick = list(toolbox.map(toolbox.clone, pick))

		for c1, c2 in zip(pick[::2], pick[1::2]):
			if random.random() < CXPB:
				toolbox.mate(c1, c2)
				del c1.fitness.values
				del c2.fitness.values
		for mut in pick:
			if random.random() < MUTPB:
				toolbox.mutate(mut)
				del mut.fitness.values
		invalids = [ind for ind in pick if not ind.fitness.valid]
		fitnesses = list(toolbox.map(toolbox.evaluate, invalids))
		for ind, fit in zip(invalids, fitnesses):
			ind.fitness.values = fit

		pop[:] = pick

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

if __name__ == '__main__':
	main()
	print('\nCreated', IND_COUNT, 'individuals!')