import urllib
import sqlite3
from datetime import date
import datetime
from toDot import viz
from associationList import Edge

from models import Heat


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
    for heat in Heat.objects.all():
        url = heat.url
        comment = heat.comment
        results = list(heat.result_set.all())
        date = heat.date
        results.sort(key=lambda x: x.time)
        for (i, result) in enumerate(results):
            faster_boat = result.boat
            boat = str(faster_boat.team) + str(faster_boat.level) + str(faster_boat.size)
            for otherResult in results[i+1:]:
                if otherResult.time.total_seconds() < 0 or result.time.total_seconds() < 0:
                    margin = None
                else:
                    margin = (otherResult.time - result.time).total_seconds()
                slower_boat = otherResult.boat

                if boat not in orders.keys():
                    orders[boat] = []
                if margin > 5:
                    margin = int(margin)

                edge = Edge(date, faster_boat.school.name, slower_boat.school.name, margin)
                edge.url = url
                edge.tooltip = comment
                orders[boat].append(edge)
                # orderEntry(orders, faster_boat.school.name, faster_boat.level)
                # orderEntry(orders, slower_boat.school.name, slower_boat.level)
                # orders[faster_boat.school.name][faster_boat.level].append(edge)
                # orders[slower_boat.school.name][slower_boat.level].append(edge)

    for boat in sorted(orders.keys(), key=sorter):
        edges = orders[boat]
        viz(boat, boat, edges)
        print "-" * 25
        print boat + ":"
        raw_input()
