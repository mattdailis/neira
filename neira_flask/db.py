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
# from rich.traceback import install
# install(show_locals=True)

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
def get_cursor(cursor=None):
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
                (uid, year, date, name, comment, distance, url, location)
                values
                (%(uid)s, %(year)s, %(date)s, %(name)s, %(comment)s, %(distance)s, %(url)s, %(location)s)
                returning id;
                """,
                dict(
                    uid=uid, 
                    year=int(regatta["date"].split("-")[0]),
                    date=regatta["date"],
                    name=regatta["name"],
                    comment=regatta["comment"].strip(),
                    distance=None,
                    url=regatta["url"],
                    location=regatta["location"],
                ))
            regatta_id = int(cursor.fetchone()[0])
            
            schools = set()
            for heat in regatta["heats"]:
                for result in heat["results"]:
                    schools.add(result["school"])
            schools = sorted(schools)

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
                    (heat_id, finish_order, raw_time, margin_from_winner, school_name)
                    from stdin
                    """) as copy:
                    for i, result in enumerate(heat["results"]):
                        copy.write_row((heat_id, result["finish_order"] if "finish_order" in result else (i + 1), result["raw_time"], result["margin_from_winner"], result["school"]))
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
                result.school_name,
                regatta.url
            from neira.regattas regatta
            join neira.heats heat on regatta.id = heat.regatta_id
            join neira.results result on heat.id = result.heat_id
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

def get_corrections_by_id(correction_id, cursor=None):
    logger.info(correction_id)
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
        logger.info(corrections)
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
                regatta_parent.parent_id,
                checksum.checksum
            from neira.regattas regatta
            join neira.regatta_statuses rstatus
            on regatta.id = rstatus.regatta_id
            join neira.regatta_checksums checksum
            on regatta.id = checksum.regatta_id
            left join neira.regatta_parents regatta_parent on regatta.id = regatta_parent.child_id
            where regatta.id in (select id from relevant_regattas)
            """,
            dict(
                regatta_uid=regatta_uid
            )
        )
        regattas = {}
        for regatta_id, status, name, date, distance, comment, url, parent_id, checksum in cursor:
            regattas[regatta_id] = {
                    "status": status,
                    "comment": comment,
                    "day": date,
                    "date": date,
                    "heats": {},
                    "name": name,
                    "url": url,
                    "parent_id": parent_id,
                    "checksum": checksum
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
                result.school_name
            from neira.heats heat
            join neira.results result on heat.id = result.heat_id
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
    

def get_regatta_by_checksum(regatta_uid, checksum, cursor=None):
    logger.info("get_regatta_by_checksum(%s, %s)", regatta_uid, checksum)
    with get_cursor(cursor=cursor) as cursor:
        cursor.execute(
            """
            select id
            from neira.regattas regatta
            join neira.regatta_checksums checksum
            on regatta.id = checksum.regatta_id
            where checksum.checksum = %(checksum)s
            and regatta.uid = %(regatta_uid)s
            order by regatta.id desc
            limit 1
            """,
            dict(
                regatta_uid=regatta_uid,
                checksum=checksum,
            )
        )
        regatta_ids = [x for (x,) in cursor]

        if len(regatta_ids) != 1:
            raise Exception("Expected exactly one regatta but found " + str(regatta_ids))
        
        return regatta_ids[0], list(get_regattas_by_id(regatta_ids).values())[0]



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
                regatta.url,
                regatta.location
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
        for regatta_id, status, name, date, distance, comment, url, location in cursor:
            regattas[regatta_id] = {
                    "status": status,
                    "comment": comment,
                    "day": date,
                    "date": date,
                    "heats": {},
                    "name": name,
                    "url": url,
                    "location": location
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
                result.school_name
            from neira.heats heat
            join neira.results result on heat.id = result.heat_id
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

        
def insert_corrections(cursor=None):
    with get_cursor(cursor=cursor) as cursor:
        with open("corrections.json", "r") as f:
            corrections = json.load(f)
            for uid, correction in corrections.items():
                insert_correction_single(uid, correction["checksum"], correction["corrections"])
                logger.info("Inserted", correction)


def insert_correction_single(uid, checksum, details, cursor=None):
    with get_cursor(cursor=cursor) as cursor:
        cursor.execute(
        """
        insert into neira.corrections
        (regatta_uid, details, checksum)
        values
        (%(uid)s, %(details)s, %(checksum)s)
        returning id;
        """,
        dict(
            uid=uid,
            details=Jsonb(details),
            checksum=checksum
        ))
        for correction_id, in cursor:
            return correction_id


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

def set_coords(cursor=None):
    defs = """
 Boston, MA                                          | 42.35397256001751, -71.09392979236829
 Cambridge, MA                                       | 42.35397256001751, -71.09392979236829
 Charles River, Auburndale, MA                       | 42.34660075551339, -71.25995897166757
 Charles River Powerhouse                            | 42.36443115308227, -71.11654347288069
 Charles River - Power House                         | 42.36443115308227, -71.11654347288069
 Charles River Powerhouse Stretch - Cambridge, MA    | 42.36443115308227, -71.11654347288069
 Charles River-Powerhouse                            | 42.36443115308227, -71.11654347288069
 Concord River, Billerica, MA                        | 42.534219714998784, -71.30078700494671
 Concord River                                       | 42.534219714998784, -71.30078700494671
 Connecticut River (25 Jones Ferry Road Holyoke, MA) | 42.1721548388209, -72.63092108799832
 Connecticut River, Gill MA                          | 42.64613269047004, -72.4758913623132
 Cos Cob Harbor, Greenwich, CT                       | 41.02844293088989, -73.59523659193667
 Farmington, CT                                      | 41.742383808137106, -72.8633175680925
 Farmington River, Farmington CT                     | 41.742383808137106, -72.8633175680925
 Hanover, NH                                         | 43.738601938783134, -72.25169536687028
 Hooksett, NH                                        | 43.08100387932582, -71.4665797840369
 Housatonic River                                    | ???
 Kent CT                                             | 41.7110681825339, -73.48776651415368
 Lake Chebacco, Essex, MA                            | 42.609294277238746, -70.81040129476798
 Lake Cochichewick                                   | 42.70404698589618, -71.09626683844864
 Lake Pocotopaug, East Hampton, CT                   | 41.59596954476194, -72.50109433863295
 Lake Quinsigamond                                   | 42.276094343474966, -71.75610320977776
 Lake Quinsigamond, Shrewsbury MA                    | 42.276094343474966, -71.75610320977776
 Lake Quinsigamond, Shrewsbury, MA                   | 42.276094343474966, -71.75610320977776
 Lake Quinsigamond, Worcester, MA                    | 42.276094343474966, -71.75610320977776
 Lake Quonnipaug                                     | 41.397762788542586, -72.69712762538448
 Lake Quonnipaug, Guilford, Ct                       | 41.397762788542586, -72.69712762538448
 Lake Waramaug, Connecticut                          | 41.686188896425556, -73.35179277465254
 Lake Waramaug, CT                                   | 41.686188896425556, -73.35179277465254
 Lake Washinee, Salisbury, CT                        | 42.02577600947489, -73.40421112926074
 Lake Wickaboag, West Brookfield, MA                 | 42.239976826738996, -72.15415594785118
 Lake Wononpakook, CT                                | 41.93859658521218, -73.4553223799735
 Methuen, MA                                         | 42.696981854738056, -71.22194826155892
 Mianus River                                        | 41.03923360258101, -73.58987700926227
 Mianus River, Greenwich, CT                         | 41.03923360258101, -73.58987700926227
 Middletown, CT                                      | 41.55735567921841, -72.57869229552692
 Mystic, CT                                          | 41.36503363878109, -71.96702593961498
 Nashua River, Groton, MA                            | 42.628563639349935, -71.60756831553016
 Power House Course, Boston                          | 42.36443115308227, -71.11654347288069
 Quasset Lake, Woodstock, CT                         | 41.92377189487075, -71.98318677406132
 Rogers lake                                         | 41.36449627452393, -72.30413588098156
 Salmon Falls River, ME                              | 43.28470343333258, -70.89324606029045
 The Powerhouse, Charles River                       | 42.36443115308227, -71.11654347288069
 Thorndike Pond                                      | 42.862256377543595, -72.05494883363608
 Turkey Pond, Concord NH                             | 43.17487210978318, -71.58402618140506
 Turkey Pond, Concord, NH                            | 43.17487210978318, -71.58402618140506
 Watuppa Pond, Fall River, MA                        | 41.69007166771546, -71.11524947094684
 Glastonbury, CT                                     | 41.71055502346872, -72.61794408641155
 Pattagansett Lake, East Lyme CT                     | 41.37382002075274, -72.23023123097646
 Shelton, CT                                         | 41.270031250772995, -73.08848655606869
 Shelton, CT (Housatonic River)                      | 41.270031250772995, -73.08848655606869
    """

    with get_cursor(cursor=cursor) as cursor:
        for line in defs.strip().splitlines():
            location, coordinates = line.split("|")
            location = location.strip()
            coordinates = coordinates.strip()
            coordinates = coordinates.replace(',', '')
            if "???" in coordinates:
                continue
            query = f"""
            update neira.locations set coords=ST_GeomFromText('POINT({coordinates})', 3857) where name=%(location)s;
            """
            print(query, flush=True)
            cursor.execute(query,
            dict(
                location=location
            ))

def set_school_locations(cursor=None):
    defs = """
  1 | Andover               | 42.649166645077244, -71.131942420082 | https://andovercrew.com/#SpringSchedule25
  2 | Bancroft              | 42.30479876302297, -71.81404489874943 | https://www.bancroftschool.org/athletics/teams-programs/varsity-crew
  3 | Bedford               | 42.93736565963292, -71.51930104110538 | https://www.bedfordcrew.org/
  4 | Suffield              | 41.9853512623523, -72.65095729616736 | https://www.suffieldacademy.org/athletics/teams/crew
  5 | Farmington            | 41.74987533847976, -72.86589126423837 | https://sites.google.com/a/fpsct.org/farmingtoncrew/
  6 | BB&N                  | 42.371018422362056, -71.1347819569751 | https://www.bbns.org/athletics/teams/crew-boys-varsity/,https://www.bbns.org/athletics/teams/crew-girls-varsity/
  7 | Nobles                | 42.262683094311505, -71.18181631225478 | https://nobilis.nobles.edu/Athletics/team_detail.php?team_id=51487,https://nobilis.nobles.edu/Athletics/team_detail.php?team_id=51488
  8 | Cambridge RLS         | 42.374590373496204, -71.11154453418106 | https://crlsrowing.org/
  9 | Exeter                | 42.981135820480674, -70.95176551894771 | http://www.exetercrew.com/wp/,https://weareexeter.com/sports/mens-crew,https://weareexeter.com/sports/womens-crew
 10 | Thayer                | 42.21172023627747, -70.98504981576848 | https://www.thayer.org/athletics/teams-schedules-results/team-details/~athletics-team-id/85
 11 | St. Mark's            | 42.30912958998844, -71.52964933715647 | https://www.stmarksschool.org/athletics/teams/team-details/~athletics-team-id/124
 12 | Greenwich Academy     | 41.041763066195536, -73.6275052992362 | https://www.greenwichacademy.org/athletics/teams-and-schedules/detail/~athletics-team-id/145
 13 | Middletown            | 41.57740560765142, -72.67910789437065 | https://mhscrew.wixsite.com/rowing
 14 | Middlesex             | 42.49809913939459, -71.36694813614666 | https://athletics.mxschool.edu/sports/mens-crew,https://athletics.mxschool.edu/sports/womens-crew
 15 | Sacred Heart          | 41.066336533359234, -73.69432446149902 | https://www.shgreenwich.org/athletics/our-teams/rowing/rowing-spring
 16 | Brooks                | 42.71825814387373, -71.07602335085038 | https://www.brooksschool.org/athletics/teams-and-schedules/athletic-details/~athletics-team-id/127,https://www.brooksschool.org/athletics/teams-and-schedules/athletic-details/~athletics-team-id/129
 17 | Tabor                 | 41.707994006249024, -70.76638598135509 | https://www.taboracademy.org/athletics/teams/team-details/~athletics-team-id/451,https://www.taboracademy.org/athletics/teams/team-details/~athletics-team-id/452
 18 | St. John's Prep       | 42.582693496935605, -70.95266566673605 | https://www.stjohnsprep.org/athletics/teams-and-schedules/team-profile/~athletics-team-id/186
 19 | Glastonbury           | 41.70329182593176, -72.59330716705634
 20 | Brookline             | 42.33351980662681, -71.12849842891532
 21 | Greenwich Country Day | 41.07243706192967, -73.60242704549414
 22 | Brewster Academy      | 43.58351703389131, -71.20745683444784
 23 | BC High               | 42.31629900842828, -71.04543231088985
 24 | St. Mary's-Lynn       | 42.46273327072896, -70.95107563745171
 25 | Simsbury              | 41.87091058133808, -72.82158639530752 | https://www.simsburycrew.org/
 26 | Derryfield            | 43.03521672063977, -71.45876373940982
 27 | Kent                  | 41.724706743932735, -73.48538497337518
 28 | Hopkins               | 41.31888653199366, -72.97179982332575
 29 | Choate                | 41.45824990327572, -72.81105320102319
 30 | Pingree               | 42.63870675994496, -70.88091380988602
 31 | Winsor                | 42.34121543932388, -71.10716943544193
 32 | Pomfret               | 41.88588067082968, -71.96510917108326
 33 | Berkshire Academy     | 42.117112108555446, -73.41626606311702
 34 | Brunswick             | 41.03854804914525, -73.62608838190707
 35 | East Lyme             | 41.36945079509881, -72.21270101818163
 36 | Hanover               | 43.740408822468154, -72.24363558383608 | https://www.friendsofhanovercrew.org/
 37 | St. John's            | 42.292267205182796, -71.72914455369558 | https://www.stjohnshigh.org/athletics/teams/crew
 38 | Fairfield Prep        | 41.160421738843965, -73.254474629838
 39 | Notre Dame            | 41.224367631386194, -73.24663070095812
 40 | Dexter-Southfield     | 42.308235788006094, -71.13762266413642
 41 | Guilford              | 41.312924553647974, -72.71053941948553
 42 | Hotchkiss             | 41.94385937876665, -73.43977537567805
 43 | Taft                  | 41.603580677066226, -73.12380800016918
 44 | Lyme/Old Lyme         | 41.31878187858171, -72.32475193367665
 45 | Duxbury               | 42.04712770190913, -70.67846433276358
 46 | NMH                   | 42.670499941768554, -72.48384948529896
 47 | Eagle Hill            | 42.36426323809319, -72.20090156779503
 48 | St. Paul's            | 43.19479458322583, -71.57423591061186
 49 | Worcester Academy     | 42.253104069546595, -71.79255395890557
 50 | Boston Latin          | 42.338044784761586, -71.10107668634988
 51 | Shrewsbury            | 42.30356365446944, -71.74422895869041 | https://shrewsburycrew.org/
 52 | Berwick               | 43.243500377736005, -70.80058235230409
 53 | Deerfield             | 42.54863920998165, -72.60689219457522
 54 | Canterbury            | 41.58662416058128, -73.41196746340371
 55 | Miss Porter's         | 41.722497503405606, -72.82932190671829
 56 | Newton Country Day    | 42.34565954031322, -71.19134179448142
 57 | Stonington            | 41.36670809484514, -71.86064700007726
 58 | Groton                | 42.593573455970045, -71.58400713228848
 59 | Frederick Gunn        | 41.628069391659004, -73.31150175943694
 60 | Hingham               | 42.227493175590624, -70.87799015180899
 61 | Salisbury             | 42.00156623827821, -73.39013088651699
 62 | Marianapolis Prep     | 41.956240014159285, -71.86840827710347
 63 | Belmont Hill          | 42.40719025388106, -71.18165581907573
"""

    with get_cursor(cursor) as cursor:
        for line in defs.strip().splitlines():
            id, school_name, coordinates = line.split("|")[:3]
            school_name = school_name.strip()
            coordinates = coordinates.strip()
            coordinates = coordinates.replace(',', '')
            if "???" in coordinates:
                continue
            query = f"""
            update neira.schools set location=ST_GeomFromText('POINT({coordinates})', 3857) where name=%(school_name)s;
            """
            cursor.execute(query,
            dict(
                school_name=school_name
            ))
    
def get_coordinates(cursor=None):
    res = []
    with get_cursor(cursor=cursor) as cursor:
        cursor.execute("select name, ST_AsText(coords) from neira.locations order by name;")
        for name, coords in cursor:
            if not name:
                continue
            if not coords:
                continue
            coords = coords.split("(")[1].split(")")[0].split()
            coords = [float(x) for x in coords]
            print(coords)
            res.append((name, coords))
    return res


if __name__ == '__main__':
    # logger.info(get_regatta("0B5A12BEAF8945DD81EB9EFB206E62F1", status="2_cleaned"))
    # insert_corrections()
    # set_coords()
    # main()
    # get_coordinates()
    set_school_locations()
    