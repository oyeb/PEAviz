import random

import numpy
import operator

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import peaviz

IND_INIT_SIZE = 5
MAX_ITEM = 15
MAX_WEIGHT = 50
NBR_ITEMS = 10
SEED = 80

random.seed(SEED)

def maker(icls, attr, dimension):
    individual = tools.initRepeat(icls, attr, dimension)
    individual.cid = tracker.deploy(individual)
    return individual

def evalKnapsack(individual):
    weight = 0.0
    value = 0.0
    for item in individual:
        weight += items[item][0]
        value += items[item][1]
    if len(individual) > MAX_ITEM or weight > MAX_WEIGHT:
        return 10000, 0             # Ensure overweighted bags are dominated
    fitness = weight, value
    tracker.update_fitness(individual.cid, fitness)
    tracker.update_score(individual.cid, sum(map(operator.mul, individual.fitness.weights, fitness)))
    return fitness

def breedAndTrack(algorithm, *parents, generation, otherAttrs):
    children = algorithm(*parents) # parents is modified in-place.
                                   # children is a shallow copy of parents
    # need to evaluate it here, as later steps will modify cid!
    parentConcreteIds = list(map(lambda p: p.cid, parents))

    # this does not set Cids but just creates nodes in the adapter We can lazy
    # evaluate here, as this is expanded in the for loop below, luckily at the
    # right time.
    # newConcreteIds = map(tracker.deploy, children, generation)
    newConcreteIds = []
    for c in children:
        newConcreteIds.append(tracker.deploy(c, generation))

    for child, newCid in zip(children, newConcreteIds):
        child.cid = newCid
        edgeIDs = tracker.set_parents(
            newCid,
            parentConcreteIds,
            generation, otherAttrs)
        # print('made (%03d, %03d) --%03d, %03d--> *(%03d)*' % (parentConcreteIds[0], parentConcreteIds[1], edgeIDs[0], edgeIDs[1], child.cid))
    return children

def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.
    """

    temp = set(ind1)                # Used in order to keep type
    ind1 &= ind2                    # Intersection (inplace)
    ind2 ^= temp                    # Symmetric Difference (inplace)

    return ind1, ind2
    
def mutSet(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.remove(random.choice(sorted(tuple(individual))))
    else:
        individual.add(random.randrange(NBR_ITEMS))
    return individual,


# Create the item dictionary: item name is an integer, and value is 
# a (weight, value) 2-uple.
items = {}
# Create random items and store them in the items' dictionary.
for i in range(NBR_ITEMS):
    items[i] = (random.randint(1, 10), random.uniform(0, 100))
print("ITEMS\n", items)

creator.create( "concreteIndex", int)
creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
creator.create("Individual", set, fitness=creator.Fitness, cid=creator.concreteIndex)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_item", random.randrange, NBR_ITEMS)
# Structure initializers
toolbox.register("individual", maker, creator.Individual, toolbox.attr_item, IND_INIT_SIZE)
# toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_item, IND_INIT_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evalKnapsack)
toolbox.register("mate", breedAndTrack, cxSet)
toolbox.register("mutate", mutSet)
toolbox.register("select", tools.selNSGA2)

tracker = peaviz.trackers.TrackerBasic(
    peaviz.adapters.GraphAdapter,
    seed_str=str(SEED),
    name='small/knapsack0')

NGEN = 40
MU = 50
LAMBDA = 100
CXPB = 0.7
MUTPB = 0.2

def doNSGA(pop, gen):
    # Vary the population, this clones the individuals
    offspring = peaviz.algorithms.varOr(pop, toolbox, LAMBDA, CXPB, MUTPB, gen)
        
    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    d = toolbox.clone(offspring)
    # Select the next generation population
    return len(invalid_ind), toolbox.select(pop + offspring, MU), d

def doWithNSGA2(seed, logbook, stats):
    
    random.seed(seed)
    
    pop = toolbox.population(n=MU)
    # Evaluate the individuals with an invalid fitness
    fitnesses = toolbox.map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    record = stats.compile(pop)
    logbook.record(gen=0, nevals=MU, **record)
    print(logbook.stream)

    for gen in range(1, NGEN+1):
        nevals, pop[:], o = doNSGA(pop, gen)
        record = stats.compile(pop)
        logbook.record(gen=gen, nevals=nevals, **record)
        print(logbook.stream)
    
    print('Total: %d' % tracker.num_nodes())
    print("\nwriting to file...")
    tracker.save()
    return pop
                 
if __name__ == "__main__":
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals']

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook.header.extend(stats.fields)
    
    pop = doWithNSGA2(SEED, logbook, stats)
    #print(len(gs))
