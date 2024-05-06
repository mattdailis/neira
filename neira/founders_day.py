import csv
import json
import neira.scraper.clean


def founders_day():
    with open("founders-day-transcribed.csv", "r") as f:
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

    print(json.dumps(data, indent=2))

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
        # TODO sort

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
            }
        )

    print(json.dumps(heats, indent=2))

    with open("founders-day.json", "w") as f:
        json.dump(
            {
                "comment": "Conditions: Some cross wind in the first 500m shifting into a light tail wind in the last 1k. Teams with multiple boats in a single event only progressed the faster boat even if both finished top 3.",
                "day": "2024-05-05",
                "regatta_display_name": "Founder's Day Regatta",
                "url": "https://www.row2k.com/results/resultspage.cfm?UID=7AC6352FAB62A8BCE52618B8C7A7971D&cat=6",
                "heats": heats,
            },
            f,
            indent=4,
            sort_keys=True,
        )
