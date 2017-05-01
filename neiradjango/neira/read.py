import urllib
import sqlite3
from datetime import date
import datetime
from toDot import viz
from associationList import Edge

from models import Heat, Boat, Result, School


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

# QuerySet of Boats -> List of Edges
def get_edges(boats):
    if boats.count() == 0:
        return []
    edges = []
    for boat in boats:
        results = boat.result_set.all()
        for result in results:
            heat = result.heat
            other_results = sorted(heat.result_set.all(), key=lambda r: r.time.total_seconds() if r.time.total_seconds() > 0 else float("inf"))
            start_index = other_results.index(result)
            school_name = boat.school.primary_name()
            for other_result in other_results[start_index+1:]:
                other_boat = other_result.boat
                if other_boat in boats:  # potentially slow check
                    margin = get_margin(result, other_result)
                    print school_name, "beat", other_result.boat.school.primary_name(), "by", margin, "seconds"
                    edge = Edge(heat.date, school_name, other_result.boat.school.primary_name(), margin)
                    edge.url = heat.url
                    edge.tooltip = heat.comment
                    edges.append(edge)
    return edges

def get_margin(r1, r2):
    if r1.time.total_seconds() < 0 or r2.time.total_seconds() < 0:
        return None
    return abs((r1.time - r2.time).total_seconds())

def main_by_boat_class():
    orders = {}
    for size in ["four", "eight"]:
        for team in ["boys", "girls"]:
            for level in range(6):
                boats = Boat.objects.filter(size=size, team=team, level=level)
                if (boats.count() > 0):
                    print "\nReading", team, level, size, "\n-----"
                key = str(team) + str(level) + str(size)
                orders[key] = get_edges(boats)

    return orders

def edges_from_results(results):
    edges = []
    results = sorted(results, key=lambda x: x.time)
    for (i, result) in enumerate(results):
        faster_boat = result.boat
        for otherResult in results[i+1:]:
            if otherResult.time.total_seconds() < 0 or result.time.total_seconds() < 0:
                margin = None
            else:
                margin = (otherResult.time - result.time).total_seconds()
                slower_boat = otherResult.boat
                
                if margin > 5:
                    margin = int(margin)
                
                edge = Edge(result.heat.date, faster_boat.school.primary_name(), slower_boat.school.primary_name(), margin)
                edge.url = result.heat.url
                edge.tooltip = result.heat.comment
                edges.append(edge)
    return edges


def main_by_heat():
    orders = {}
    for heat in Heat.objects.all():
        url = heat.url
        comment = heat.comment
        results = list(heat.result_set.all())
        date = heat.date
        if results:
            faster_boat = results[0].boat.team
            boat = str(faster_boat.team) + str(faster_boat.level) + str(faster_boat.size)
            if boat not in orders:
                orders[boat] = []
            orders[boat].extend(edges_from_results(results))

    return orders


def main_by_school():
    orders = {}
    all_results = Result.objects.all()
    for school in School.primaries.all():
        results = filter(lambda r: r.boat.school.get_primary() == school, all_results)
        for result in results:
            if not school.name in orders:
                orders[school.name] = []
            orders[school.name].extend(edges_from_results(results))

    return orders
                

def main():
    orders = main_by_school()  # boat_class()
    for boat in sorted(orders.keys(), key=sorter):
        print "-" * 25
        print boat + ":"
        # raw_input()
        edges = orders[boat]
        viz(boat, boat, edges)
