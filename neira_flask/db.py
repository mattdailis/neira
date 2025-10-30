import json
import os
from psycopg_pool import ConnectionPool

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = ConnectionPool(os.environ['DATABASE_URL'])
    return _pool


def main():
    datadir = "/Users/dailis/neiraseeding/neira/data/1_cleaned"
    status = "1_cleaned"
    with ConnectionPool(os.environ['DATABASE_URL']) as pool:
        with pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("select trunc(extract(epoch from now() )* 1000);")
                scrape_id = int(cursor.fetchone()[0])

        print(f"{scrape_id=}")
        for json_file in os.listdir(datadir):
            uid = os.path.splitext(os.path.basename(json_file))[0]
            with open(os.path.join(datadir, json_file)) as f, pool.connection() as conn, conn.cursor() as cursor:
                data = json.load(f)
                cursor.execute(
                    """
                    insert into neira.regattas
                    (scrape_id, uid, year, date, name, comment, distance, status)
                    values
                    (%(scrape_id)s, %(uid)s, %(year)s, %(date)s, %(name)s, %(comment)s, %(distance)s, %(status)s)
                    returning id;
                    """,
                    dict(
                       scrape_id=scrape_id,
                       uid=uid, 
                       year=2025,
                       date=data["day"],
                       name=data["regatta_display_name"],
                       comment=data["comment"].strip(),
                       distance=None,
                       status=status
                    ))
                regatta_id = int(cursor.fetchone()[0])
                
                schools = set()
                for heat in data["heats"]:
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

                for heat in data["heats"]:
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
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                with relevant_regattas as (
                  select distinct on (uid) id
                  from neira.regattas regatta
                  where regatta.year = %(year)s
                  and regatta.status = '1_cleaned'
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
                and regatta.id in (select id from relevant_regattas)
                limit 100;
                """,
                dict(
                    year=year,
                    gender=gender,
                    varsity_index=int(varsity_index),
                    **{
                        "class": class_
                    }
                )
            )
            heats = {}
            for heat_id, regatta_uid, regatta_name, regatta_date, distance, finish_order, raw_time, margin_from_winner, school in cursor:
                print(regatta_uid)
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

if __name__ == '__main__':
    main()