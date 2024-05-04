import json
import os
from pprint import pprint
import neira.data_provider.data_provider as data
from tabulate import tabulate

from neira.scraper.neiraschools import girls_fours


def head_to_head(data_dir, html_dir):
    all_heats = data.get(data_dir)
    heats_by_date = {}
    counters = {}
    for boat in ("fours-girls-1", "fours-girls-2", "fours-girls-3", "fours-girls-4"):
        heats = all_heats[boat]
        counter = {}
        for heat in heats:
            for result in heat["results"]:
                school = result["school"]
                if school not in counter:
                    counter[school] = 0
                counter[school] += 1

            if not heat["date"] in heats_by_date:
                heats_by_date[heat["date"]] = {}

            if not heat["url"] in heats_by_date[heat["date"]]:
                heats_by_date[heat["date"]][heat["url"]] = {}

            if boat not in heats_by_date[heat["date"]][heat["url"]]:
                heats_by_date[heat["date"]][heat["url"]][boat] = []

            heats_by_date[heat["date"]][heat["url"]][boat].append(heat)
        counters[boat] = counter

    table = []
    for i, school in enumerate(sorted(girls_fours)):
        row = [
            i + 1,
            school,
            counters["fours-girls-1"].get(school, 0),
            "",
            counters["fours-girls-2"].get(school, 0),
            "",
            counters["fours-girls-3"].get(school, 0),
            "",
            counters["fours-girls-4"].get(school, 0),
            "",
        ]
        table.append(row)

    table.append([""] * 11)
    table.append(
        [
            "",
            "Results",
            "1st girls",
            "Time",
            "2nd girls",
            "Time",
            "3rd girls",
            "Time",
            "4th girls",
            "Time",
        ]
    )

    for date, heats_by_race in sorted(heats_by_date.items()):
        first = True
        for race, heats in heats_by_race.items():
            columns = []
            if first:
                columns.append([date])
                first = False
            else:
                columns.append([])
            for boat in (
                "fours-girls-1",
                "fours-girls-2",
                "fours-girls-3",
                "fours-girls-4",
            ):
                school_column = []
                time_column = []
                for heat in heats.get(boat, []):
                    for result in heat["results"]:
                        school_column.append(result["school"])
                        time_column.append(result["raw_time"])
                    school_column.append("")
                    time_column.append("")
                columns.append(school_column)
                columns.append(time_column)
            while any(column for column in columns):
                row = []
                for column in columns:
                    if len(column) > 0:
                        row.append(column.pop(0))
                    else:
                        row.append("")
                table.append(row)
        table.append("-" * 11)

    print(tabulate(table))

    with open(os.path.join(html_dir, "fours-girls.html"), "w") as f:
        f.write(tabulate(table, tablefmt="html"))

    import csv

    with open("head-to-head.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(table)
    # date
    # school time
    # space
    # school time
