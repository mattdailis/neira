from associationList import Edge

class Graph():
    def __init__(self):
        self.outEdges = {}
        self.inEdges = {}
        self.inEdgeCount = {}
        self.data = {}
        self.nodes = set([])
        self.notFirst = set([])
        self.removed = set([])
        self.ancestors = {}

    def addEdge(self, key, val, data):
        if self.checkData(key, val) != None:
            print self.checkData(key, val)
            print key, val, data
            raise ValueError
        (d, m) = data
        if m < 0:
            tmp = key
            key = val
            val = tmp
            data = self.flipData(data)
        self.initNode(key)
        self.initNode(val)
        self.outEdges[key].add(val)
        if key not in self.inEdges[val]:
            self.inEdges[val].add(key)
            if key not in self.removed and val not in self.removed:
                self.inEdgeCount[val] += 1
            self.notFirst.add(val)
        self.data[(key, val)] = data

        self.updateAncestors(val, set([key]))

#        print "New Edge:", key, "->", val


    def succ(self, key):
        return self.outEdges[key]

    def pred(self, key):
        return self.inEdges[key]

    def adj(self, key):
        return self.inEdges[key].union(self.outEdges[key])

    def firstSet(self):
        return self.nodes.difference(self.notFirst).difference(self.removed)

    def initNode(self, key):
        self.nodes.add(key)
        self.makeKey(key, self.outEdges, set([]))
        self.makeKey(key, self.inEdges, set([]))
        self.makeKey(key, self.inEdgeCount, 0)

    def makeKey(self, key, dic, default):
        if not key in dic.keys():
            dic[key] = default

    # Passively returns data if it exists
    def checkData(self, first, second):
        if (first, second) in self.data:
            return self.data[(first, second)]
        elif (second, first) in self.data:
            return self.flipData(self.data[(second, first)])
        else:
            return None

    # Actively creates data if it doesn't exist
    def findData(self, first, second):
        data = self.checkData(first, second)
        if data == None:
            return self.createData(first, second, set([]))
        else:
            return data

    # Assumes data is in the form (date, margin)
    def flipData(self, data):
        (date, margin) = data
        if margin == None:
            return (date, 0) # 0 or None?
        else:
            return (date, -margin)

    def pop(self, key):
        if key in self.nodes and key not in self.removed:
            print "pop!", key
#            if key not in self.notFirst:
            self.removed.add(key)
            for val in self.succ(key):
                print "sub1", val, self.inEdgeCount[val], self.inEdgeCount[val] - 1
                self.inEdgeCount[val] -= 1
                if self.inEdgeCount[val] <= 0:
                    self.notFirst.remove(val)


    # dfs
    def createDataDFS(self, first, second, visited):
        data = self.checkData(first, second)
        if data != None:
            return data
        if first == second:
            return (None, 0)
        adj = self.adj(first)
        avgData = set([])
        for node in adj.difference(visited):
            (date1, margin1) = self.checkData(first, node)
            for pred in visited:
                if self.checkData(pred, node) == None:
                    (date0, margin0) = self.checkData(pred, first)
                    totalMargin = margin0 + margin1
                    self.addEdge(pred, node, (max(date0, date1), totalMargin))

            rest = self.createData(node, second, visited.union(set([first])))
            if rest != None:
                (date2, margin2) = rest
                avgData.add((max(date1, date2), float(margin1 + margin2)))
        if len(avgData) > 0:
            maxdate = max(list(d for (d, m) in avgData))
            avgmargin = sum(list(m for (d, m) in avgData)) / len(avgData)
            self.addEdge(first, second, ((maxdate, avgmargin)))
            return (maxdate, avgmargin)

    #bfs
    def createData(self, first, second, blank):
        visited = set([first])
        fromNode = {}
        data = self.checkData(first, second)
        if data != None:
            return data
        if first == second:
            return (None, 0)
        worklist = list(self.adj(first))
        for w in worklist:
            fromNode[w] = first
        while len(worklist) > 0:
            current = worklist.pop(0)

            if current == second:
                # printpath(first, second, fromNode)
                return self.checkData(first, second)

            (date, margin) = self.checkData(first, current)

#            if self.checkData(current, second) != None:
#                fromNode[second] = current
#                # printPath(first, second, fromNode)
#                (date1, margin1) = self.checkData(current, second)
#                return (max(date, date1), margin + margin1)


            visited.add(current)
            adj = self.adj(current)
            for node in adj.difference(visited):
                (nodeDate, nodeMargin) = self.checkData(current, node)
                if node not in worklist:
                    worklist.append(node)
                    if self.checkData(first, node) == None:
                        self.data[(first, node)] = (max(date, nodeDate), margin + nodeMargin)
                fromNode[node] = current

    def updateAncestors(self, node, newMembers):
        if node not in self.ancestors.keys():
            self.ancestors[node] = set([])
        if len(newMembers) > 0:
            newMembers = newMembers.difference(self.ancestors[node])
            self.ancestors[node] = self.ancestors[node].union(newMembers)
            for succ in self.succ(node):
                self.updateAncestors(succ, newMembers.union(set([node])))

    def isAncestor(self, node1, node2):
        if node2 in self.ancestors.keys():
            return node1 in self.ancestors[node2]
        else:
            return False


def printPath(start, end, dic):
    current = end
    print "from", end, "to", start
    while current != start:
        print current
        current = dic[current]
    print start




# Association List
# Takes tuples of the form (date, FIRST, SECOND, margin)
# and returns a dictionary of outgoing edges
# Node -> (Node, Date, Margin)
def fromAssociationList(edges):
    graph = Graph()
    for edge in edges:
        if edge.margin == None:
            edge.margin = 10
        graph.addEdge(edge.first, edge.second, (edge.date, edge.margin))
    return graph
