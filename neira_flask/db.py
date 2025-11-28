from contextlib import contextmanager
import json
import logging
import os
from psycopg_pool import ConnectionPool
from psycopg.types.json import Jsonb

import sys
import atexit
import signal

from neira_flask.checksum import compute_checksum, get_checksum_version

logger = logging.getLogger(__name__)
_pool = None

def exit_handler():
    if _pool is not None:
        _pool.close()
    logger.info("Cleaning up")

def kill_handler(*args):
    sys.exit(0)

atexit.register(exit_handler)
signal.signal(signal.SIGINT, kill_handler)
signal.signal(signal.SIGTERM, kill_handler)

def get_pool():
    global _pool
    if _pool is None:
        _pool = ConnectionPool(os.environ['DATABASE_URL'], min_size=2, max_size=2)
    return _pool


@contextmanager
def get_cursor(cursor):
    if cursor is not None:
        yield cursor
    else:
        with get_pool().connection() as conn, conn.cursor() as cursor:
            yield cursor


def main():
    datadir = "/Users/dailis/neiraseeding/neira/data/1_parsed"
    status = "1_parsed"

    scrape_id = get_scrape_id()

    logger.info(f"{scrape_id=}")
    for json_file in os.listdir(datadir):
        uid = os.path.splitext(os.path.basename(json_file))[0]
        with open(os.path.join(datadir, json_file)) as f:
            regatta = json.load(f)
        write_regatta(uid, regatta, status=status, scrape_id=scrape_id)


def write_regatta(uid, regatta, status, scrape_id, parent_id=None, producer=None, correction_id=None, cursor=None):
    if parent_id is None or producer is None or correction_id is None:
        if not (parent_id is None and producer is None and correction_id is None):
            raise Exception("parent_id, producer, and correction_id must either all be omitted or all provided")

    checksum_version, regatta_checksum = compute_checksum(regatta)

    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            select regatta.id
            from neira.regattas regatta
            join neira.regatta_statuses rstatus
            on regatta.id = rstatus.regatta_id
            join neira.regatta_checksums checksum on regatta.id = checksum.regatta_id
            where rstatus.status = %(status)s
            and checksum.checksum = %(regatta_checksum)s
            and checksum.checksum_version = %(checksum_version)s
            """,
            dict(
                status=status,
                regatta_checksum=regatta_checksum,
                checksum_version=checksum_version,
            )
        )

        skip_insert = False
        regatta_id = None
        for regatta_id, in cursor:
            logger.info(f"Skipping inserting regatta with uid={uid}, status={status}, checksum={regatta_checksum}")
            skip_insert = True
            regatta_id = regatta_id

        if not skip_insert:
            cursor.execute(
                """
                insert into neira.regattas
                (uid, year, date, name, comment, distance, url)
                values
                (%(uid)s, %(year)s, %(date)s, %(name)s, %(comment)s, %(distance)s, %(url)s)
                returning id;
                """,
                dict(
                    uid=uid, 
                    year=int(regatta["date"].split("-")[0]),
                    date=regatta["date"],
                    name=regatta["name"],
                    comment=regatta["comment"].strip(),
                    distance=None,
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
                        copy.write_row((heat_id, result["finish_order"], result["raw_time"], result["margin_from_winner"], school_ids[result["school"]]))
                        logger.info("Inserted result %s", json.dumps(result))

            cursor.execute(
                """
                insert into neira.regatta_checksums
                (regatta_id, checksum, checksum_version)
                values
                (%(regatta_id)s, %(regatta_checksum)s, %(checksum_version)s);
                """,
                dict(
                    regatta_id=regatta_id,
                    regatta_checksum=regatta_checksum,
                    checksum_version=checksum_version,
                )
            )

            if parent_id is not None:
                cursor.execute(
                """
                insert into neira.regatta_parents
                (parent_id, child_id, producer, correction_id)
                values
                (%(parent_id)s, %(child_id)s, %(producer)s, %(correction_id)s);
                """,
                dict(
                    parent_id=parent_id,
                    child_id=regatta_id,
                    producer=producer,
                    correction_id=correction_id,
                )
            )

        # Unconditionally insert a status 
        cursor.execute(
            """
            insert into neira.regatta_statuses
            (regatta_id, status, scrape_id)
            values
            (%(regatta_id)s, %(status)s, %(scrape_id)s)
            """,
            dict(
                regatta_id=regatta_id,
                status=status,
                scrape_id=scrape_id
            )
        )

        read_regatta = get_regattas_by_id([regatta_id], cursor=cursor)
        logger.info("read_regatta_keys: %s", list(read_regatta))
        read_regatta = read_regatta[regatta_id]
        current_checksum_version, checksum = compute_checksum(read_regatta)
        if checksum != regatta_checksum:
            logger.error("Checksum mismatch on write. Writing correct checksum now.")
            cursor.execute(
                """
                update neira.regatta_checksums
                set checksum=%(checksum)s, checksum_version=%(checksum_version)s
                where regatta_id=%(regatta_id)s
                """,
                dict(
                    regatta_id=regatta_id,
                    checksum=checksum,
                    checksum_version=current_checksum_version,
                )
            )

    logger.info("Finished %s", uid)
    return regatta_id


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


def get_heats(year, class_, gender, varsity_index, cursor=None):
    status = "2_cleaned"
    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            with relevant_regattas as (
                select distinct on (uid) id
                from neira.regattas regatta
                join neira.regatta_statuses rstatus
                on regatta.id = rstatus.regatta_id
                where regatta.year = %(year)s
                and rstatus.status = %(status)s
                order by uid, rstatus.scrape_id desc
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
                school.name,
                regatta.url
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
        logger.info("finished query")
        heats = {}
        for heat_id, regatta_uid, regatta_name, regatta_date, distance, finish_order, raw_time, margin_from_winner, school, url in cursor:
            if not heat_id in heats:
                heats[heat_id] = {
                    "regatta_name": regatta_name,
                    "regatta_uid": regatta_uid,
                    "date": regatta_date,
                    "distance": distance,
                    "results": [],
                    "url": url
                }
            heats[heat_id]["results"].append({
                "finish_order": finish_order,
                "school": school,
                "raw_time": raw_time,
                "margin_from_winner": float(margin_from_winner) if margin_from_winner is not None else None
            })
            heats[heat_id]["results"].sort(key=lambda x: x["finish_order"])
        return sorted(heats.values(), key=lambda heat: heat["date"])


def get_corrections(cursor=None):
    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            select distinct on (regatta_uid) regatta_uid, id, details, checksum
            from neira.corrections
            order by regatta_uid, id desc
            """
        )
        corrections = {}
        for regatta_uid, correction_id, details, checksum in cursor:
            corrections[regatta_uid] = {
                "correction_id": correction_id,
                "checksum": checksum,
                "corrections": details
            }
    return corrections

def get_corrections_by_id(cursor=None):
    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            select regatta_uid, id, details, checksum
            from neira.corrections
            where id = %(correction_id)s
            """,
            dict(
                correction_id=correction_id
            )
        )
        corrections = {}
        for regatta_uid, correction_id, details, checksum in cursor:
            corrections[regatta_uid] = {
                "correction_id": correction_id,
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


def get_regattas_review_status(year, cursor=None):
    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            select regatta.id as regatta_id, rstatus.scrape_id, uid, year,  date, name, rstatus.status, comment, distance, correction.id as correction_id, rp.parent_id
            from neira.regattas regatta
            join neira.regatta_statuses rstatus
            on regatta.id = rstatus.regatta_id
            left join neira.regatta_parents rp on regatta.id = rp.child_id
            left join neira.regatta_checksums checksum on regatta.id = checksum.regatta_id
            left join neira.corrections correction on regatta.uid = correction.regatta_uid and checksum.checksum = correction.checksum
            where year=%(year)s
            order by rstatus.scrape_id
            """,
            dict(
                year=year
            )
        )
        regattas = {}
        for regatta_id, scrape_id, regatta_uid, year, date, name, status, comment, distance, correction_id, parent_id in cursor:
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
                "correction_id": correction_id,
                "parent_id": parent_id,
            })

        for uid, subregattas in list(regattas.items()):
            regattas_by_id = {}
            for regatta in subregattas:
                regattas_by_id[regatta["regatta_id"]] = regatta
            for regatta in subregattas:
                if regatta["status"] == "3_reviewed" and regatta["parent_id"] not in regattas_by_id:
                    del regattas_by_id[regatta["regatta_id"]]
            regattas[uid] = list(regattas_by_id.values())
    
    return sorted(regattas.values(), key=lambda x: x[0]["date"])


def get_regatta_for_review(regatta_uid, cursor=None):
    logger.info(regatta_uid)
    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            with relevant_regattas as (
                select distinct on (rstatus.status) id
                from neira.regattas regatta
                join neira.regatta_statuses rstatus
                on regatta.id = rstatus.regatta_id
                where regatta.uid = %(regatta_uid)s
                order by rstatus.status, rstatus.scrape_id desc
            )
            select
                regatta.id as regatta_id,
                rstatus.status as status,
                regatta.name,
                regatta.date,
                regatta.distance,
                regatta.comment,
                regatta.url,
                regatta_parent.parent_id
            from neira.regattas regatta
            join neira.regatta_statuses rstatus
            on regatta.id = rstatus.regatta_id
            left join neira.regatta_parents regatta_parent on regatta.id = regatta_parent.child_id
            where regatta.id in (select id from relevant_regattas)
            """,
            dict(
                regatta_uid=regatta_uid
            )
        )
        regattas = {}
        for regatta_id, status, name, date, distance, comment, url, parent_id in cursor:
            regattas[regatta_id] = {
                    "status": status,
                    "comment": comment,
                    "day": date,
                    "date": date,
                    "heats": {},
                    "name": name,
                    "url": url,
                    "parent_id": parent_id,
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
        for regatta_id, regatta in regattas.items():
            res[regatta["status"]] = regatta
            regatta["heats"] = list(regatta["heats"].values())
            regatta["id"] = regatta_id
        return res
    


def get_regatta(regatta_uid, status, cursor=None):
    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            select id
            from neira.regattas regatta
            join neira.regatta_statuses rstatus
            on regatta.id = rstatus.regatta_id
            where rstatus.status = %(status)s
            and regatta.uid = %(regatta_uid)s
            order by rstatus.scrape_id desc
            limit 1
            """,
            dict(
                regatta_uid=regatta_uid,
                status=status,
            )
        )
        regatta_ids = [x for (x,) in cursor]

        if len(regatta_ids) != 1:
            raise Exception("Expected exactly one regatta but found " + str(regatta_ids))
        
        return regatta_ids[0], list(get_regattas_by_id(regatta_ids).values())[0]


def get_regattas_by_id(regatta_ids, cursor=None):
    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            select
                regatta.id as regatta_id,
                rstatus.status as status,
                regatta.name,
                regatta.date,
                regatta.distance,
                regatta.comment,
                regatta.url
            from neira.regattas regatta
            join neira.regatta_statuses rstatus
            on regatta.id = rstatus.regatta_id
            where regatta.id = any(%(regatta_ids)s);
            """,
            dict(
                regatta_ids=regatta_ids
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
            dict(
                regatta_ids=regatta_ids
            )
        )
        for regatta_id, heat_id, class_, gender, varsity_index, finish_order, raw_time, margin_from_winner, school in cursor:
            heats = regattas[regatta_id]["heats"]
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
        
        for regatta in regattas.values():
            regatta["heats"] = list(regatta["heats"].values())
        return regattas

        
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
                logger.info("Inserted", correction)


def update_correction(uid, details, checksum, cursor=None):
    with get_cursor(cursor) as cursor:
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
            checksum=checksum,
        ))


def lookup_checksum(regatta_id, cursor=None):
    with get_cursor(cursor) as cursor:
        cursor.execute(
            """
            select checksum
            from neira.regatta_checksums
            where regatta_id = '%(regatta_id)s'
            """,
            dict(regatta_id=regatta_id)
        )
        return cursor.fetchone()[0]


def insert_job(job_type, args, cursor=None):
    with get_cursor(cursor) as cursor:
        cursor.execute(
        """
        insert into neira.jobs
        (status, job_type, arguments)
        values
        ('pending', %(job_type)s, %(arguments)s);
        """,
        dict(
            job_type=job_type,
            arguments=Jsonb(args)
        ))


def get_scrape_id(cursor=None):
    with get_cursor(cursor) as cursor:
        cursor.execute("select trunc(extract(epoch from now() )* 1000);")
        return int(cursor.fetchone()[0])


if __name__ == '__main__':
    # logger.info(get_regatta("0B5A12BEAF8945DD81EB9EFB206E62F1", status="2_cleaned"))
    insert_corrections()
    # main()

    