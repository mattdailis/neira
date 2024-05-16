from collections import namedtuple
import csv
import datetime
from itertools import permutations
import json
from math import factorial
import os
from pprint import pprint
from random import shuffle
from typing import List
import neira.data_provider.data_provider as data
from tabulate import tabulate
from tqdm import tqdm

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


Problem = namedtuple("Problem", "ranking head_to_head meets_minimum_races path2")


def rank_by_most_recent_head_to_head(data_dir):
    # for each class/gender/varsity index
    # filter data to only the most recent head-to-head matchup between every pair of schools
    # randomize order (using deterministic seed)
    # Iterate until no progress is made:
    # Identify conflicts
    # Choose a conflict to repair
    # Repair

    tuples: List[data.Datum] = data.get_head_to_head_tuples(data_dir)

    for class_ in ("fours",):
        for gender in ("girls",):
            for varsity_index in ("4",):  # "1", "2", "3",
                boatName = gender + varsity_index + class_
                print(boatName)
                filtered_tuples = [x for x in tuples if x.boatName == boatName]

                schools = set()
                for x in filtered_tuples:
                    schools.add(x.faster_boat)
                    schools.add(x.slower_boat)

                school_dates = {school: set() for school in schools}
                for x in filtered_tuples:
                    school_dates[x.faster_boat].add(x.date)
                    school_dates[x.slower_boat].add(x.date)

                meets_minimum_races = {
                    school: len(school_dates[school]) > 0
                    for school in schools  # TODO how to incorporate minimum
                }

                head_to_head = dict()
                # margin = right school time minus left school time

                for x in filtered_tuples:
                    put_margin(
                        head_to_head, x.faster_boat, x.slower_boat, x.margin, x.date
                    )

                path2 = dict()
                for (school1, school2), (date1, margin1) in head_to_head.items():
                    for (school3, school4), (date2, margin2) in head_to_head.items():
                        if school2 == school3:
                            put_margin(
                                path2,
                                school1,
                                school4,
                                margin1 + margin2,
                                min(date1, date2),
                            )
                        if school1 == school3:
                            put_margin(
                                path2,
                                school2,
                                school4,
                                margin2 - margin1,
                                min(date1, date2),
                            )
                        if school1 == school4:
                            put_margin(
                                path2,
                                school3,
                                school2,
                                margin1 + margin2,
                                min(date1, date2),
                            )
                        if school2 == school4:
                            put_margin(
                                path2,
                                school1,
                                school3,
                                margin1 - margin2,
                                min(date1, date2),
                            )

                # best_option = min(
                #     tqdm(
                #         (
                #             objective_function(Problem(permutation, head_to_head))
                #             for permutation in permutations(schools)
                #         ),
                #         total=factorial(len(schools)),
                #     )
                # )
                # print(best_option.ranking)
                # print(objective_function(Problem(best_option, head_to_head)))

                best_ranking = sorted(list(schools))
                alternatives = []
                best_objective = objective_function(
                    Problem(best_ranking, head_to_head, meets_minimum_races, path2)
                )

                for _ in tqdm(range(300)):
                    schools_copy = list(schools)
                    shuffle(schools_copy)
                    problem = Problem(
                        schools_copy,
                        head_to_head,
                        meets_minimum_races,
                        path2,
                    )

                    result = iterative_repair(
                        problem, get_conflicts, objective_function, (move_up, move_down)
                    )

                    new_objective = objective_function(result)
                    if (
                        new_objective == best_objective
                        and result.ranking != best_ranking
                    ):
                        alternatives.append(result.ranking)
                    if new_objective > best_objective:
                        best_objective = new_objective
                        best_ranking = result.ranking
                        alternatives = []
                        print(best_objective)
                        print(best_ranking)

                print("Finished")

                print(
                    "There were "
                    + str(len(alternatives) + 1)
                    + " equally viable alternatives"
                )

                print()
                print(best_objective)
                table = list(zip(best_ranking, *alternatives))
                table.insert(18, ("---------",) * (1 + len(alternatives)))

                print(tabulate(table))

                conflicts = get_conflicts(
                    Problem(best_ranking, head_to_head, meets_minimum_races, path2)
                )
                print(conflicts)

                print()
                print(repr(problem.head_to_head))

                # head_to_head_no_conflicts = dict(head_to_head)
                # for conflict in conflicts:
                #     if (conflict[0], conflict[1]) in head_to_head_no_conflicts:
                #         del head_to_head_no_conflicts[(conflict[0], conflict[1])]
                #     elif (conflict[1], conflict[0]) in head_to_head_no_conflicts:
                #         del head_to_head_no_conflicts[(conflict[1], conflict[0])]

                # incoming_edge_counters = {school: 0 for school in schools}
                # for (
                #     school1,
                #     school2,
                # ), (date, margin) in head_to_head_no_conflicts.items():
                #     if margin > 0:
                #         incoming_edge_counters[school2] += 1
                #     elif margin < 0:
                #         incoming_edge_counters[school1] += 1

                # tiers = []
                # while incoming_edge_counters:
                #     tier = []
                #     for school, count in list(incoming_edge_counters.items()):
                #         if count == 0:
                #             tier.append(school)
                #             del incoming_edge_counters[school]
                #     for school in tier:
                #         for (
                #             school1,
                #             school2,
                #         ), (date, margin) in head_to_head_no_conflicts.items():
                #             if margin > 0 and school == school1:
                #                 incoming_edge_counters[school2] -= 1
                #             elif margin < 0 and school == school2:
                #                 incoming_edge_counters[school1] -= 1
                #     tiers.append(tier)

                # for i, tier in enumerate(tiers):
                #     print(str(i + 1) + ": " + ", ".join(sorted(tier)))

                def fiddle():
                    beat = {school: [] for school in schools}
                    for (school1, school2), (date, margin) in head_to_head.items():
                        if margin > 0:
                            beat[school1].append((school2, margin))
                        if margin < 0:
                            beat[school2].append((school1, -margin))

                    potential_energy = get_potential_energy(best_ranking, beat)

                    for i, school in enumerate(best_ranking):
                        print(
                            str(i + 1)
                            + ": "
                            + school
                            + " ("
                            + str(round(potential_energy[school], 2))
                            + ") "
                            + repr(beat[school])
                        )

                    conflicts = set(conflicts)

                    total_potential_energy = sum(potential_energy.values())

                    current_ranking = best_ranking
                    previous_ranking = None
                    while previous_ranking != current_ranking:
                        previous_ranking = current_ranking
                        for school, _ in sorted(
                            potential_energy.items(), key=lambda x: -x[1]
                        ):
                            school_index = current_ranking.index(school)
                            if school_index == 0:
                                continue
                            new_ranking = list(current_ranking)
                            new_ranking[school_index] = new_ranking[school_index - 1]
                            new_ranking[school_index - 1] = school

                            new_potential_energy = get_potential_energy(
                                new_ranking, beat
                            )

                            if (
                                sum(new_potential_energy.values())
                                >= total_potential_energy
                            ):
                                continue

                            if (
                                objective_function(
                                    Problem(
                                        new_ranking,
                                        head_to_head,
                                        meets_minimum_races,
                                        path2,
                                    )
                                )
                                < best_objective
                            ):
                                continue

                            print("Bumped up " + school)
                            current_ranking = new_ranking
                            potential_energy = new_potential_energy
                            total_potential_energy = sum(new_potential_energy.values())
                            print(total_potential_energy)
                            break

                    print("-" * 25)

                    for i, school in enumerate(current_ranking):
                        print(
                            str(i + 1)
                            + ": "
                            + school
                            + " ("
                            + str(round(potential_energy[school], 2))
                            + ") "
                            + repr(beat[school])
                        )

                    table = list(
                        zip(
                            best_ranking,
                            map(
                                lambda x: (
                                    x
                                    + (
                                        (
                                            " ("
                                            + (
                                                "+"
                                                if best_ranking.index(x)
                                                > current_ranking.index(x)
                                                else ""
                                            )
                                            + str(
                                                best_ranking.index(x)
                                                - current_ranking.index(x)
                                            )
                                            + ")"
                                        )
                                        if best_ranking.index(x)
                                        != current_ranking.index(x)
                                        else ""
                                    )
                                ),
                                current_ranking,
                            ),
                        )
                    )
                    # table.insert(18, ("----------", "----------"))

                    # print(
                    #     tabulate(
                    #         table,
                    #         headers=("Original", "After Adjusting"),
                    #     )
                    # )

                    best_ranking = current_ranking

                rows = []
                rows.append([FORMULA] + best_ranking)
                for school1 in best_ranking:
                    row = [school1]
                    for school2 in best_ranking:
                        if (school2, school1) in head_to_head and head_to_head[
                            (school2, school1)
                        ][1] > 0:
                            row.append(head_to_head[(school2, school1)][1])
                        elif (school1, school2) in head_to_head and head_to_head[
                            (school1, school2)
                        ][1] < 0:
                            row.append(-head_to_head[(school1, school2)][1])
                        else:
                            row.append("")
                    rows.append(row)
                with open(
                    f"head-to-head-{class_}-{gender}-{varsity_index}.csv", "w"
                ) as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)


def get_potential_energy(ranking, beat):
    potential_energy = {}
    for school in ranking:
        this_ranking = ranking.index(school) + 1
        potential_energy[school] = len(beat[school])
        for other_school, margin in beat[school]:
            other_ranking = ranking.index(other_school) + 1
            potential_energy[school] += max(
                0, (margin / 5) - (other_ranking - this_ranking)
            )

    for _ in range(10):
        old_potential_energy = dict(potential_energy)
        for school in ranking:
            this_ranking = ranking.index(school) + 1
            for other_school, margin in beat[school]:
                other_ranking = ranking.index(other_school) + 1
                potential_energy[school] += max(
                    0,
                    (old_potential_energy[other_school] / 5)
                    - (other_ranking - this_ranking),
                )

    return potential_energy


def objective_function(problem):
    conflicts = get_conflicts(problem)
    if not conflicts:
        return (0, 0, 0)
    date = datetime.datetime.strptime(max(x.date for x in conflicts), "%Y-%m-%d")
    # favor conflicts that are further in the past

    conflicts_by_level = dict()
    for level in (CONFLICT_LEVEL._1, CONFLICT_LEVEL._2):
        conflicts_by_level[level] = []

    for conflict in conflicts:
        conflicts_by_level[conflict.level].append(conflict)

    return (
        (
            -len(conflicts_by_level[CONFLICT_LEVEL._1]),
            -len(conflicts_by_level[CONFLICT_LEVEL._2]),
        ),
        -date.timestamp(),
        (
            sum(x.margin for x in conflicts_by_level[CONFLICT_LEVEL._1]),
            sum(x.margin for x in conflicts_by_level[CONFLICT_LEVEL._2]),
        ),
    )


def get_margin_and_date(head_to_head, school1, school2):
    """
    margin > 0 means that school1 beat school2
    """
    if (school1, school2) in head_to_head:
        return head_to_head[(school1, school2)][1], head_to_head[(school1, school2)][0]
    if (school2, school1) in head_to_head:
        return -head_to_head[(school2, school1)][1], head_to_head[(school2, school1)][0]


def put_margin(head_to_head, faster_boat, slower_boat, margin, date):
    """
    school1 beat school2 by margin
    """
    if faster_boat > slower_boat:
        pair = (slower_boat, faster_boat)
        margin = -margin
    else:
        pair = (faster_boat, slower_boat)
        margin = margin
    new_value = date, margin
    if pair not in head_to_head:
        head_to_head[pair] = new_value
    else:
        # Maximize date and abs(margin)
        head_to_head[pair] = max(
            head_to_head[pair],
            new_value,
            key=lambda x: (x[0], abs(x[1])),
        )


class CONFLICT_LEVEL:
    _1 = 1
    _2 = 2


Conflict = namedtuple("Conflict", "school1 school2 level margin date")


def get_conflicts(problem) -> List[Conflict]:
    """
    Conflict: (school1, school2, level, margin, date, indirect_margins)
    means that school2 should be ranked above school1, because they beat school1 by margin on date
    indirect_margins collects the links of length two between the two schools
    """
    conflicts = []
    for i, school1 in enumerate(problem.ranking):
        for school2 in problem.ranking[i + 1 :]:
            if tuple(sorted((school1, school2))) in problem.head_to_head:
                margin, date = get_margin_and_date(
                    problem.head_to_head, school1, school2
                )
                if margin < 0:
                    conflicts.append(
                        Conflict(school1, school2, CONFLICT_LEVEL._1, margin, date)
                    )
            if (
                problem.meets_minimum_races[school2]
                and not problem.meets_minimum_races[school1]
            ):
                conflicts.append(
                    Conflict(school1, school2, CONFLICT_LEVEL._1, 0, "3000-01-01")
                )
            if tuple(sorted((school1, school2))) in problem.path2:
                margin, date = get_margin_and_date(problem.path2, school1, school2)
                if margin < 0:
                    conflicts.append(
                        Conflict(school1, school2, CONFLICT_LEVEL._2, margin, date)
                    )

    return conflicts


def move_up(problem, conflict):
    new_ranking = list(problem.ranking)

    index_1 = problem.ranking.index(conflict.school1)
    index_2 = problem.ranking.index(conflict.school2)

    new_ranking = (
        problem.ranking[:index_1]
        + [conflict.school2]
        + [conflict.school1]
        + problem.ranking[index_1 + 1 : index_2]
        + problem.ranking[index_2 + 1 :]
    )

    return Problem(
        new_ranking, problem.head_to_head, problem.meets_minimum_races, problem.path2
    )


def move_down(problem, conflict):
    new_ranking = list(problem.ranking)

    index_1 = problem.ranking.index(conflict.school1)
    index_2 = problem.ranking.index(conflict.school2)

    new_ranking = (
        problem.ranking[:index_1]
        + problem.ranking[index_1 + 1 : index_2]
        + [conflict.school2]
        + [conflict.school1]
        + problem.ranking[index_2 + 1 :]
    )

    return Problem(
        new_ranking, problem.head_to_head, problem.meets_minimum_races, problem.path2
    )


def iterative_repair(subject, get_conflicts, objective_function, repair_strategies):
    """
    subject: opaque
    get_conflicts : subject -> List[conflict]
    repair_strategies: List[(subject, conflict) -> subject]
    objective_function: subject -> float
    """
    # We are MAXIMIZING the objective function. It can be -margin

    initial_objective = objective_function(subject)
    conflicts = get_conflicts(subject)

    current_objective = initial_objective
    current_subject = subject

    previous_objective = None

    # Iterate to a fixed-point
    while current_objective != previous_objective:
        best_objective = current_objective
        best_candidate = current_subject
        best_repair = None

        for conflict in conflicts:
            for repair in repair_strategies:
                candidate = repair(best_candidate, conflict)

                # if conflict in get_conflicts(candidate):
                #     raise Exception("Didn't fix conflict " + str(conflict) + " " + str(candidate) + " " + subject)

                candidate_objective = objective_function(candidate)
                if candidate_objective > best_objective:
                    best_candidate = candidate
                    best_objective = candidate_objective
                    best_repair = (repair, conflict)

        current_objective = best_objective
        current_subject = best_candidate

        if best_repair == None:
            break

    return current_subject


# FORMULA = "=SUM(AK2:AK36,AJ2:AJ35,AI2:AI34,AH2:AH33,AG2:AG32,AF2:AF31,AE2:AE30,AD2:AD29,AC2:AC28,AB2:AB27,AA2:AA26,Z2:Z25,Y2:Y24,X2:X23,W2:W22,V2:V21,U2:U20,T2:T19,S2:S18,R2:R17,Q2:Q16,P2:P15,O2:O14,N2:N13,M2:M12,L2:L11,K2:K10,J2:J9,I2:I8,H2:H7,G2:G6,F2:F5,E2:E4,D2:D3,C2)"
# FORMULA = "=SUM($AK$2:$AK$36,$AJ$2:$AJ$35,$AI$2:$AI$34,$AH$2:$AH$33,$AG$2:$AG$32,$AF$2:$AF$31,$AE$2:$AE$30,$AD$2:$AD$29,$AC$2:$AC$28,$AB$2:$AB$27,$AA$2:$AA$26,$Z$2:$Z$25,$Y$2:$Y$24,$X$2:$X$23,$W$2:$W$22,$V$2:$V$21,$U$2:$U$20,$T$2:$T$19,$S$2:$S$18,$R$2:$R$17,$Q$2:$Q$16,$P$2:$P$15,$O$2:$O$14,$N$2:$N$13,$M$2:$M$12,$L$2:$L$11,$K$2:$K$10,$J$2:$J$9,$I$2:$I$8,$H$2:$H$7,$G$2:$G$6,$F$2:$F$5,$E$2:$E$4,$D$2:$D$3,$C$2)"
FORMULA = "=SUMPRODUCT(B2:AK37, ROW(B2:AK37) < COLUMN(B2:AK37))"

# best_ranking = [
#                     "BB&N",
#                     "BU Academy",
#                     "Brooks",
#                     "Frederick Gunn",
#                     "Valley Regional",
#                     "Lincoln",
#                     "Hopkins",
#                     "Greenwich Country Day",
#                     "Cambridge RLS",
#                     "Brewster Academy",
#                     "Berkshire Academy",
#                     "Lyme/Old Lyme",
#                     "Middlesex",
#                     "Taft",
#                     "St. Mary's-Lynn",
#                     "Canterbury",
#                     "Middletown",
#                     "NMH",
#                     "Choate",
#                     "Derryfield",
#                     "Greenwich Academy",
#                     "St. Mark's",
#                     "Nobles",
#                     "Winsor",
#                     "Pomfret",
#                     "Pingree",
#                     "St. Mary Academy-Bay View",
#                     "Newton Country Day",
#                     "Suffield",
#                     "Marianapolis Prep",
#                     "Berwick",
#                     "Worcester Academy",
#                     "Groton",
#                     "Miss Porter's",
#                 ]


# -4
# ['Nobles', 'BB&N', 'Brooks', 'Cambridge RLS', 'Middlesex', 'Choate', 'Taft', 'Hopkins', 'Frederick Gunn', "St. Mark's", 'Brewster Academy', 'Winsor', 'Newton Country Day', 'Canterbury', 'Greenwich Academy', 'Lyme/Old Lyme', 'NMH', 'Groton', 'Berkshire Academy', 'Pomfret', 'Valley Regional', "St. Mary's-Lynn", 'Lincoln', 'St. Mary Academy-Bay View', "Miss Porter's", 'Marianapolis Prep', 'Middletown', 'Suffield', 'BU Academy', 'Pingree', 'Greenwich Country Day', 'Berwick', 'Derryfield', 'Worcester Academy']
# -36.970000000000006
# ['Nobles', 'Groton', 'BB&N', 'Brooks', 'Cambridge RLS', 'Choate', 'Taft', 'Hopkins', 'Frederick Gunn', 'Middlesex', "St. Mark's", 'Brewster Academy', 'Canterbury', 'Greenwich Academy', 'Lyme/Old Lyme', "Miss Porter's", 'Middletown', 'Valley Regional', "St. Mary's-Lynn", 'NMH', 'Berkshire Academy', 'Pomfret', 'Marianapolis Prep', 'Suffield', 'Winsor', 'Greenwich Country Day', 'BU Academy', 'Pingree', 'Berwick', 'Derryfield', 'Worcester Academy', 'Newton Country Day', 'Lincoln', 'St. Mary Academy-Bay View']

# (-4, -42.07000000000001)
# ['Choate', 'Taft', 'Hopkins', 'Nobles', 'BB&N', 'Brooks', 'Cambridge RLS', 'Winsor', 'Frederick Gunn', 'Middlesex', 'Brewster Academy', 'Canterbury', 'Greenwich Academy', 'Lyme/Old Lyme', 'NMH', "St. Mark's", 'Berwick', 'Groton', 'Berkshire Academy', 'Pomfret', 'Newton Country Day', 'BU Academy', 'Valley Regional', "St. Mary's-Lynn", 'Marianapolis Prep', 'Derryfield', 'Worcester Academy', 'Middletown', 'Lincoln', 'St. Mary Academy-Bay View', 'Pingree', 'Suffield', "Miss Porter's", 'Greenwich Country Day']

# (-4, -36.970000000000006)
# ['Nobles', 'Brooks', 'Groton', 'BB&N', 'Cambridge RLS', 'Middlesex', 'Choate', 'Taft', 'Hopkins', 'Frederick Gunn', "St. Mark's", 'BU Academy', 'Pingree', 'Brewster Academy', 'Canterbury', 'Greenwich Academy', 'Lyme/Old Lyme', 'NMH', 'Berkshire Academy', "Miss Porter's", 'Greenwich Country Day', 'Valley Regional', "St. Mary's-Lynn", 'Pomfret', 'Marianapolis Prep', 'Winsor', 'Newton Country Day', 'Lincoln', 'Berwick', 'Middletown', 'Suffield', 'Derryfield', 'Worcester Academy', 'St. Mary Academy-Bay View']

# (-4, -36.970000000000006)
# ['Choate', 'Taft', 'Hopkins', 'Frederick Gunn', 'Nobles', 'Groton', 'BB&N', 'Brooks', 'Cambridge RLS', 'Middlesex', 'Winsor', "St. Mark's", 'Brewster Academy', 'Canterbury', 'Newton Country Day', 'Greenwich Academy', 'Lyme/Old Lyme', 'Middletown', 'Berwick', 'Valley Regional', 'NMH', 'Berkshire Academy', 'Greenwich Country Day', "St. Mary's-Lynn", 'Lincoln', 'St. Mary Academy-Bay View', 'Pomfret', 'Marianapolis Prep', 'Derryfield', 'Suffield', 'Worcester Academy', 'BU Academy', 'Pingree', "Miss Porter's"]

# (-4, '2024-04-27', -40.57)
# ['Nobles', 'Choate', 'Taft', 'Hopkins', 'Frederick Gunn', 'Brewster Academy', 'Canterbury', 'Brooks', 'Groton', 'BB&N', 'Cambridge RLS', 'Middlesex', 'Greenwich Academy', 'Lyme/Old Lyme', 'Greenwich Country Day', 'Middletown', 'Valley Regional', "St. Mary's-Lynn", 'Berwick', 'NMH', 'Berkshire Academy', "St. Mark's", 'BU Academy', 'Pingree', 'Pomfret', 'Marianapolis Prep', "Miss Porter's", 'Derryfield', 'Worcester Academy', 'Winsor', 'Newton Country Day', 'Lincoln', 'St. Mary Academy-Bay View', 'Suffield']
# [('Choate', 'Berkshire Academy', -14.41, '2024-05-05'), ('Taft', 'Berkshire Academy', -17.46, '2024-05-05'), ('Brewster Academy', "St. Mark's", -4.7, '2024-04-27'), ('Groton', 'Cambridge RLS', -4.0, '2024-05-04')]

# (-4, -1714892400.0, -36.970000000000006)
# ['Nobles', 'Groton', 'BB&N', 'Brooks', 'Cambridge RLS', 'Middlesex', 'Choate', 'Taft', 'Hopkins', 'Frederick Gunn', "St. Mark's", 'Brewster Academy', 'Canterbury', 'Greenwich Academy', 'Lyme/Old Lyme', 'Valley Regional', "St. Mary's-Lynn", 'Middletown', 'NMH', 'Berwick', 'Berkshire Academy', 'Pomfret', 'Marianapolis Prep', 'Derryfield', 'Worcester Academy', 'Suffield', 'BU Academy', 'Winsor', 'Newton Country Day', 'Lincoln', 'St. Mary Academy-Bay View', "Miss Porter's", 'Pingree', 'Greenwich Country Day']
# [('Groton', 'Cambridge RLS', -4.0, '2024-05-04'), ('Choate', 'Berkshire Academy', -14.41, '2024-05-05'), ('Taft', 'Berkshire Academy', -17.46, '2024-05-05'), ("St. Mark's", 'NMH', -1.1, '2024-04-13')]

# (-2, -1712991600.0, -10.9)
# ['Nobles', 'Brooks', 'Cambridge RLS', 'Groton', 'BB&N', 'BU Academy', 'Middlesex', 'Taft', 'Choate', 'Hopkins', 'Frederick Gunn', "St. Mark's", 'Pingree', 'Brewster Academy', 'Lyme/Old Lyme', 'Greenwich Academy', 'Canterbury', 'NMH', 'Berkshire Academy', 'Pomfret', 'Valley Regional', "St. Mary's-Lynn", 'Winsor', 'Newton Country Day', 'Middletown', 'Marianapolis Prep', 'Suffield', 'Greenwich Country Day', 'Derryfield', 'Berwick', "Miss Porter's", 'St. Mary Academy-Bay View', 'Lincoln', 'Worcester Academy']
# [('Cambridge RLS', 'BB&N', -9.8, '2024-04-13'), ("St. Mark's", 'NMH', -1.1, '2024-04-13')]

# (-2, -1713596400.0, -6.6)
# ['Nobles', 'Brooks', 'BB&N', 'Cambridge RLS', 'Taft', 'Choate', 'Hopkins', 'Frederick Gunn', 'Middlesex', "St. Mark's", 'Brewster Academy', 'Lyme/Old Lyme', 'Greenwich Academy', 'Canterbury', 'Groton', 'NMH', 'Berkshire Academy', 'Pomfret', 'Valley Regional', "St. Mary's-Lynn", 'Marianapolis Prep', 'Winsor', 'Newton Country Day', 'BU Academy', 'Pingree', 'Derryfield', 'Middletown', 'Berwick', 'Worcester Academy', "Miss Porter's", 'Greenwich Country Day', 'Suffield', 'St. Mary Academy-Bay View', 'Lincoln']
# [('BB&N', 'Groton', -5.5, '2024-04-20'), ("St. Mark's", 'NMH', -1.1, '2024-04-13')]

Critique = namedtuple("Critique", "school1 school2 critique_type ")


def critique(data_dir, class_, gender, varsity_index, ranking):
    """
    For every pair of schools, gather evidence that either SUPPORTS or CONTRADICTS their relative ordering
    """
    boatName = gender + varsity_index + class_
    print(boatName)

    tuples: List[data.Datum] = data.get_head_to_head_tuples(data_dir)

    filtered_tuples = [x for x in tuples if x.boatName == boatName]

    critiques = []

    for i, school1 in enumerate(ranking):
        for school2 in ranking[i + 1 :]:
            # did school1 beat school2 head-to-head? That supports it
            # did school2 beat school1 head-to-head? That contradicts it
            pass
