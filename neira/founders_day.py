import csv
import json
import neira.scraper.clean
from neira.scraper.neiraschools import match_school


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
                "date": day,
                "name": "Founder's Day Regatta",
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
                "date": day,
                "name": "Founder's Day Regatta",
                "name": "Founder's Day Regatta",
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


def main():
    result = {"heats": [],
              "location": "Lake Waramaug, CT",
              "comment": """Conditions: Competing Programs: Hotchkiss, Berkshire, Miss Porter’s Canterbury, Rumsey Hall, Hopkins, Lyme/Old Lyme, Greenwich Academy, Choate, Northfield Mount Hermon, Taft, Suffield, Brewster, Notre Dame West Haven, Pomfret, Gunn A very windy day on Lake Waramaug led to first a pause in racing and then, following a restart with a truncated, ‘straight final’ format, an early conclusion also due to wind. Girls’ and Boys’ 4V and Girls’ 3V ran as scheduled in the morning, after which point racing paused. The regatta resumed following a resolution to start with both flights of girls’ 1V, then boys 1V, then girls’ 2V, then boys’ 2V, with a possibility of getting to the boys’ 3V, all without afternoon finals; girls’ and boys’ 1V and girls’ 2V were able to get their one race each despite headwinds building again in each successive race before racing ultimately ended for the day. Stiff and steady AM headwinds built finally to 10+ knots in the morning with gusts far in excess of that, leading to chop increasing drastically from the finish up to the start; upon resumption of racing after the morning pause, the first girls’ 1V race featured relatively clean water with a steady headwind before wind speeds built again to 10+ knots with gusts, chop and white caps by the end of the race day. Thank you to all programs for coming out and being so patient with Gunn’s regatta staff as we navigated some very tricky conditions and decisions. Here's to a calm, sunny day next year.""",
              "name": "NEIRA Boys & Girls Fours, Founders Day Regatta",
              "url": "https://www.row2k.com/results/resultspage.cfm?UID=AD1DB8B7FF440FDBF5A8B2F0C30E70D1&cat=6",
              "date": "2026-05-03"
              }
    with open("founders-2026.json", "r") as f:
        data = json.load(f)
        for heat in data:
            if heat["heat"].startswith("B"):
                gender = "boys"
            elif heat["heat"].startswith("G"):
                gender = "girls"
            else:
                raise ValueError("Could not guess gender from: " + str(heat["heat"]))
            
            varsity_index = heat["heat"][1]
            int(varsity_index)

            result["heats"].append({
                "class": "fours",
                "gender": gender,
                "varsity_index": varsity_index,
                "results": [],
            })

            tmp_results = []

            for results in heat["results"]:
                school = results["school"]
                time = results["time"]

                if "(G5)" in school or "(B)" in school:
                    continue

                neira_school = match_school(school, "fours", gender)

                if neira_school is None:
                    print("Could not match ", school)
                    continue

                school = neira_school  #f"{school} ({neira_school})"

                tmp_results.append((neira.scraper.clean.getTime(time), {
                    "school": school,
                    "raw_time": time,
                }))

            tmp_results.sort(key=lambda x: x[0])

            winning_time = tmp_results[0][0]
            for (i, (t, r)) in enumerate(tmp_results):
                r["finish_order"] = i + 1
                r["margin_from_winner"] = (t - winning_time).total_seconds()
                result["heats"][-1]["results"].append(r)
            

    filename = "data/1_parsed/AD1DB8B7FF440FDBF5A8B2F0C30E70D1.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=4)
    print("Wrote", filename)
    
    filename = "data/2_cleaned/AD1DB8B7FF440FDBF5A8B2F0C30E70D1.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=4)
    print("Wrote", filename)

if __name__ == "__main__":
    main()
