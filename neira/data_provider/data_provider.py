from collections import namedtuple
import datetime
import json
import os
from typing import List


Datum = namedtuple(
    "Datum",
    "date gender boatName faster_boat faster_varsity_index slower_boat slower_varsity_index margin adjusted_margin regatta_display_name comment url",
)


def get(data_dir):
    all_heats = {}  # key: "class-gender-varsity_index"
    for class_ in ("eights", "fours"):
        for gender in ("girls", "boys"):
            for varsity_index in ("1", "2", "3", "4", "5", "6"):
                all_heats["-".join((class_, gender, varsity_index))] = []
    for filename in os.listdir(data_dir):
        with open(os.path.join(data_dir, filename), "r") as f:
            scraped_json = json.load(f)

        heats = scraped_json["heats"]
        for heat in heats:
            heat["url"] = scraped_json["url"]
            heat["regatta_display_name"] = scraped_json["regatta_display_name"]
            heat["comment"] = scraped_json["comment"]
            heat["date"] = scraped_json["day"]
            all_heats[
                "-".join((heat["class"], heat["gender"], heat["varsity_index"]))
            ].append(heat)

    return all_heats


def founders_day_head_to_head_tuples():
    with open("founders-day-head-to-head.json", "r") as f:
        founders_day_head_to_head = json.load(f)
    results = []
    for entry in founders_day_head_to_head["head_to_head"]:
        for head_to_head in entry["results"]:
            results.append(
                Datum(
                    founders_day_head_to_head["day"],
                    entry["gender"],
                    entry["gender"] + entry["varsity_index"] + entry["class"],
                    head_to_head["school1"],
                    entry["varsity_index"],
                    head_to_head["school2"],
                    entry["varsity_index"],
                    head_to_head["margin"],
                    None,
                    founders_day_head_to_head["regatta_display_name"],
                    founders_day_head_to_head["comment"],
                    founders_day_head_to_head["url"],
                )
            )

    return results


def get_head_to_head_tuples(data_dir, class_=None, gender=None) -> List[Datum]:
    filter_class = class_
    filter_gender = gender
    del class_, gender
    results = []
    for filename in os.listdir(data_dir):
        with open(os.path.join(data_dir, filename), "r") as f:
            scraped_json = json.load(f)
        day = scraped_json["day"]

        date = datetime.datetime.strptime(day, "%Y-%m-%d")

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
                .replace("~", "")
                .split()[0]
                .rstrip("m")
            )
        except Exception as e:
            print(e)
            distance = None

        for heat in heats:
            class_ = heat["class"]
            gender = heat["gender"]
            varsity_index = heat["varsity_index"]
            heat_results = heat["results"]  # assume they're ordered?

            if filter_class is not None and class_ != filter_class:
                continue
            if filter_gender is not None and gender != filter_gender:
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
                if (
                    slowerBoat["margin_from_winner"] is not None
                    and fasterBoat["margin_from_winner"] is not None
                ):
                    margin = round(
                        slowerBoat["margin_from_winner"]
                        - fasterBoat["margin_from_winner"],
                        1,
                    )
                else:
                    margin = None
                if distance == 1500:
                    adjusted_margin = None
                else:
                    adjusted_margin = (
                        round((1500.0 / distance) * margin, 2)
                        if distance is not None and margin is not None
                        else None
                    )

                results.append(
                    Datum(
                        date.strftime("%Y-%m-%d"),
                        gender,
                        boatName,
                        fasterBoat["school"],
                        varsity_index,
                        slowerBoat["school"],
                        varsity_index,
                        margin,
                        adjusted_margin,
                        regatta_display_name,
                        comment,
                        url,
                    )
                )
    results.extend(founders_day_head_to_head_tuples())
    return results


def all_pairs(my_list):
    for i in range(len(my_list) - 1):
        for j in range(i + 1, len(my_list)):
            yield my_list[i], my_list[j]
