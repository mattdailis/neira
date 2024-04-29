"""
Input data: one file per page on row2k
Output data: one file per heat, plus a file for the raceday metadata
"""

import json
import os
import datetime

from os.path import basename, splitext

from neiraschools import matchSchool


def clean(scraped):
    """
    Take scraped data and clean it to ensure the following properties:
    - gender is boys or girls
    - class is fours or eights
    - varsity_index is 1-6 or novice
    - All school names are resolved to a set of known schools
    - All race times are valid
    - All dates are valid
    - No school appears in a heat twice
    """
    race_object = {
        "regatta_display_name": scraped["name"],
        "comment": scraped["comment"],
        "url": scraped["url"],
        "day": clean_date(scraped["date"]),
    }

    name = scraped["name"]

    # Guess the gender from the name, if possible. Else None
    gender = None
    if "boy" in name.lower() and not "girl" in name.lower():
        gender = "boys"
    elif "girl" in name.lower() and not "boy" in name.lower():
        gender = "girls"

    # Guess the boat size from the name. Else "fours"
    # TODO take into account what schools are participating - we know which ones row fours or eights
    boatSize = "fours"  # assume fours
    if (
        "eight" in name.lower()
        or "8" in name
        and not ("four" in name.lower() or "4" in name)
    ):
        boatSize = "eights"
    elif (
        "four" in name.lower()
        or "4" in name
        and not ("eight" in name.lower() or "8" in name)
    ):
        boatSize = "fours"

    heats = []
    for span in scraped["spans"]:
        if span["name"] and "women" in span["name"]:
            gender = "girls"
        elif span["name"] and "men" in span["name"]:
            gender = "boys"
        for heat in span["heats"]:
            (gender, boatNum, boatSize) = parseBoat(gender, boatSize, heat["heat"])
            school_times = []
            for x in heat["school_times"]:
                school = x["school"]
                time = x["time"]
                school_times.append(
                    {
                        "school": clean_school(school),
                        "time": clean_time(time),
                    }
                )
            heats.append(
                {
                    "class": str(boatSize),
                    "varsity_index": str(boatNum),
                    "results": school_times,
                    "gender": gender,
                }
            )

    race_object["heats"] = heats

    return race_object


def clean_maybe(data_raw, out_dir):
    """
    Read data from DATA_RAW and write it to OUT_DIR
    """
    for filename in os.listdir(data_raw):
        with open(os.path.join(data_raw, filename), "r") as f:
            race = json.load(f)

        prefix = splitext(basename(filename))[0]

        with open(os.path.join(out_dir, prefix + "-meta.json"), "w") as f:
            json.dump(
                {
                    "comment": race["comment"],
                    "date": clean_date(race["day"]),
                    "regatta_display_name": race["regatta_display_name"],
                    "url": race["url"],
                },
                f,
                indent=2,
            )

        for heat in race["heats"]:
            contents = []

            for result in heat["results"]:
                contents.append(
                    {
                        "school": clean_school(result["school"]),
                        "time": clean_time(result["time"]),
                    }
                )

            with open(
                os.path.join(
                    out_dir,
                    "-".join(
                        (
                            prefix,
                            clean_class(heat["class"]),
                            clean_gender(heat["gender"]),
                            clean_varsity_index(heat["varsity_index"]),
                        )
                    )
                    + ".json",
                ),
                "w",
            ) as f:
                json.dump(contents, f, indent=2)


def clean_time(time):
    return time


def clean_school(school):
    return matchSchool(school)[0]


def clean_gender(gender):
    if gender not in ("boys", "girls"):
        raise Exception("Unrecognized gender: " + gender)
    return gender


def clean_varsity_index(varsity_index):
    if varsity_index not in map(str, (1, 2, 3, 4, 5, 6)):
        raise Exception("Unrecognized varsity index: " + varsity_index)
    return varsity_index


def clean_class(class_):
    if class_ not in ("fours", "eights"):
        raise Exception("Unrecognized class: " + class_)
    return class_


def clean_date(date):
    return date


# string to date object
# Assumes format "Sunday, March 6, 2016"
def getDate(string):
    # f = "%A, %B %d, %Y"
    f = "%B %d, %Y"
    d = datetime.datetime.strptime(string, f).date()
    return d


def parseBoat(gender, boatSize, boatString):
    number = None
    if gender is None:
        if "g" in boatString.lower().replace("eig", ""):
            gender = "girls"
        elif "b" in boatString.lower():
            gender = "boys"

    if (
        "1" in boatString
        or "one" in boatString.lower()
        or "first" in boatString.lower()
        or "st" in boatString.lower()
    ):
        number = "1"
    elif (
        "2" in boatString
        or "two" in boatString.lower()
        or "second" in boatString.lower()
        or "nd" in boatString.lower()
    ):
        number = "2"
    elif "n" in boatString.lower().replace("nd", "").replace("ne", "").replace(
        "en", ""
    ):
        number = "novice"
    elif (
        "3" in boatString
        or "three" in boatString.lower()
        or "third" in boatString.lower()
        or "rd" in boatString.lower()
    ):
        number = "3"
    elif "fourth" in boatString.lower() or "4th" in boatString.lower():
        number = "4"
    elif (
        "5" in boatString
        or "five" in boatString.lower()
        or "fifth" in boatString.lower()
    ):
        number = "5"
    elif (
        "6" in boatString
        or "six" in boatString.lower()
        or "sixth" in boatString.lower()
    ):
        number = "6"
    elif "7" in boatString or "seven" in boatString.lower():
        number = "6"
    elif "4" in boatString or "four" in boatString.lower():
        number = "4"

    if number != "4" and ("4" in boatString or "four" in boatString.lower()):
        boatSize = "fours"
    elif "8" in boatString or "eight" in boatString.lower():
        boatSize = "eights"

    return (gender, number, boatSize)


if __name__ == "__main__":
    clean()
