import sys
sys.path.append("/Users/matt/workspace/neira_project/neira/src")

import urllib.request, urllib.parse, urllib.error
import sqlite3
from datetime import date
import datetime
from toDot import viz
from associationList import Edge
from associationList import removeCycles
from associationList import markCycles
from associationList import getNodes
from graph import fromAssociationList
from chains import seed

# faster: school
# slower: school
# boat: Ex: boys1 girls1 etc..
# date: 2016-05-24
# margin: Seconds difference (maybe should be real number)
# race: the name of the race that took place
# url: the url where the results were scraped

def sorter(string):
    if "boys" in string.lower():
        return "00" + string.lower()
    if "girls" in string.lower():
        return "0" + string.lower()
    else:
        return string.lower()

def orderEntry(orders, school, boat):
    if school not in list(orders.keys()):
        orders[school] = {}
    if boat not in list(orders[school].keys()):
        orders[school][boat] = []


if __name__ == '__main__':
    conn = sqlite3.connect('../bin/row2k.sqlite3')
    cur = conn.cursor()


    cur.execute("""
    SELECT date, gender, heat, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url FROM Results
    """)

    results = cur.fetchall()
    for result in results:
        print(result)
    (date, gender, heat, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url) = results[0]
    orders = {}
    nodes = {}
    for row in results:
        # print (date, gender, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url)
        (date, gender, boat, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url) = row
        if boat not in list(orders.keys()):
            orders[boat] = []
        if margin is None:
            continue
        if margin > 5:
            margin = int(margin)
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        if gender + str(fasterBoat) not in boat:
            fasterSchool = fasterSchool + str(fasterBoat)
        if gender + str(slowerBoat) not in boat:
            slowerSchool = slowerSchool + str(slowerBoat)

        edge = Edge(date, fasterSchool, slowerSchool, margin)
        edge.url = url
        edge.tooltip = race + "\t\t\t\n" + comment
        orders[boat].append(edge)
        orderEntry(orders, fasterSchool, fasterBoat)
        orderEntry(orders, slowerSchool, slowerBoat)
        orders[fasterSchool][fasterBoat].append(edge)
        orders[slowerSchool][slowerBoat].append(edge)
        form = "{boat}: {faster} beat {slower} by {margin} seconds on {date}"
        print(form.format(date=str(date),
                            faster=fasterSchool,
                            slower=slowerSchool,
                            boat=boat,
                            margin=str(margin)))

    for boat in sorted(list(orders.keys()), key=sorter):
        #edges = removeCycles(orders[boat])
        print(orders)
        edges = orders[boat]
        viz(boat, boat, edges)
        # try:
        print("-" * 25)
        print(boat + ":")
        # for school in seed(fromAssociationList(removeCycles(edges))):
        #     print school
        # for school in getNodes(edges):
        #     relevant = []
        #     for edge in edges:
        #         if edge.first == school or edge.second == school:
        #             relevant.append(edge)
        #             #            viz(boat, boat+school, relevant)
                    #        print len(allChains(fromAssociationList(removeCycles(edges))))
        input()

    conn.commit()
    cur.close()
