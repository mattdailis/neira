# audit.py is intended for queries that check certain properties of data, or identify data that can safely be deleted

from neira_flask import db
from neira_flask.checksum import compute_checksum, get_checksum_version



def delete_unneeded_regattas():
    """
    Find regattas that are not the most recent in their status
    """

    pool = db.get_pool()
    with pool.connection() as conn, conn.cursor() as cursor:
        cursor.execute(
        """
        with relevant_regattas as (
            select distinct on (uid, status) id
            from neira.regattas regatta
            order by uid, status, scrape_id desc
        )
        delete from neira.regattas where id not in (select id from relevant_regattas);
        """)


def recompute_checksums():
    current_checksum_version = get_checksum_version()
    pool = db.get_pool()
    with pool.connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            select regatta.id, checksum.checksum
            from neira.regattas regatta
            left join neira.regatta_checksums checksum on regatta.id = checksum.regatta_id and checksum.checksum_version=%(current_checksum_version)s
            where checksum is null;
            """,
            dict(
                current_checksum_version=current_checksum_version,
            )
        )
        checksums = list(cursor)
        for i, (regatta_id, checksum) in enumerate(checksums):
            regatta = db.get_regattas_by_id([regatta_id])[regatta_id]
            current_checksum_version, checksum = compute_checksum(regatta)
            cursor.execute(
                """
                insert into neira.regatta_checksums
                (regatta_id, checksum, checksum_version)
                values
                (%(regatta_id)s, %(checksum)s, %(checksum_version)s);
                """,
                dict(
                    regatta_id=regatta_id,
                    checksum=checksum,
                    checksum_version=current_checksum_version,
                )
            )
            conn.commit()

            print("Updated checksum for", regatta_id, "checksum="+checksum, f"({i}/{len(checksums)})")
if __name__ == "__main__":
    recompute_checksums()
