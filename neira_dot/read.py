import datetime
import json
import os

import numpy as np
from scipy.linalg import eig

from associationList import Edge
from associationList import getNodes
from neiraschools import matchSchool, matched, unmatched
from toDot import viz

import click


def sorter(string):
    string = string.lower()
    if "boys" in string:
        string = "0" + string
    if "girls" in string.lower():
        string = "1" + string
    if "eight" in string:
        string = "1" + string
    else:
        string = "0" + string
    return string


def orderEntry(orders, school, boat):
    if school not in list(orders.keys()):
        orders[school] = {}
    if boat not in list(orders[school].keys()):
        orders[school][boat] = []


def getMargin(time1, time2):
    time1 = getTime(time1)
    time2 = getTime(time2)
    if time1 == None or time2 == None:
        return None
    return (time2 - time1).total_seconds()


def getTime(time):
    time = cleanTime(time)
    formats = ["%M:%S.%f", "%M.%S.%f", "%M:%S"]
    for f in formats:
        try:
            return datetime.datetime.strptime(time, f)
        except:
            continue
    return None


def cleanTime(string):
    res = (
        string.replace("!", "1")
        .replace(" ", "")
        .replace(";", ":")
        .replace("..", ".")
        .replace(",", ".")
    )
    if ":" in res:
        parts = res.split(":")
        res = parts[0] + ":" + ".".join(parts[1:])
    return res


@click.command()
@click.argument("data")
@click.argument("out")
def main(data, out):
    """
    Read data from DATA and write output to OUT
    """
    data_dir = data
    out_dir = out
    del data
    del out

    results = []
    for filename in os.listdir(data_dir):
        print("Processing", filename)
        with open(os.path.join(data_dir, filename), "r") as f:
            scraped_json = json.load(f)
        day = scraped_json["day"]

        date = datetime.datetime.strptime(day, "%B %d, %Y")

        heats = scraped_json["heats"]
        regatta_display_name = scraped_json["regatta_display_name"]
        comment = scraped_json["comment"]
        url = scraped_json["url"]

        try:
            distance = int(
                comment.split("Distance:")[1]
                .split("Conditions")[0]
                .strip()
                .lower()
                .rstrip(" meters")
                .lstrip("approx. ")
                .replace(",", "")
            )
        except Exception as e:
            print(e)
            distance = None

        for heat in heats:
            class_ = heat["class"]
            gender = heat["gender"]
            varsity_index = heat["varsity_index"]
            heat_results = heat["results"]  # assume they're ordered?

            # Ignore anything that isn't Girls Fours
            # if gender != "girls":
            #     continue

            if class_ != "fours":
                continue

            boatName = gender + str(varsity_index) + class_

            # take only fastest result by a given school
            new_heat_results = []
            seen_schools = set()
            for entry in heat_results:
                school = entry["school"]
                if school not in seen_schools:
                    seen_schools.add(school)
                    new_heat_results.append(entry)
                else:
                    continue
            heat_results = new_heat_results
            del new_heat_results
            del entry
            del school

            for fasterBoat, slowerBoat in all_pairs(heat_results):
                margin = getMargin(fasterBoat["time"], slowerBoat["time"])
                if distance == 1500:
                    adjusted_margin = None
                else:
                    adjusted_margin = (
                        round((1500.0 / distance) * margin, 2)
                        if distance is not None and margin is not None
                        else None
                    )
                fasterSchool, fasterSchoolBoatNum = matchSchool(
                    fasterBoat["school"], boatNum=varsity_index
                )
                slowerSchool, slowerSchoolBoatNum = matchSchool(
                    slowerBoat["school"], boatNum=varsity_index
                )
                if fasterSchool is None:
                    # This means one of the schools was not recognized as a neira school
                    print(fasterBoat["school"], "was not recognized as a neira school")
                    continue
                if slowerSchool is None:
                    print(slowerBoat["school"], "was not recognized as a neira school")
                    continue
                if fasterSchool == slowerSchool:
                    continue
                if fasterSchoolBoatNum != slowerSchoolBoatNum:
                    continue
                fasterSchoolName = fasterSchool
                if fasterSchoolBoatNum != varsity_index:
                    continue  # ignore any boats that aren't in the right heat
                slowerSchoolName = slowerSchool
                if slowerSchoolBoatNum != varsity_index:
                    continue  # ignore any boats that aren't in the right heat
                results.append(
                    (
                        date.strftime("%Y-%m-%d"),
                        gender,
                        boatName,
                        fasterSchoolName,
                        varsity_index,
                        slowerSchoolName,
                        varsity_index,
                        margin,
                        adjusted_margin,
                        regatta_display_name,
                        comment,
                        url,
                    )
                )

    with open("schoolslog.txt", "w") as f:
        print("Matches:", file=f)
        for name, school in sorted(matched, key=lambda x: x[1]):
            print(f"{school} {name}", file=f)
        print("-" * 25)
        print("Could not be matched:", file=f)
        for name in sorted(unmatched):
            print(name, file=f)

    orders = {}
    nodes = {}

    for row in results:
        (
            date,
            gender,
            boat,
            fasterSchool,
            fasterBoat,
            slowerSchool,
            slowerBoat,
            margin,
            adjusted_margin,
            race,
            comment,
            url,
        ) = row
        if boat not in orders:
            orders[boat] = []
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        if gender + str(fasterBoat) not in boat:
            fasterSchool = fasterSchool + str(fasterBoat)
        if gender + str(slowerBoat) not in boat:
            slowerSchool = slowerSchool + str(slowerBoat)

        edge = Edge(date, fasterSchool, slowerSchool, margin, adjusted_margin)
        edge.url = url
        edge.tooltip = race + "\t\t\t\n" + comment
        orders[boat].append(edge)
        form = "{boat}: {faster} beat {slower} by {margin} seconds on {date}"
        print(
            form.format(
                date=str(date),
                faster=fasterSchool,
                slower=slowerSchool,
                boat=boat,
                margin=str(margin),
            )
        )

    for boat in sorted(list(orders.keys()), key=sorter):
        if "eight" in boat:
            continue
        edges = orders[boat]
        viz(out_dir, boat, boat, edges)

        schools = {x.first for x in edges}
        schools.update({x.second for x in edges})

        for school in schools:
            viz(
                out_dir,
                boat + school,
                boat + school,
                [
                    edge
                    for edge in edges
                    if edge.first == school or edge.second == school
                ],
            )

        with open(os.path.join(out_dir, boat + "_topo.txt"), "w") as f:
            res, edges, tail = topo_sort(edges)
            for x in res:
                print(x, file=f)

            if edges:
                print("Cycle detected: ", file=f, end="")
                print(edges, file=f)

            for x in tail:
                print(x, file=f)

        with open(os.path.join(out_dir, boat + ".csv"), "w") as f:
            for row in gen_matrix(orders[boat], None):
                print(",".join(map(str, row)), file=f)

            # print()

            # print("All pairs weights:")

            # for left, right, weight in all_pairs_weights(edges):


def all_pairs_weights(edges):
    nodes = getNodes(edges)
    weights = {}
    for node1 in nodes:
        weights[node1] = {}
        for node2 in nodes:
            weights[node1][node2] = []

    for edge in edges:
        weights[edge.first][edge.second].append(edge.margin)
        weights[edge.second][edge.first].append(-edge.margin)

        # propagate
        for neighbor in weights[edge.second]:
            weights[edge.first][neighbor].extend(
                (margin + x) for x in weights[edge.first][edge.second]
            )


def get_neighbors(edges, x):
    neighbors = []
    for edge in edges:
        if edge.first == x:
            neighbors.append((edge.second, edge.margin))
        if edge.second == x:
            neighbors.append((edge.first, -edge.margin))
    return neighbors


# def all_paths(edges, x, y):
#     neighbors = get_neighbors(x)
#     if


def topo_sort(edges):
    nodes = getNodes(edges)
    res = []
    while True:
        # get nodes that have no incoming edges
        no_incoming = get_next_set(edges, lambda x: x.first, lambda x: x.second)

        if not no_incoming:
            break

        # add those nodes to the list
        res.append(no_incoming)
        nodes.difference_update(no_incoming)

        # filter out edges that touch these nodes
        edges = [edge for edge in edges if edge.first not in no_incoming]

    tail = []
    if edges:
        # If we hit a cycle, try doing a topological sort from the bottom as well
        while True:
            # get nodes that have no incoming edges
            no_outgoing = get_next_set(
                edges, lambda x: x.second, lambda x: x.first
            )  # swap first and second

            if not no_outgoing:
                break

            # add those nodes to the list
            tail.insert(0, no_outgoing)

            # filter out edges that touch these nodes
            edges = [edge for edge in edges if edge.second not in no_outgoing]
    else:
        res.append(nodes)

    remaining_nodes = set()
    for edge in edges:
        remaining_nodes.add(edge.first)
        remaining_nodes.add(edge.second)
    return res, remaining_nodes, tail


def kruskals(edges):
    F = []
    SET = {}

    def find(x):
        while x != SET[x]:
            x = SET[x]
        return x

    def union(u, v):
        SET[find(v)] = SET[find(u)]

    for v in getNodes(edges):
        SET[v] = v
    for edge in sorted(edges, key=lambda edge: edge.date, reverse=True):
        u = edge.first
        v = edge.second
        if find(u) != find(v):
            F.append(edge)
            union(u, v)
    return F


def combine_margins(edges):
    frontier = ["Canterbury"]
    score = {"Canterbury": 0}
    while frontier:
        node = frontier.pop(0)
        for neighbor, margin in get_neighbors(edges, node):
            if neighbor not in score:
                score[neighbor] = score[node] + margin
                frontier.append(neighbor)
    return sorted(score.items(), key=lambda x: x[1])


def power_rank(edges):
    nodes = sorted(list(getNodes(edges)))
    node_to_index = {}
    index_to_node = {}
    for i, node in enumerate(nodes):
        node_to_index[node] = i
        index_to_node[i] = node
    rows = []
    for node in nodes:
        margin_per_neighbor = {}
        for neighbor, margin in get_neighbors(edges, node):
            if margin > 0:  # We're only interested in losses
                continue
            # TODO: should recency factor in here? E.g. scale margin by recency
            if neighbor not in margin_per_neighbor:
                margin_per_neighbor[neighbor] = 0
            margin_per_neighbor[neighbor] += min(
                60, abs(margin)
            )  # make negative into positive

        total = sum(margin_per_neighbor.values())
        row = []
        if total == 0:
            for node in nodes:
                row.append(1 / len(nodes))
        else:
            for node in nodes:
                if node not in margin_per_neighbor:
                    row.append(0)
                else:
                    row.append(margin_per_neighbor[node] / total)
        rows.append(row)

    # Matrix A is a square matrix - row i column j holds the summed margin of teams i and j across all times they've competed

    A = np.matrix(rows)

    w, vl, _ = eig(A, left=True)
    w_index = list(x for x in enumerate(w) if abs(x[1] - 1) < 0.0000000001)[0][0]

    return sorted(zip(nodes, vl[:, w_index]), key=lambda x: x[1])


def get_next_set(edges, get_first, get_second):
    all_nodes = set()
    has_incoming = set()
    for edge in edges:
        all_nodes.add(get_first(edge))
        all_nodes.add(get_second(edge))
        has_incoming.add(get_second(edge))
    return all_nodes.difference(has_incoming)


def all_pairs(my_list):
    for i in range(len(my_list) - 1):
        for j in range(i + 1, len(my_list)):
            yield my_list[i], my_list[j]


school_list = [
    "NMH",
    "Nobles",
    "Brooks",
    "Winsor",
    "Cambridge RLS",
    "Groton",
    "Middlesex",
    "BB&N",
    "Taft",
    "Choate",
    "Greenwich Academy",
    "Hopkins",
    "St. Mark's",
    "Brewster Academy",
    "Lyme/Old Lyme",
    "Gunn School",
    "Marianapolis Prep",
    "Berkshire Academy",
    "Newton Country Day",
    "Valley Regional",
    "Bancroft",
    "Canterbury",
]


def gen_matrix(edges, school_list):
    nodes = sorted(getNodes(edges))
    res = {}
    for node in nodes:
        res[node] = {}
    for first in nodes:
        for second in nodes:
            head_to_heads = sorted(
                (
                    edge
                    for edge in edges
                    if sorted((edge.first, edge.second)) == sorted((first, second))
                ),
                key=lambda edge: edge.date,
                reverse=True,
            )
            if head_to_heads:
                edge = head_to_heads[0]
                res[edge.second][edge.first] = (
                    edge.adjusted_margin
                    if edge.adjusted_margin is not None
                    else edge.margin
                )

    nodes = sorted(
        nodes,
        key=lambda x: sum(map(lambda _: _ if _ is not None else 0, res[x].values())),
    )
    rows = []
    rows.append([""] + nodes)
    for node in nodes:
        row = [node]
        for node2 in nodes:
            if node2 in res[node]:
                row.append(res[node][node2])
            else:
                row.append("")
        rows.append(row)

    return rows


if __name__ == "__main__":
    print("starting")
    main()
