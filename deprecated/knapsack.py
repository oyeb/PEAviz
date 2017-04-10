import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import peaviz, py2neo

IND_INIT_SIZE = 5
MAX_ITEM = 50
MAX_WEIGHT = 50
NBR_ITEMS = 20
SEED = 64

random.seed(SEED)
neodb = peaviz.Neo4jAdapter(SEED, passwd='kraken')
neodb.connect()

neoNodes = []

def maker(icls, attr, dimension):
    individual = tools.initRepeat(icls, attr, dimension)
    node = py2neo.Node(
        "I", str(SEED),
        gene=individual,
        gen=0,
        fitness=None
    )
    neoNodes.append(node)
    neodb.graph.merge(node)
    individual.neoNodeIndex = len(neoNodes)-1
    print(individual.neoNodeIndex)
    return individual

# Create the item dictionary: item name is an integer, and value is 
# a (weight, value) 2-uple.
items = {}
# Create random items and store them in the items' dictionary.
for i in range(NBR_ITEMS):
    items[i] = (random.randint(1, 10), random.uniform(0, 100))
print("ITEMS\n", items)

# creator.create("NeoNode", peaviz.NeoNode)
creator.create( "NeoNodeIndex", int)
creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
# creator.create("Individual", set, fitness=creator.Fitness, neoNode=creator.NeoNode)
creator.create("Individual", set, fitness=creator.Fitness, neoNodeIndex=creator.NeoNodeIndex)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_item", random.randrange, NBR_ITEMS)

# Structure initializers
toolbox.register("individual", maker, creator.Individual, toolbox.attr_item, IND_INIT_SIZE)
# toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_item, IND_INIT_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalKnapsack(individual):
    weight = 0.0
    value = 0.0
    for item in individual:
        weight += items[item][0]
        value += items[item][1]
    if len(individual) > MAX_ITEM or weight > MAX_WEIGHT:
        return 10000, 0             # Ensure overweighted bags are dominated
    
    node = neoNodes[individual.neoNodeIndex]
    node['fitness'] = weight, value
    node['score'] = weight+value
    neodb.graph.merge(node)
    return weight, value

def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.
    """
    p1 = neoNodes[ind1.neoNodeIndex]
    p2 = neoNodes[ind2.neoNodeIndex]

    temp = set(ind1)                # Used in order to keep type
    ind1 &= ind2                    # Intersection (inplace)
    ind2 ^= temp                    # Symmetric Difference (inplace)
    
    node1 = py2neo.Node(
        gene=ind1,
        gen=None)
    node2 = py2neo.Node(
        gene=ind2,
        gen=None)
    r1 = peaviz.ParentOf(p1, node1)
    r2 = peaviz.ParentOf(p2, node2)
    neoNodes.append(node1)
    neoNodes.append(node2)
    ind2.neoNodeIndex = len(neoNodes) - 1
    ind1.neoNodeIndex = ind2.neoNodeIndex - 1
    neodb.graph.merge(node1|node2|r1|r2)
    
    return ind1, ind2
    
def mutSet(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.remove(random.choice(sorted(tuple(individual))))
    else:
        individual.add(random.randrange(NBR_ITEMS))

    node = neoNodes[individual.neoNodeIndex]
    node["gene"] = individual
    neodb.graph.merge(node)
    return individual,

toolbox.register("evaluate", evalKnapsack)
toolbox.register("mate", cxSet)
toolbox.register("mutate", mutSet)
toolbox.register("select", tools.selNSGA2)

def main(seed):
    random.seed(seed)
    NGEN = 50
    MU = 50
    LAMBDA = 100
    CXPB = 0.7
    MUTPB = 0.2
    
    pop = toolbox.population(n=MU)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    
    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats)
    
    return pop, stats
                 
if __name__ == "__main__":
    main(SEED)

