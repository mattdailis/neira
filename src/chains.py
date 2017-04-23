# A Chain is a Listof Nodes

from graph import fromAssociationList
from neiradjango.neira.associationList import Edge


def chainsFromSeed(seed, graph):
    chains = []
    if len(graph.succ(seed)) == 0:
        return [[seed]]
    for succ in graph.succ(seed):
        for chain in chainsFromSeed(succ, graph):
            chain.insert(0, seed)
            chains.append(chain)
    return chains

def allChains(graph):
    chains = []
    for seed in graph.firstSet():
        chains += chainsFromSeed(seed, graph)
    return chains

def related(chain1, chain2):
    for node in chain1:
        if node in chain2:
            return True
    return False

def mergeChains(chain1, chain2, graph):
    # Get the index of the intersection
    c1 = 0
    while chain1[c1] not in chain2:
        c1 += 1
    common = chain1[c1]

    c2 = chain2.index(common)

    # m1 and m2 are the accumulated margins
    m1 = 0
    m2 = 0
    # i, j are indicies in each chain
    i = c1 - 1
    j = c2 - 1
    chain3 = [common]
    while i > 0 and j > 0:
        nodeI = chain1[i]
        nodeJ = chain2[j]
        (dateI, marginI) = graph.checkData(chain1[i-1], nodeI)
        (dateJ, marginJ) = graph.checkData(chain2[j-1], nodeJ)
        if graph.isAncestor(nodeI, nodeJ):
            # If this fails. the chain does not fit the invariant:
            chain3.insert(0, nodeJ)
            m2 += marginJ
            j -= 1
        elif graph.isAncestor(nodeJ, nodeI):
            chain3.insert(0, nodeI)
            m1 += marginI
            i -= 1
        elif marginJ + m2 < marginI + m1:
            chain3.insert(0, nodeI)
            i -= 1
        else:
            chain3.insert(0, nodeJ)
            j -= 1

    # Prepend the remainder
    chain3 = chain1[:i+1] + chain2[:j+1] + chain3

    # reset to the common
    i = c1 + 1
    j = c2 + 1
    m1 = 0
    m2 = 0
    while i < len(chain1) and j < len(chain2):
        nodeI = chain1[i]
        nodeJ = chain2[j]
        try:
            (dateI, marginI) = graph.checkData(chain1[i-1], nodeI)
        except TypeError:
            print chain1
            raise TypeError
        try:
            (dateJ, marginJ) = graph.checkData(chain2[j-1], nodeJ)
        except TypeError:
            print chain2
            raise TypeError
        if nodeI == nodeJ:
            common = nodeI
            chain3.append(common)
            i += 1
            j += 1
            m1 = 0
            m2 = 0
        elif nodeI in chain2[j:]:
            while chain2[j] != nodeI:
                chain3.append(chain2[j])
                j += 1
        elif nodeJ in chain1[i:]:
            while chain1[i] != nodeJ:
                chain3.append(chain1[i])
                i += 1
        elif graph.isAncestor(nodeJ, nodeI):
            chain3.append(nodeJ)
            m2 += marginJ
            j += 1
        elif graph.isAncestor(nodeI, nodeJ):
            chain3.append(nodeI)
            m1 += marginI
            i += 1
        elif marginI + m1 < marginJ + m2:
            chain3.append(nodeI)
            i += 1
        else:
            chain3.append(nodeJ)
            j += 1

    chain3 = chain3 + chain1[i:] + chain2[j:]
   # print chain1, "+", chain2, "=", chain3
    return chain3

def compare(node1, node2, graph):
    return 1

def seed(graph):
    chains = allChains(graph)
    if len(chains) == 1:
        return chains[0]
    else:
        chain = chains[0]
        chains = chains[1:]
        merge = (lambda chain1, chain2: mergeChains(chain1, chain2, graph))
        i = -1
        unchangeCount = 0
        while len(chains) > 0:
            if unchangeCount >= len(chains):
                raise Exception
            i = (i + 1) % len(chains)
            unchangeCount += 1
            if related(chains[i], chain):
                chain = merge(chain, chains[i])
                chains = chains[:i] + chains[i+1:]
                unchangeCount = 0
    return chain

if __name__ == '__main__':
    e1 = Edge(0, 1, 2, 0)
    e2 = Edge(0, 2, 3, 0)
    e3 = Edge(0, 3, 4, 0)
    e4 = Edge(0, 5, 6, 0)
    e5 = Edge(0, 6, 3, 0)
    e6 = Edge(0, 3, 7, 0)
    e7 = Edge(0, 7, 8, 0)

    edges = [e1, e2, e3, e4, e5, e6, e7]
    graph = fromAssociationList(edges)

    print seed(graph)
