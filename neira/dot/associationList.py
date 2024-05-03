class Pair():
    def __init__(self, a, b):
        self.first = a
        self.second = b

class Edge(Pair):
    def __init__(self, d, o, t, m, am):
        self.date = d
        self.first = o
        self.second = t
        self.margin = m
        self.adjusted_margin = am
        self.red = False
        self.url = "#"
        self.tooltip = ""
        self.firstURL = ""
        self.secondURL = ""

    def __hash__(self):
        return hash((self.date, self.first, self.second, self.margin))

    def toPairTuple(self):
        return (self.first, self.second)

    def __repr__(self):
        return str((self.first, self.second, self.date, self.margin, self.red))

# [Listof Nodes] [Listof Pairs] -> [Listof Nodes]
# Returns the set of nodes which have no incoming edges
def getFirst(nodes, orders):
    notFirst = set([])
    for pair in orders:
        notFirst.add(pair.second)
    return nodes.difference(notFirst)

# [Listof Pairs] -> [Listof Nodes]
# Collects the set of nodes that are touched by these edges
def getNodes(orders):
    nodes = set([])
    for pair in orders:
        nodes.add(pair.first)
        nodes.add(pair.second)
    return nodes

# Association List (a, b)
def removeAll(item, orders):
    return list(filter(
        (lambda pair: item != pair.first and item != pair.second),
        orders))

# Association List (a, b)
def outEdges(node, edges):
    res = set([])
    for edge in edges:
        if node == edge.first:
            res.add(edge)
    return res

# Association List
def cycles(edges):
    nodes = getNodes(edges)
    firsts = getFirst(nodes, edges)
    cycles = []
    visited = set([])
    for seed in firsts:
        (otherCycles, otherVisited) = cyclesHelp(seed, [], edges, visited)
        #print(otherCycles)
        cycles += otherCycles
        visited = visited.union(otherVisited)
    return cycles

# Association List
def cyclesHelp(node, ancestors, edges, visited):
    if len(edges) <= 1:
        return ([], set([]))
    out = outEdges(node, edges)
    if len(out) == 0:
        return ([], set([]))
    if node in visited:
        return ([], set([]))
    res = []
    next = []
    for edge in out:
        hasCycle = False
        if edge.second == node:
            res.append([this, this])
            hasCycle = True
        for i in range(len(ancestors)):
            if edge.second == ancestors[i]:
                cycle = ancestors[i:] + [node, that]
                res.append(cycle)
                hasCycle = True
        if hasCycle == False:
            next.append(that)
    otherVisited = set([])
    for child in next:
        (otherCycles, otherVisited) = cyclesHelp(child, ancestors + [node], edges, visited)
        res += otherCycles
    return (res, set(ancestors + [node]).union(otherVisited).union(visited))

# Association List
def averageEdges(edges):
    edgeDict = {}
    for edge in edges:
        if edge.toPairTuple() not in edgeDict:
            edgeDict[edge.toPairTuple()] = set([])
        edgeDict[edge.toPairTuple()].add((edge.date, edge.margin))
    newEdges = set([])
    for (o, t) in list(edgeDict.keys()):
        s = 0
        margins = edgeDict[(o, t)]
        for (d, m) in margins:
            if m == None:
                m = 10 # magic number!
            s += m
        avg = float(s) / len(margins)
        newEdges.add(Edge(d, o, t, avg))
    return newEdges

def earliestRace(races):
    return min(races, key=(lambda edge : edge.date))

# Association List
# Returns the set of edges which, if removed, would leave a DAG
def getFeedbackSet(edges):
    edges = set(edges)
    nodes = getNodes(edges)
    cycles = []
    visited = set([])
    feedbackSet = set([])
    for seed in nodes:
        visited = visited.union(removeCyclesHelp(seed, [], edges, visited, feedbackSet))
    return feedbackSet

# Association List
# Removes Feedback Set from a set of edges
def removeCycles(edges):
    edges = set(edges)
    feedbackSet = getFeedbackSet(edges)
    return averageEdges(list(edges.difference(feedbackSet)))

# Association List
# Returns a set of 5-tuples, marked with True if in the Feedback Set
def markCycles(edges):
    edges = set(edges)
    feedbackSet = getFeedbackSet(edges)
    black = edges.difference(feedbackSet)
    red = feedbackSet
    res = set([])
    for edge in black:
        edge.red = False
        res.add(edge)
    for edge in red:
        edge.red = True
        res.add(edge)
    return res

def removeCyclesHelp(node, path, edges, visited, feedbackSet):
    if len(edges) <= 1:
        return set([node])
    out = outEdges(node, edges).difference(feedbackSet)
    if len(out) == 0:
        return set([node])
    if node in visited:
        return set([node])
    next = []
    for edge in out:
        hasCycle = False
        #if edge.second == node:
        #    feedbackSet.add(edge)
        #    hasCycle = True
        for i in range(len(path)):
            if edge.second == path[i].first:
                cycle = path[i:] + [edge]
                feedbackSet.add(earliestRace(cycle))
                hasCycle = True
        if edge.first == edge.second:
            feedbackSet.add(edge)
            hasCycle = True
        if hasCycle == False:
            next.append(edge)
    otherVisited = set([])
    for edge in next:
        otherVisited = removeCyclesHelp(edge.second, path + [edge], edges.difference(feedbackSet), visited.union(set([node])), feedbackSet)
    return otherVisited.union(visited)
