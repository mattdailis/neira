import json
import os
import urllib.request, urllib.parse, urllib.error

from datetime import date
import datetime
from toDot import viz
from associationList import Edge
from associationList import removeCycles
from associationList import markCycles
from associationList import getNodes
from graph import fromAssociationList
from chains import seed
from neiraschools import matchSchool, matched, unmatched

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
    res = string.replace("!", "1").replace(" ", "").replace(";", ":").replace("..", ".").replace(",", ".")
    if ":" in res:
        parts = res.split(":")
        res = parts[0] + ":" + ".".join(parts[1:])
    return res

def main():
    results = []
    for filename in os.listdir('data'):
        print("Processing", filename)
        with open(f"data/{filename}", "r") as f:
            scraped_json = json.load(f)
        day = scraped_json["day"]

        date = datetime.datetime.strptime(day, "%B %d, %Y")
            
        heats = scraped_json["heats"]
        regatta_display_name = scraped_json["regatta_display_name"]
        comment = scraped_json["comment"]
        url = scraped_json["url"]

        try:
            distance = int(comment.split("Distance:")[1].split("Conditions")[0].strip().lower().rstrip(" meters").lstrip("approx. ").replace(",", ""))
        except Exception as e:
            print(e)
            distance = None

        for heat in heats:
            class_ = heat["class"]
            gender = heat["gender"]
            varsity_index = heat["varsity_index"]
            heat_results = heat["results"] # assume they're ordered?

            boatName = gender + str(varsity_index) + class_

            # take only fastest result by a given school
            new_heat_results = []
            seen_schools = set()
            for entry in heat_results:
                school, _ = matchSchool(entry["school"], boatNum=varsity_index)
                if school not in seen_schools:
                    seen_schools.add(school)
                    new_heat_results.append(entry)
                else:
                    continue
            heat_results = new_heat_results
            del new_heat_results
            del entry
            del school
            del _
            
            for fasterBoat, slowerBoat in all_pairs(heat_results):
                margin = getMargin(fasterBoat["time"], slowerBoat["time"])
                if distance == 1500:
                    adjusted_margin = None
                else:
                    adjusted_margin = round((1500.0 / distance) * margin, 2) if distance is not None and margin is not None else None
                fasterSchool, fasterSchoolBoatNum = matchSchool(fasterBoat["school"], boatNum=varsity_index)
                slowerSchool, slowerSchoolBoatNum = matchSchool(slowerBoat["school"], boatNum=varsity_index)
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
                    fasterSchoolName += " " + str(fasterSchoolBoatNum)
                slowerSchoolName = slowerSchool
                if slowerSchoolBoatNum != varsity_index:
                    slowerSchoolName += " " + str(slowerSchoolBoatNum)
                results.append((
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
                    url
                ))

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
        (date, gender, boat, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, adjusted_margin, race, comment, url) = row
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
        print(form.format(date=str(date),
                            faster=fasterSchool,
                            slower=slowerSchool,
                            boat=boat,
                            margin=str(margin)))

    for boat in sorted(list(orders.keys()), key=sorter):
        if "eight" in boat:
            continue
        edges = orders[boat]
        viz(boat, boat, edges)

        schools = {x.first for x in edges}
        schools.update({x.second for x in edges})

        for school in schools:
            viz(boat + school, boat + school, [edge for edge in edges if edge.first == school or edge.second == school])

        with open('../docs/' + boat + '_topo.txt', 'w') as f:
            res, edges, tail = topo_sort(edges)
            for x in res:
                print(x, file=f)
            
            if edges:
                print("Cycle detected: ", file=f, end="")
                print(edges, file=f)
            
            for x in tail:
                print(x, file=f)

def topo_sort(edges):
    res = []
    while True:
        # get nodes that have no incoming edges
        no_incoming = get_next_set(edges, lambda x: x.first, lambda x: x.second)
        
        if not no_incoming:
            break
        
        # add those nodes to the list
        res.append(no_incoming)
        
        # filter out edges that touch these nodes
        edges = [edge for edge in edges if edge.first not in no_incoming]

    tail = []
    if edges:
        # If we hit a cycle, try doing a topological sort from the bottom as well
        while True:
            # get nodes that have no incoming edges
            no_outgoing = get_next_set(edges, lambda x: x.second, lambda x: x.first) # swap first and second
        
            if not no_outgoing:
                break
        
            # add those nodes to the list
            tail.insert(0, no_outgoing)
        
            # filter out edges that touch these nodes
            edges = [edge for edge in edges if edge.second not in no_outgoing]

    remaining_nodes = set()
    for edge in edges:
        remaining_nodes.add(edge.first)
        remaining_nodes.add(edge.second)
    return res, remaining_nodes, tail


def get_next_set(edges, get_first, get_second):
    no_incoming = set()
    has_incoming = set()
    for edge in edges:
        first = get_first(edge)
        second = get_second(edge)
        has_incoming.add(second)
        if second in no_incoming:
            no_incoming.remove(second)
        if first not in has_incoming:
            no_incoming.add(first)
    return no_incoming

def all_pairs(my_list):
    for i in range(len(my_list) - 1):
        for j in range(i + 1, len(my_list)):
            yield my_list[i], my_list[j]
        
if __name__ == '__main__':
    print("starting")
    main()
