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
    if len(boats) == 0:
        print "Empty"
        return []
    edges = []
    for boat in boats:
        results = boat.result_set.all()
        for result in results:
            heat = result.heat
            other_results = sorted(heat.result_set.all(), key=lambda r: r.time.total_seconds() if r.time is not None and r.time.total_seconds() > 0 else float("inf"))
            start_index = other_results.index(result)
            school_name = boat.school.primary_name()
            for other_result in other_results[start_index+1:]:
                other_boat = other_result.boat
                if other_boat in boats:  # potentially slow check
                    margin = get_margin(result, other_result)
                    print school_name, "beat", other_result.boat.school.primary_name(), "by", margin, "seconds"
                    edge = Edge(heat.date, school_name, other_result.boat.school.primary_name(), margin)
                    edge.url = heat.url
                    edge.tooltip = boat.school.name + " ----> " + other_boat.school.name + "\n" + heat.comment
                    edges.append(edge)
    return edges

def get_margin(r1, r2):
    if r1.time is None or r2.time is None:
        return None
    if r1.time.total_seconds() < 0 or r2.time.total_seconds() < 0:
        return None
    return abs((r1.time - r2.time).total_seconds())


def main_by_boat_class():
    all_boats = Boat.objects.all()
    # if school is not None:
    #     all_boats = filter(lambda x: x.school.get_primary() == school, all_boats)
    #     print all_boats
    orders = {}
    for size in ["four", "eight"]:
        for team in ["boys", "girls"]:
            for level in range(6):
                boats = filter(lambda boat: boat.size == size and boat.team == team and boat.level == level, all_boats)
                if len(boats) > 0:
                    print "\nReading", team, level, size, "\n-----"
                    key = str(team) + str(level) + str(size)
                    edges = get_edges(boats)
                    orders[key] = edges
                    for school in School.primaries.all():
                        name = school.primary_name()
                        key = str(team) + str(level) + str(size) + (school.primary_name() if school is not None else "")
                        orders[key] = filter(lambda edge: name == edge.first or name == edge.second, edges)

    return orders


def edges_between_boats(boats):
    edges = []
    for boat in boats:
        all_results = boat.result_set.all()
        for my_result in all_results:
            results = my_result.heat.result_set.all()
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


# def main_by_heat():
#     orders = {}
#     for heat in Heat.objects.all():
#         url = heat.url
#         comment = heat.comment
#         results = list(heat.result_set.all())
#         date = heat.date
#         if results:
#             faster_boat = results[0].boat.team
#             boat = str(faster_boat.team) + str(faster_boat.level) + str(faster_boat.size)
#             if boat not in orders:
#                 orders[boat] = []
#             orders[boat].extend(edges_from_results(results))
#
#     return orders


# def main_by_school():
#     orders = {}
#     boats = filter(lambda r: r.boat.school.get_primary() == school, all_results)
#         if school.name not in orders:
#             orders[school.name] = []
#         orders[school.name].extend(edges_from_results(results))
#     return orders
                

def gen(orders):
    for boat in sorted(orders.keys(), key=sorter):
        print "-" * 25
        print boat + ":"
        # raw_input()
        edges = orders[boat]
        viz(boat, boat, edges)



def main():
    gen(main_by_boat_class())
