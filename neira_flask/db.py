import os
import psycopg

def main():
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select name from neira.schools;")
            for record in cursor:
                print(record)