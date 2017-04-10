class AdapterBase():

    def add_node(self, gene, gen=0, attr={}):
        return 0

    def add_edge(self, TAG, srcID, destID, attrs={}):
        pass

    def getNode(self, nodeID):
        pass

    def getEdge(self, edgeID):
        pass

    def fetchIndividual(self, individual):
        pass

    def walk_edge(self, TAG, startID):
        pass

    def update_fitness(self, nodeID, fitness):
        pass

    def save(self):
        pass
