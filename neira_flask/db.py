import json
import os
from psycopg_pool import ConnectionPool
from psycopg.types.json import Jsonb

import sys
import atexit
import signal

_pool = None

def exit_handler():
    if _pool is not None:
        _pool.close()
    print("Cleaning up")

def kill_handler(*args):
    sys.exit(0)

atexit.register(exit_handler)
signal.signal(signal.SIGINT, kill_handler)
signal.signal(signal.SIGTERM, kill_handler)

def get_pool():
    global _pool
    if _pool is None:
        _pool = ConnectionPool(os.environ['DATABASE_URL'])
    return _pool


def main():
    datadir = "/Users/dailis/neiraseeding/neira/data/1_cleaned"
    status = "1_cleaned"
    pool = get_pool()
    with pool.connection() as conn, conn.cursor() as cursor:
        cursor.execute("select trunc(extract(epoch from now() )* 1000);")
        scrape_id = int(cursor.fetchone()[0])

    print(f"{scrape_id=}")
    for json_file in os.listdir(datadir):
        uid = os.path.splitext(os.path.basename(json_file))[0]
        with open(os.path.join(datadir, json_file)) as f:
            regatta = json.load(f)
        write_regatta(uid, regatta, status=status, scrape_id=scrape_id)

def write_regatta(uid, regatta, status, scrape_id):    
    pool = get_pool()
    with pool.connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            insert into neira.regattas
            (scrape_id, uid, year, date, name, comment, distance, status, url)
            values
            (%(scrape_id)s, %(uid)s, %(year)s, %(date)s, %(name)s, %(comment)s, %(distance)s, %(status)s, %(url)s)
            returning id;
            """,
            dict(
                scrape_id=scrape_id,
                uid=uid, 
                year=2025,
                date=regatta["day"],
                name=regatta["regatta_display_name"],
                comment=regatta["comment"].strip(),
                distance=None,
                status=status,
                url=regatta["url"]
            ))
        regatta_id = int(cursor.fetchone()[0])
        
        schools = set()
        for heat in regatta["heats"]:
            for result in heat["results"]:
                schools.add(result["school"])
        schools = sorted(schools)

        school_ids = load_school_ids(cursor)

        for school in schools:
            if school not in school_ids:       
                cursor.execute(
                    """
                    insert into neira.schools
                    (name)
                    values
                    (%(name)s)
                    on conflict do nothing
                    """,
                    dict(name=school)
                )

        school_ids = load_school_ids(cursor)

        for heat in regatta["heats"]:
            cursor.execute(
            """
            insert into neira.heats
            (regatta_id, class, gender, varsity_index)
            values
            (%(regatta_id)s, %(class)s, %(gender)s, %(varsity_index)s)
            returning id;
            """,
            dict(
                regatta_id=regatta_id,
                gender=heat["gender"],
                varsity_index=heat["varsity_index"],
                **{
                    "class": heat["class"]
                }
            ))
            heat_id = int(cursor.fetchone()[0])

            with cursor.copy("""
                copy neira.results
                (heat_id, finish_order, raw_time, margin_from_winner, school_id)
                from stdin
                """) as copy:
                for i, result in enumerate(heat["results"]):
                    finish_order = i + 1
                    copy.write_row((heat_id, finish_order, result["raw_time"], result["margin_from_winner"], school_ids[result["school"]]))
                    print("Inserted result", json.dumps(result))
    print("Finished", uid)


def load_school_ids(cursor):
    cursor.execute(
        """
        select name, id from neira.schools;
        """
    )
    school_ids = {}
    for school_name, school_id in cursor:
        school_ids[str(school_name)] = int(school_id)
    return school_ids


def get_heats(year, class_, gender, varsity_index):
    status = "1_cleaned"
    pool = get_pool()
    with pool.connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            with relevant_regattas as (
                select distinct on (uid) id
                from neira.regattas regatta
                where regatta.year = %(year)s
                and regatta.status = %(status)s
                order by uid, scrape_id desc
            )

            select
                heat.id as heat_id,
                regatta.uid as uid,
                regatta.name,
                regatta.date,
                regatta.distance,
                result.finish_order,
                result.raw_time,
                result.margin_from_winner,
                school.name
            from neira.regattas regatta
            join neira.heats heat on regatta.id = heat.regatta_id
            join neira.results result on heat.id = result.heat_id
            join neira.schools school on result.school_id = school.id
            where heat.gender = %(gender)s
            and heat.class = %(class)s
            and heat.varsity_index = %(varsity_index)s
            and regatta.id in (select id from relevant_regattas);
            """,
            dict(
                year=year,
                gender=gender,
                varsity_index=int(varsity_index),
                status=status,
                **{
                    "class": class_
                }
            )
        )
        print("finished query")
        heats = {}
        for heat_id, regatta_uid, regatta_name, regatta_date, distance, finish_order, raw_time, margin_from_winner, school in cursor:
            if not heat_id in heats:
                heats[heat_id] = {
                    "regatta_name": regatta_name,
                    "regatta_uid": regatta_uid,
                    "date": regatta_date,
                    "distance": distance,
                    "results": []
                }
            heats[heat_id]["results"].append({
                "finish_order": finish_order,
                "school": school,
                "raw_time": raw_time,
                "margin_from_winner": float(margin_from_winner) if margin_from_winner is not None else None
            })
            heats[heat_id]["results"].sort(key=lambda x: x["finish_order"])
        return sorted(heats.values(), key=lambda heat: heat["date"])


def get_corrections():
    pool = get_pool()
    with pool.connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            select distinct on (regatta_uid) regatta_uid, details, checksum
            from neira.corrections
            order by regatta_uid, id desc
            """
        )
        corrections = {}
        for regatta_uid, details, checksum in cursor:
            corrections[regatta_uid] = {
                "checksum": checksum,
                "corrections": details
            }
    return corrections


def get_regatta_uids(year):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                
                select distinct uid from neira.regattas
                where year=%(year)s;
                """,
                dict(
                    year=year
                )
            )
            regattas = []
            for uid, in cursor:
                regattas.append(uid)
    return regattas


def get_regattas_review_status(year):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select id, scrape_id, uid, year,  date, name, status, comment, distance from neira.regattas
                where year=%(year)s
                order by scrape_id
                """,
                dict(
                    year=year
                )
            )
            regattas = {}
            for regatta_id, scrape_id, regatta_uid, year, date, name, status, comment, distance in cursor:
                if regatta_uid not in regattas:
                    regattas[regatta_uid] = []
                regattas[regatta_uid].append({
                    "regatta_id": regatta_id, 
                    "scrape_id": scrape_id,
                    "regatta_uid": regatta_uid,
                    "year": year,
                    "date": date,
                    "name": name,
                    "status": status,
                    "comment": comment,
                    "distance": distance,
                })
    
    return sorted(regattas.values(), key=lambda x: x[0]["date"])


def get_regatta_for_review(regatta_uid):
    print(regatta_uid)
    pool = get_pool()
    with pool.connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            with relevant_regattas as (
              select distinct on (status) id
              from neira.regattas regatta
              where uid = %(regatta_uid)s
              order by status, scrape_id desc
            )
            select
                regatta.id as regatta_id,
                regatta.status as status,
                regatta.name,
                regatta.date,
                regatta.distance,
                regatta.comment,
                regatta.url
            from neira.regattas regatta
            where regatta.id in (select id from relevant_regattas)
            """,
            dict(
                regatta_uid=regatta_uid
            )
        )
        regattas = {}
        for regatta_id, status, name, date, distance, comment, url in cursor:
            regattas[regatta_id] = {
                    "status": status,
                    "comment": comment,
                    "day": date,
                    "date": date,
                    "heats": {},
                    "regatta_display_name": name,
                    "name": name,
                    "url": url
                }
        cursor.execute(
            """
            select
                heat.regatta_id,
                heat.id as heat_id,
                heat.class,
                heat.gender,
                heat.varsity_index,
                result.finish_order,
                result.raw_time,
                result.margin_from_winner,
                school.name
            from neira.heats heat
            join neira.results result on heat.id = result.heat_id
            join neira.schools school on result.school_id = school.id
            and heat.regatta_id = any(%(regatta_ids)s);
            """,
            dict(regatta_ids=list(regattas)),
        )
        heats = {}
        for regatta_id, heat_id, class_, gender, varsity_index, finish_order, raw_time, margin_from_winner, school in cursor:
            if heat_id not in heats:
                heats[heat_id] = {
                    "class": class_,
                    "gender": gender,
                    "varsity_index": str(varsity_index),
                    "results": []
                }
            heats[heat_id]["results"].append({
                "margin_from_winner": None if margin_from_winner is None else (float(margin_from_winner) if margin_from_winner != 0 else 0),
                "raw_time": raw_time,
                "school": school,
                "finish_order": finish_order
            })
            heats[heat_id]["results"].sort(key=lambda x: x["finish_order"])
            regattas[regatta_id]["heats"][heat_id] = heats[heat_id]
        res = {}
        for regatta in regattas.values():
            res[regatta["status"]] = regatta
            regatta["heats"] = list(regatta["heats"].values())
            for heat in regatta["heats"]:
                for result in heat["results"]:
                    del result["finish_order"]
        return res
    


def get_regatta(regatta_uid, status):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                with relevant_regattas as (
                  select distinct on (uid) id
                  from neira.regattas regatta
                  where regatta.status = %(status)s
                  order by uid, scrape_id desc
                )

                select
                  heat.id as heat_id,
                  heat.class,
                  heat.gender,
                  heat.varsity_index,
                  regatta.name,
                  regatta.date,
                  regatta.distance,
                  regatta.comment,
                  result.finish_order,
                  result.raw_time,
                  result.margin_from_winner,
                  school.name,
                  regatta.url
                from neira.regattas regatta
                join neira.heats heat on regatta.id = heat.regatta_id
                join neira.results result on heat.id = result.heat_id
                join neira.schools school on result.school_id = school.id
                and regatta.uid = %(regatta_uid)s
                and regatta.id in (select id from relevant_regattas);


                """,
                dict(
                    status=status,
                    regatta_uid=regatta_uid
                )
            )
            regatta = None
            heats = {}
            for heat_id, class_, gender, varsity_index, regatta_name, date, distance, comment, finish_order, raw_time, margin_from_winner, school, url in cursor:
                if regatta is None:
                    regatta = {
                        "comment": comment,
                        "day": date,
                        "date": date,
                        "heats": [],
                        "regatta_display_name": regatta_name,
                        "name": regatta_name,
                        "url": url
                    }
                if heat_id not in heats:
                    heats[heat_id] = {
                        "class": class_,
                        "gender": gender,
                        "varsity_index": str(varsity_index),
                        "results": []
                    }
                heats[heat_id]["results"].append({
                    "margin_from_winner": None if margin_from_winner is None else (float(margin_from_winner) if margin_from_winner != 0 else 0),
                    "raw_time": raw_time,
                    "school": school,
                    "finish_order": finish_order
                })
                heats[heat_id]["results"].sort(key=lambda x: x["finish_order"])
            if regatta is None:
                return None
            regatta["heats"] = list(heats.values())
            for heat in regatta["heats"]:
                for result in heat["results"]:
                    del result["finish_order"]
            return regatta
        
def insert_corrections():
    with open("corrections.json", "r") as f:
        corrections = json.load(f)

    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            for uid, correction in corrections.items():
                cursor.execute(
                """
                insert into neira.corrections
                (regatta_uid, details, checksum)
                values
                (%(uid)s, %(details)s, %(checksum)s);
                """,
                dict(
                    uid=uid,
                    details=Jsonb(correction["corrections"]),
                    checksum=correction["checksum"]
                ))


def update_correction(uid, details, checksum):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
            """
            insert into neira.corrections
            (regatta_uid, details, checksum)
            values
            (%(uid)s, %(details)s, %(checksum)s);
            """,
            dict(
                uid=uid,
                details=Jsonb(details),
                checksum=checksum
            ))

if __name__ == '__main__':
    # print(get_regatta("0B5A12BEAF8945DD81EB9EFB206E62F1", status="1_cleaned"))
    # insert_corrections()
    main()

    