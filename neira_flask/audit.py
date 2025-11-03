# audit.py is intended for queries that check certain properties of data, or identify data that can safely be deleted

from neira_flask import db



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
