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

def getMargin(time1, time2):
    time1 = getTime(time1)
    time2 = getTime(time2)
    if time1 == None or time2 == None:
        return None
    return (time2 - time1).total_seconds()

def getTime(time):
    time = cleanTime(time)
    try:
        return datetime.datetime.strptime(time, "%M:%S.%f")
    except:
        try:
            return datetime.datetime.strptime(time, "%M.%S.%f")
        except:
            try:
                return datetime.datetime.strptime(time, "%M:%S")
            except:
                return None

def cleanTime(string):
    return string.replace("!", "1").replace(" ", "")

def main():
    results = []
    for filename in os.listdir('data'):
        with open(f"data/{filename}", "r") as f:
            scraped_json = json.load(f)
            day = scraped_json["day"]

            date = datetime.datetime.strptime(day, "%B %d, %Y")
            
            heats = scraped_json["heats"]
            regatta_display_name = scraped_json["regatta_display_name"]
            comment = scraped_json["comment"]
            url = scraped_json["url"]

            for heat in heats:
                class_ = heat["class"]
                gender = heat["gender"]
                varsity_index = heat["varsity_index"]
                heat_results = heat["results"]

                boatName = gender + str(varsity_index) + class_
                
                for i, fasterBoat in enumerate(heat_results[:-1]):
                    for slowerBoat in heat_results[i+1:]:
                        margin = getMargin(fasterBoat["time"], slowerBoat["time"])
                        fasterSchool, fasterSchoolBoatNum = matchSchool(fasterBoat["school"], boatNum=varsity_index)
                        slowerSchool, slowerSchoolBoatNum = matchSchool(slowerBoat["school"], boatNum=varsity_index)
                        if fasterSchool is None or slowerSchool is None:
                            # This means one of the schools was not recognized as a neira school
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
        (date, gender, boat, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url) = row
        if boat not in orders:
            orders[boat] = []
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        if gender + str(fasterBoat) not in boat:
            fasterSchool = fasterSchool + str(fasterBoat)
        if gender + str(slowerBoat) not in boat:
            slowerSchool = slowerSchool + str(slowerBoat)

        edge = Edge(date, fasterSchool, slowerSchool, margin)
        edge.url = url
        edge.tooltip = race + "\t\t\t\n" + comment
        orders[boat].append(edge)
        # orderEntry(orders, fasterSchool, fasterBoat)
        # orderEntry(orders, slowerSchool, slowerBoat)
        # orders[fasterSchool][fasterBoat].append(edge)
        # orders[slowerSchool][slowerBoat].append(edge)
        form = "{boat}: {faster} beat {slower} by {margin} seconds on {date}"
        print(form.format(date=str(date),
                            faster=fasterSchool,
                            slower=slowerSchool,
                            boat=boat,
                            margin=str(margin)))

    for boat in sorted(list(orders.keys()), key=sorter):
        #edges = removeCycles(orders[boat])
        edges = orders[boat]
        viz(boat, boat, edges)
        # try:
        #print("-" * 25)
        #print(boat + ":")
        # for school in seed(fromAssociationList(removeCycles(edges))):
        #     print school
        # for school in getNodes(edges):
        #     relevant = []
        #     for edge in edges:
        #         if edge.first == school or edge.second == school:
        #             relevant.append(edge)
        #             #            viz(boat, boat+school, relevant)
                    #        print len(allChains(fromAssociationList(removeCycles(edges))))

if __name__ == '__main__':
    main()
