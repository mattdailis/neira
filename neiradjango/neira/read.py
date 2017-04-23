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
        for (i, result) in enumerate(results)[:-1]:
            fasterBoat = result.boat
            boat = str(fasterBoat.team) + str(fasterBoat.level) + str(fasterBoat.size)
            for otherResult in results[i+1:]:
                t1, t2 = otherResult.time, result.time

                t1_ms = (t1.hour*60*60 + t1.minute*60 + t1.second)*1000 + t1.microsecond
                t2_ms = (t2.hour*60*60 + t2.minute*60 + t2.second)*1000 + t2.microsecond

                margin = (max([t1_ms, t2_ms]) - min([t1_ms, t2_ms]))/1000
                slowerBoat = otherResult.boat

    #
    # for row in results:
    #     # print (date, gender, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url)
    #     (date, gender, boat, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url) = row
                if boat not in orders.keys():
                    orders[boat] = []
                if margin > 5:
                    margin = int(margin)
                # date = datetime.datetime.strptime(date, "%Y-%m-%d")
        # if gender + str(fasterBoat) not in boat:
        #     fasterSchool = fasterSchool + str(fasterBoat)
        # if gender + str(slowerBoat) not in boat:
        #     slowerSchool = slowerSchool + str(slowerBoat)

                edge = Edge(date, fasterBoat.school.name, slowerBoat.school.name, margin)
                edge.url = url
                edge.tooltip = comment # race + "\t\t\t\n" + comment
                orders[boat].append(edge)
                orderEntry(orders, fasterBoat.school.name, fasterBoat.level)
                orderEntry(orders, slowerBoat.school.name, slowerBoat.level)
                orders[fasterBoat.school.name][fasterBoat.level].append(edge)
                orders[slowerBoat.school.name][slowerBoat.level].append(edge)
                form = "{boat}: {faster} beat {slower} by {margin} seconds on {date}"
                print form.format(date=str(date),
                                faster=fasterBoat.school.name,
                                slower=slowerBoat.school.name,
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
