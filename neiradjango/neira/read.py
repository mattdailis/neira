import urllib
import sqlite3
from datetime import date
import datetime
from toDot import viz
from associationList import Edge

from models import Heat

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
    if school not in orders.keys():
        orders[school] = {}
    if boat not in orders[school].keys():
        orders[school][boat] = []


def main():
    orders = {}
    nodes = {}
    for heat in Heat.objects.all():
        url = heat.url
        comment = heat.comment
        results = list(heat.result_set.all())
        date = heat.date
        results.sort(key=lambda x: x.time)
        for (i, result) in enumerate(results):
            fasterBoat = result.boat
            boat = str(fasterBoat.team) + str(fasterBoat.level) + str(fasterBoat.size)
            for otherResult in results[i+1:]:
                if otherResult.time.total_seconds() < 0 or result.time.total_seconds < 0:
                    margin = None
                else:
                    margin = (otherResult.time - result.time).total_seconds()
                slower_boat = otherResult.boat

    #
    # for row in results:
    #     # print (date, gender, fasterSchool, fasterBoat, slowerSchool, slower_boat, margin, race, comment, url)
    #     (date, gender, boat, fasterSchool, fasterBoat, slowerSchool, slower_boat, margin, race, comment, url) = row
                if boat not in orders.keys():
                    orders[boat] = []
                if margin > 5:
                    margin = int(margin)
                # date = datetime.datetime.strptime(date, "%Y-%m-%d")
        # if gender + str(fasterBoat) not in boat:
        #     fasterSchool = fasterSchool + str(fasterBoat)
        # if gender + str(slower_boat) not in boat:
        #     slowerSchool = slowerSchool + str(slower_boat)

                edge = Edge(date, fasterBoat.school.name, slower_boat.school.name, margin)
                edge.url = url
                edge.tooltip = comment # race + "\t\t\t\n" + comment
                orders[boat].append(edge)
                orderEntry(orders, fasterBoat.school.name, fasterBoat.level)
                orderEntry(orders, slower_boat.school.name, slower_boat.level)
                orders[fasterBoat.school.name][fasterBoat.level].append(edge)
                orders[slower_boat.school.name][slower_boat.level].append(edge)
                form = "{boat}: {faster} beat {slower} by {margin} seconds on {date}"
                print form.format(date=str(date),
                                faster=fasterBoat.school.name,
                                slower=slower_boat.school.name,
                                boat=boat,
                                margin=str(margin))

    for boat in sorted(orders.keys(), key=sorter):
        #edges = removeCycles(orders[boat])
        print orders
        edges = orders[boat]
        viz(boat, boat, edges)
        # try:
        print "-" * 25
        print boat + ":"
        # for school in seed(fromAssociationList(removeCycles(edges))):
        #     print school
        # for school in getNodes(edges):
        #     relevant = []
        #     for edge in edges:
        #         if edge.first == school or edge.second == school:
        #             relevant.append(edge)
        #             #            viz(boat, boat+school, relevant)
                    #        print len(allChains(fromAssociationList(removeCycles(edges))))
        raw_input()
