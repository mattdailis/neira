import csv
import json
import neira.scraper.clean


def founders_day():
    with open("founders-day-transcribed-2025.csv", "r") as f:
        reader = csv.DictReader(f)

        data = []

        row_1 = None
        for row_2 in reader:
            if row_1:
                data.append(
                    {
                        "Race": row_1["Race"],
                        "Boat": row_1["Boat"],
                        "results": [
                            {
                                "school": row_1[x],
                                "raw_time": row_2[x],
                            }
                            for x in ("1", "2", "3", "4", "5", "6")
                            if row_1[x] != ""
                        ],
                    }
                )
                row_1 = None
            else:
                row_1 = row_2

    heats = []
    for datum in data:
        if "H" in datum["Boat"]:
            heat_or_final = "heat"
        else:
            heat_or_final = "final"

        if datum["Boat"].startswith("B"):
            gender = "boys"
        elif datum["Boat"].startswith("G"):
            gender = "girls"
        else:
            raise Exception("Could not determine gender " + datum["Boat"])

        varsity_index = str(int(datum["Boat"][1]))

        results = []

        # Pick one arbitrarily to use as reference
        # Get all margins relative to it
        # Sort

        # Assume results has at least 1 element, and that there are no empty elements
        first_result = datum["results"][0]

        for result in datum["results"]:
            results.append(
                {
                    "school": result["school"],
                    "raw_time": result["raw_time"],
                    "margin_from_winner": neira.scraper.clean.get_margin(
                        first_result["raw_time"],
                        result["raw_time"],
                    ),
                }
            )

        def margin(x):
            if x["margin_from_winner"]:
                return x["margin_from_winner"]
            else:
                return 1000

        # Re-zero the margins, since it's likely that our reference point was not the winner
        results.sort(key=margin)
        min_margin = min(map(margin, results))
        for result in results:
            if result["margin_from_winner"] is not None:
                result["margin_from_winner"] -= min_margin
                result["margin_from_winner"] = round(result["margin_from_winner"], 2)
                if result["margin_from_winner"] == 0.0:
                    result["margin_from_winner"] = 0

        new_results = []
        schools = set()
        for result in results:
            school = neira.scraper.clean.clean_school(result["school"], "fours", gender)

            if school is None:
                continue

            if school in schools:
                continue

            schools.add(school)

            if new_results:
                margin_from_winner = neira.scraper.clean.get_margin(
                    new_results[0]["raw_time"], result["raw_time"]
                )
            else:
                margin_from_winner = 0

            if margin_from_winner is None:
                continue

            new_results.append(
                {
                    "school": school,
                    "raw_time": result["raw_time"],
                    "margin_from_winner": margin_from_winner,
                }
            )

        heats.append(
            {
                "class": "fours",  # TODO verify that they're all fours
                "gender": gender,
                "varsity_index": varsity_index,
                "results": new_results,
                "heat_or_final": heat_or_final,
                "Boat": datum["Boat"],
            }
        )

    # comment = "Conditions: Some cross wind in the first 500m shifting into a light tail wind in the last 1k. Teams with multiple boats in a single event only progressed the faster boat even if both finished top 3."
    comment = ""

    day = "2025-05-04"
    # url = "https://www.row2k.com/results/resultspage.cfm?UID=7AC6352FAB62A8BCE52618B8C7A7971D&cat=6"
    url = "https://www.row2k.com/results/resultspage.cfm?UID=9400921B2CB64E59B0F43EC7E58300B4&cat=6"

    with open("founders-day.json", "w") as f:
        json.dump(
            {
                "comment": comment,
                "day": day,
                "regatta_display_name": "Founder's Day Regatta",
                "url": url,
                "heats": heats,
            },
            f,
            indent=4,
            sort_keys=True,
        )

    all_head_to_head = []
    for gender in ("boys", "girls"):
        for varsity_index in ("1", "2", "3", "4", "5", "6"):
            print(gender + " " + varsity_index)
            head_to_head = []
            recorded_pairs = set()
            for heat in heats:
                if heat["gender"] != gender or heat["varsity_index"] != varsity_index:
                    continue
                if heat["heat_or_final"] == "final":
                    print("Processing " + heat["Boat"])
                    new = process_heat(recorded_pairs, heat)
                    for x in new:
                        print(
                            x["school1"]
                            + " beat "
                            + x["school2"]
                            + " by "
                            + str(x["margin"])
                            + " seconds"
                        )
                    head_to_head.extend(new)

            for heat in heats:
                if heat["gender"] != gender or heat["varsity_index"] != varsity_index:
                    continue
                if heat["heat_or_final"] == "heat":
                    print("Processing " + heat["Boat"])
                    new = process_heat(recorded_pairs, heat)
                    for x in new:
                        print(
                            x["school1"]
                            + " beat "
                            + x["school2"]
                            + " by "
                            + str(x["margin"])
                            + " seconds"
                        )
                    head_to_head.extend(new)

            all_head_to_head.append(
                {
                    "class": "fours",
                    "gender": gender,
                    "varsity_index": varsity_index,
                    "results": head_to_head,
                }
            )
    # write founders-day-head-to-head.json
    with open("founders-day-head-to-head.json", "w") as f:
        json.dump(
            {
                "comment": comment,
                "day": day,
                "regatta_display_name": "Founder's Day Regatta",
                "url": url,
                "head_to_head": all_head_to_head,
            },
            f,
            indent=4,
            sort_keys=True,
        )


def process_heat(recorded_pairs, heat):
    heat_head_to_head = []
    for result1 in heat["results"]:
        for result2 in heat["results"]:
            pair = tuple(sorted((result1["school"], result2["school"])))
            if result1 is not result2 and pair not in recorded_pairs:
                recorded_pairs.add(
                    tuple(sorted((result1["school"], result2["school"])))
                )
                margin = result1["margin_from_winner"] - result2["margin_from_winner"]
                if margin > 0:
                    heat_head_to_head.append(
                        {
                            "school1": result2["school"],
                            "school2": result1["school"],
                            "margin": round(margin, 2),
                        }
                    )
                else:
                    heat_head_to_head.append(
                        {
                            "school1": result1["school"],
                            "school2": result2["school"],
                            "margin": -round(margin, 2),
                        }
                    )
    return heat_head_to_head
