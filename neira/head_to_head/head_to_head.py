from collections import namedtuple
import csv
import datetime
from itertools import permutations
import json
from math import factorial
from multiprocessing import Pool
import os
from pprint import pprint
from random import shuffle
from typing import List
import neira.data_provider.data_provider as data
from tabulate import tabulate
from tqdm import tqdm

from neira.dot.toDot import nodeName
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

    boatnames = []

    for class_ in ("fours",):
        for gender in ("girls",):
            for varsity_index in ("1", "2", "3", "4"):
                boatName = gender + varsity_index + class_
                boatnames.append(boatName)

    # with Pool(5) as p:
    #     p.map(Ranker(data_dir).rank, boatnames)

    Ranker(data_dir).rank(boatnames[3])


class Ranker:
    def __init__(self, data_dir) -> None:
        self.data_dir = data_dir

    def rank(self, boatName):
        return rank_helper(self.data_dir, boatName)


def rank_helper(data_dir, boatName):
    tuples: List[data.Datum] = data.get_head_to_head_tuples(data_dir)
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
        if x.adjusted_margin is None:
            margin = x.margin
        else:
            margin = x.adjusted_margin
        put_margin(head_to_head, x.faster_boat, x.slower_boat, margin, x.date)

    path2 = dict()
    for (school1, school2), (date1, margin1, _) in head_to_head.items():
        for (school3, school4), (date2, margin2, _) in head_to_head.items():
            if school2 == school3 and school1 != school4:
                put_margin(
                    path2,
                    school1,
                    school4,
                    margin1 + margin2,
                    min(date1, date2),
                )
            if school1 == school3 and school2 != school4:
                put_margin(
                    path2,
                    school2,
                    school4,
                    margin2 - margin1,
                    min(date1, date2),
                )
            if school1 == school4 and school2 != school3:
                put_margin(
                    path2,
                    school3,
                    school2,
                    margin1 + margin2,
                    min(date1, date2),
                )
            if school2 == school4 and school1 != school3:
                put_margin(
                    path2,
                    school1,
                    school3,
                    margin1 - margin2,
                    min(date1, date2),
                )

    for school1, school2 in head_to_head:
        if (school1, school2) in path2:
            del path2[(school1, school2)]

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

    best_ranking = [
        "Nobles",
        "Brooks",
        "BB&N",
        "Winsor",
        "Groton",
        "NMH",
        "Choate",
        "Middlesex",
        "St. Mark's",
        "Taft",
        "Pomfret",
        "Cambridge RLS",
        "Newton Country Day",
        "Hopkins",
    ]

    # sorted(list(schools))
    alternatives = []
    best_objective = objective_function(
        Problem(best_ranking, head_to_head, meets_minimum_races, path2)
    )

    for _ in tqdm(range(1)):
        # schools_copy = list(schools)
        # shuffle(schools_copy)
        problem = Problem(
            # schools_copy,
            best_ranking,
            head_to_head,
            meets_minimum_races,
            path2,
        )

        result = iterative_repair(
            problem, get_conflicts, objective_function, (move_up, move_down)
        )

        new_objective = objective_function(result)
        if new_objective == best_objective and result.ranking != best_ranking:
            alternatives.append(result.ranking)
        if new_objective > best_objective:
            best_objective = new_objective
            best_ranking = result.ranking
            alternatives = []
            print(best_objective)
            print(best_ranking)

    print("Finished")

    print("There were " + str(len(alternatives)) + " equally viable alternatives")

    print()
    print("Best objective: \n")
    print(best_objective)
    table = list(zip(best_ranking, *alternatives))
    table.insert(18, ("---------",) * (1 + len(alternatives)))

    print(tabulate(table))

    conflicts = get_conflicts(
        Problem(best_ranking, head_to_head, meets_minimum_races, path2)
    )

    conflicts.sort(key=lambda x: (-x.level, x.date, x.margin), reverse=True)
    for x in conflicts:
        print(x)

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
            for school, _ in sorted(potential_energy.items(), key=lambda x: -x[1]):
                school_index = current_ranking.index(school)
                if school_index == 0:
                    continue
                new_ranking = list(current_ranking)
                new_ranking[school_index] = new_ranking[school_index - 1]
                new_ranking[school_index - 1] = school

                new_potential_energy = get_potential_energy(new_ranking, beat)

                if sum(new_potential_energy.values()) >= total_potential_energy:
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
                                    if best_ranking.index(x) > current_ranking.index(x)
                                    else ""
                                )
                                + str(best_ranking.index(x) - current_ranking.index(x))
                                + ")"
                            )
                            if best_ranking.index(x) != current_ranking.index(x)
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
            if (school2, school1) in head_to_head and head_to_head[(school2, school1)][
                1
            ] > 0:
                row.append(head_to_head[(school2, school1)][1])
            elif (school1, school2) in head_to_head and head_to_head[
                (school1, school2)
            ][1] < 0:
                row.append(-head_to_head[(school1, school2)][1])
            else:
                row.append("")
        rows.append(row)
    with open(f"head-to-head-{boatName}.csv", "w") as f:
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


def get_margin_and_date(head_to_head, school1, school2, extra=None):
    """
    margin > 0 means that school1 beat school2
    """
    if extra == None:
        extra = []
    if (school1, school2) in head_to_head:
        extra.extend(head_to_head[(school1, school2)][2])
        return head_to_head[(school1, school2)][1], head_to_head[(school1, school2)][0]
    if (school2, school1) in head_to_head:
        extra.extend(reversed(head_to_head[(school2, school1)][2]))
        return -head_to_head[(school2, school1)][1], head_to_head[(school2, school1)][0]


def put_margin(head_to_head, faster_boat, slower_boat, margin, date, metadata=None):
    """
    school1 beat school2 by margin
    """
    if metadata is None:
        metadata = []
    if faster_boat > slower_boat:
        pair = (slower_boat, faster_boat)
        margin = -margin
        metadata = list(reversed(metadata))
    else:
        pair = (faster_boat, slower_boat)
        margin = margin
    new_value = date, margin, metadata
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

    repairs = []

    print("Initial:", subject.ranking)

    # Iterate to a fixed-point
    while current_objective != previous_objective:
        best_objective = current_objective
        best_candidate = current_subject
        best_repair = None

        for conflict in conflicts:
            for repair in repair_strategies:
                candidate = repair(current_subject, conflict)

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

        repairs.append(best_repair)

    for x in repairs:
        print("Repair:", x)
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

# Critique = namedtuple("Critique", "school1 school2 critique_type ")


class Evidence:
    def __init__(self, data_dir, class_, gender, varsity_index):
        tuples: List[data.Datum] = data.get_head_to_head_tuples(data_dir)
        boatName = gender + varsity_index + class_
        filtered_tuples = [x for x in tuples if x.boatName == boatName]

        self.filtered_tuples = filtered_tuples

        schools = set()
        for x in filtered_tuples:
            schools.add(x.faster_boat)
            schools.add(x.slower_boat)

        self.schools = schools

        head_to_head = dict()
        # margin = right school time minus left school time

        for x in filtered_tuples:
            if x.adjusted_margin is not None:
                margin = x.adjusted_margin
            else:
                margin = x.margin
            put_margin(head_to_head, x.faster_boat, x.slower_boat, margin, x.date)

        path2 = expand_one_step(head_to_head, head_to_head)

        for school1, school2 in head_to_head:
            if (school1, school2) in path2:
                del path2[(school1, school2)]

        path3 = expand_one_step(path2, head_to_head)
        for school1, school2 in head_to_head:
            if (school1, school2) in path3:
                del path3[(school1, school2)]
        for school1, school2 in path2:
            if (school1, school2) in path3:
                del path3[(school1, school2)]

        transitive_head_to_head = dict()
        for school in schools:
            transitive_head_to_head[school] = []

        def put_transitive(school1, school2, path=None):
            if school2 in [x[0] for x in transitive_head_to_head[school1]]:
                return
            transitive_head_to_head[school1].append((school2, path))
            for school, losers in list(transitive_head_to_head.items()):
                if school1 in losers:
                    continue
                put_transitive(school, school2, path=[school] + path)

        for (school1, school2), (date, margin, _) in head_to_head.items():
            if margin < 0:
                school3 = school1
                school1 = school2
                school2 = school3
            put_transitive(school1, school2, path=[school1, school2])

        self.head_to_head = head_to_head
        self.path2 = path2
        self.path3 = path3
        self.transitive_head_to_head = transitive_head_to_head

    def compare_head_to_head(self, school1, school2, extra=None):
        """
        Get margin and date of head-to-head.
        Return None if these two schools never raced
        """
        return get_margin_and_date(self.head_to_head, school1, school2, extra=extra)

    def compare_common_opponent(self, school1, school2, extra=None):
        """
        Compare two schools relative to some common opponent, if one exists
        """
        return get_margin_and_date(self.path2, school1, school2, extra=extra)

    def compare_chain_3(self, school1, school2, extra=None):
        """
        Compare two schools along chains of length 3
        Return None if these two schools never raced
        """
        return get_margin_and_date(self.path3, school1, school2, extra=extra)

    def beats_transitively(self, school1, school2):
        """
        Compare two schools along chains of length 3
        Return None if these two schools never raced
        """
        return school2 in self.transitive_head_to_head[school1]

    def compare(self, school1, school2):
        """
        Return a list of comparisons between the schools. Types of comparisons include:
        - Head to head results and dates (all)
        - Paths of length 2 and dates and margins (all)
        - Paths of length 3 and dates and margins (all)
        """

        comparisons = []
        for path in paths_of_length(1, self.filtered_tuples, school1, school2):
            x = path[0]
            margin = x.adjusted_margin if x.adjusted_margin is not None else x.margin
            comparisons.append(
                ("HEAD_TO_HEAD", margin, x.date, list(map(trim_tuple, path)))
            )
        for path in paths_of_length(2, self.filtered_tuples, school1, school2):
            margin = sum(
                x.adjusted_margin if x.adjusted_margin is not None else x.margin
                for x in path
            )
            date = min(x.date for x in path)
            comparisons.append(
                ("PATH_2", round(margin, 2), date, list(map(trim_tuple, path)))
            )
        for path in paths_of_length(3, self.filtered_tuples, school1, school2):
            margin = sum(
                x.adjusted_margin if x.adjusted_margin is not None else x.margin
                for x in path
            )
            date = min(x.date for x in path)
            comparisons.append(
                ("PATH_3", round(margin, 2), date, list(map(trim_tuple, path)))
            )
        return comparisons


def trim_tuple(x):
    return (
        x.faster_boat,
        x.slower_boat,
        round(x.adjusted_margin if x.adjusted_margin is not None else x.margin, 2),
        x.date,
    )


def lookup_tuples(tuples, school):
    for x in tuples:
        if x.faster_boat == school:
            yield x
        if x.slower_boat == school:
            yield data.Datum(
                x.date,
                x.gender,
                x.boatName,
                # Swapped slower and faster
                x.slower_boat,
                x.slower_varsity_index,
                x.faster_boat,
                x.faster_varsity_index,
                # Negated margins
                -x.margin,
                -x.adjusted_margin if x.adjusted_margin is not None else None,
                x.regatta_display_name,
                x.comment,
                x.url,
            )


def paths_of_length(length, tuples, school1, school2):
    frontier = [(school1, [])]
    for i in range(length):
        new_frontier = []
        for school, path in frontier:
            visited = set()
            for x in path:
                visited.add(x.faster_boat)
                visited.add(x.slower_boat)
            for x in lookup_tuples(tuples, school):
                other_school = (
                    x.slower_boat
                )  # NOTE! Mis-nomer. It may not actually be slower, if the margin is negative
                if other_school in visited:
                    continue
                new_frontier.append((other_school, path + [x]))
        frontier = new_frontier
    paths = []
    for school, path in frontier:
        if school == school2:
            if length == 1 or len({x.date for x in path}) > 1:
                paths.append(path)
    return paths


def critique(data_dir, class_, gender, varsity_index, ranking):
    """
    For every pair of schools, gather evidence that either SUPPORTS or CONTRADICTS their relative ordering
    """
    boatName = gender + varsity_index + class_
    print(boatName)

    evidence = Evidence(data_dir, class_, gender, varsity_index)

    for x in ranking:
        if x.strip() not in evidence.schools:
            print(evidence.schools)
            raise Exception(x + "not in schools")

    critiques = []

    for i, school1 in enumerate(ranking):
        for j in range(i + 1, len(ranking)):
            school2 = ranking[j]
            # did school1 beat school2 head-to-head? That supports it
            # did school2 beat school1 head-to-head? That contradicts it
            margin_and_date = evidence.compare_head_to_head(school1, school2)
            if margin_and_date is not None:
                margin, date = margin_and_date
                if margin > 0:
                    critiques.append(
                        (
                            "SUPPORTED",
                            f"{school1} is ranked above {school2} because they won head to head by {margin} seconds on {date}",
                        )
                    )
                else:
                    critiques.append(
                        (
                            "CONTRADICTED",
                            f"{school1} is ranked above {school2}, but they lost head to head by {-margin} seconds on {date}",
                        )
                    )
            else:
                extra = []
                margin_and_date = evidence.compare_common_opponent(
                    school1, school2, extra=extra
                )
                if margin_and_date is None:
                    extra = []
                    margin_and_date = evidence.compare_chain_3(
                        school1, school2, extra=extra
                    )
                    if margin_and_date is None:
                        if evidence.beats_transitively(school1, school2):
                            critiques.append(
                                (
                                    "SUPPORTED",
                                    f"{school1} is ranked above {school2} because {school1} transitively beats {school2}",
                                )
                            )
                        elif evidence.beats_transitively(school2, school2):
                            critiques.append(
                                (
                                    "CONTRADICTED",
                                    f"{school1} is ranked above {school2}, but {school2} transitively beats {school1}",
                                )
                            )
                        else:
                            critiques.append(
                                (
                                    "UNSUPPORTED",
                                    f"{school1} is ranked above {school2} even though we have no way to compare these two schools",
                                )
                            )
                    else:
                        margin, date = margin_and_date

                        margin_chain = ""
                        previous_school = school1
                        for next_school in extra + [school2]:
                            margin_chain += previous_school
                            m_d = get_margin_and_date(
                                evidence.head_to_head, previous_school, next_school
                            )
                            previous_school = next_school
                            if m_d is None:
                                import pdb

                                pdb.set_trace()
                            m, d = m_d
                            margin_chain += "("
                            if m > 0:
                                m = "+" + str(m)
                            else:
                                m = str(m)
                            margin_chain += m
                            margin_chain += ")"
                        margin_chain += school2

                        if margin > 0:
                            critiques.append(
                                (
                                    "SUPPORTED",
                                    f"{school1} is ranked above {school2} because of this chain of margins: {margin_chain} [{school1} net +{round(margin, 2)}]",
                                )
                            )
                        else:
                            critiques.append(
                                (
                                    "CONTRADICTED",
                                    f"{school1} is ranked above {school2} despite this chain of margins: {margin_chain} [{school2} net +{-round(margin, 2)}]",
                                )
                            )
                else:
                    margin, date = margin_and_date
                    if margin > 0:
                        critiques.append(
                            (
                                "SUPPORTED",
                                f"{school1} is ranked above {school2} because they each raced {extra[0]}, and {school1} had a more favorable outcome",
                            )
                        )
                    else:
                        critiques.append(
                            (
                                "CONTRADICTED",
                                f"{school1} is ranked above {school2}, but when they each raced {extra[0]}, {school2} had a more favorable outcome",
                            )
                        )

    with open(f"critiques-{class_}-{gender}-{varsity_index}.txt", "w") as f:
        print(f"critiques-{class_}-{gender}-{varsity_index}.txt")
        for type_, critique in sorted(critiques):
            f.write(type_ + " " + critique)
            f.write("\n")


def compare_all(data_dir, out_dir, class_, gender, varsity_index):
    evidence = Evidence(data_dir, class_, gender, varsity_index)
    for school1 in evidence.schools:
        for school2 in evidence.schools:
            if school1 < school2:
                lines = compare_inner(evidence, school1, school2)
                with open(
                    os.path.join(
                        out_dir,
                        f"compare-{class_}-{gender}-{varsity_index}-{nodeName(school1)}-{nodeName(school2)}.txt",
                    ),
                    "w",
                ) as f:
                    f.writelines(lines)


def compare(data_dir, class_, gender, varsity_index, school1, school2):
    evidence = Evidence(data_dir, class_, gender, varsity_index)
    for line in compare_inner(evidence, school1, school2):
        print(line)


def compare_inner(evidence, school1, school2):
    """
    For every pair of schools, gather evidence that either SUPPORTS or CONTRADICTS their relative ordering
    """

    lines = []

    def print(*s):
        lines.append(" ".join(s) + "\n")

    comparisons = sorted(
        evidence.compare(school1, school2),
        key=lambda y: (-["HEAD_TO_HEAD", "PATH_2", "PATH_3"].index(y[0]), y[2], -y[1]),
        reverse=True,
    )

    head_to_head = [x for x in comparisons if x[0] == "HEAD_TO_HEAD"]

    if len(head_to_head) == 0:
        print(f"{school1} and {school2} have never raced head to head")
    elif len(head_to_head) == 1:
        result = head_to_head[0]
        print(f"{school1} and {school2} have raced head to head once on {result[2]}")
        if result[1] > 0:
            print(f"{school1} won the race by {result[1]} seconds")
        elif result[1] < 0:
            print(f"{school2} won the race by {-result[1]} seconds")
        else:
            print("It was a dead tie")

    else:
        print(
            f"{school1} and {school2} have raced head to head {len(head_to_head)} time{'s' if len(head_to_head) > 1 else ''}"
        )
        school1_wins = 0
        school2_wins = 0
        for x in head_to_head:
            if x[1] > 0:
                school1_wins += 1
            else:
                school2_wins += 1

        if school2_wins == 0:
            print(f"{school1} has won every race")
        elif school1_wins == 0:
            print(f"{school2} has won every race")
        elif school1_wins >= school2_wins:
            print(f"{school1} has won {school1_wins}/{len(head_to_head)} races")
        else:
            print(f"{school2} has won {school2_wins}/{len(head_to_head)} races")

        print()
        print("From most recent to least recent:")
        for x in head_to_head:
            if x[1] > 0:
                print(f"{x[2]}: {school1} won by {x[1]} seconds")
            elif x[1] < 0:
                print(f"{x[2]}: {school2} won by {-x[1]} seconds")

    del head_to_head
    path_2 = [x for x in comparisons if x[0] == "PATH_2"]

    print()

    print_path_results(2, path_2, school1, school2, print=print)

    print()
    path_3 = [x for x in comparisons if x[0] == "PATH_3"]
    print_path_results(3, path_3, school1, school2, print=print)

    return lines


def print_path_results(length, results, school1, school2, print=print):
    if len(results) == 0:
        print(f"There are no paths of length {length} between {school1} and {school2}")
    elif len(results) == 1:
        result = results[0]
        print(
            f"There is exactly one path of length {length} between {school1} and {school2}, via {path_to_string(school1, result[3])}"
        )
        print(
            f"It favors {school1 if result[1] > 0 else school2} by a cumulative margin of {abs(result[1])} seconds"
        )
    else:
        print(
            f"There are {len(results)} paths of length {length} between {school1} and {school2}"
        )

        school1_wins = 0
        school2_wins = 0
        for x in results:
            if x[1] > 0:
                school1_wins += 1
            else:
                school2_wins += 1

        if school2_wins == 0:
            print(f"All of them favor {school1}")
        elif school1_wins == 0:
            print(f"All of them favor {school2}")
        elif school1_wins >= school2_wins:
            print(f"{school1_wins}/{len(results)} of them favor {school1}")
        else:
            print(f"{school2_wins}/{len(results)} of them favor {school2}")
        print("From most recent to least recent:")
        for x in results:
            path = path_to_string(school1, x[3])
            print(path)


def path_to_string(school1, path):
    result = school1
    for x in path:
        y, m, d = x[3].split("-")
        result += f"--({x[2]} {int(m)}/{int(d)})-->{x[1]}"
        school2 = x[1]
    total_margin = round(sum(x[2] for x in path), 2)
    if total_margin > 0:
        return result + f" [{school1} net +{total_margin}]"
    else:
        return result + f" [{school2} net +{-total_margin}]"


def expand_one_step(previous, head_to_head):
    path2 = dict()
    for (school1, school2), (date1, margin1, old_metadata) in previous.items():
        for (school3, school4), (date2, margin2, _) in head_to_head.items():
            if school2 == school3 and school1 != school4:
                put_margin(
                    path2,
                    school1,
                    school4,
                    margin1 + margin2,
                    min(date1, date2),
                    old_metadata + [school2],
                )
            if school1 == school3 and school2 != school4:
                put_margin(
                    path2,
                    school2,
                    school4,
                    margin2 - margin1,
                    min(date1, date2),
                    list(reversed(old_metadata)) + [school1],
                )
            if school1 == school4 and school2 != school3:
                put_margin(
                    path2,
                    school3,
                    school2,
                    margin1 + margin2,
                    min(date1, date2),
                    [school1] + old_metadata,
                )
            if school2 == school4 and school1 != school3:
                put_margin(
                    path2,
                    school1,
                    school3,
                    margin1 - margin2,
                    min(date1, date2),
                    old_metadata + [school2],
                )
    return path2


# Nobles,Groton,Brooks,BB&N,Middlesex,Cambridge RLS,Taft,Choate,Hopkins,Frederick Gunn,Canterbury,Greenwich Academy,Lyme/Old Lyme,Middletown,Valley Regional,Miss Porter's,Winsor,St. Mark's,Brewster Academy,Newton Country Day,NMH,Berkshire Academy,Pomfret,St. Mary's-Lynn,Marianapolis Prep,St. Mary Academy-Bay View,Derryfield,Suffield,BU Academy,Berwick,Worcester Academy,Greenwich Country Day,Lincoln,Pingree


# "Taft,Nobles,Groton,Brooks,Choate,Hopkins,Frederick Gunn,Brewster Academy,BB&N,Middlesex,Cambridge RLS,Canterbury,Miss Porter's,Winsor,Greenwich Academy,Lyme/Old Lyme,NMH,St. Mark's,Middletown,Berkshire Academy,Valley Regional,St. Mary's-Lynn,Pomfret,Marianapolis Prep,Greenwich Country Day,BU Academy,Derryfield,Dexter-Southfield,Newton Country Day,St. Mary Academy-Bay View,Lincoln,Berwick,Worcester Academy,Suffield,Pingree"


# Nobles,NMH,Brooks,BB&N,Winsor,Groton,Choate,St. Mark's,Middlesex,Taft,Cambridge RLS,Berkshire Academy,Pomfret,Greenwich Country Day,Hopkins,Lyme/Old Lyme,Canterbury,Newton Country Day
