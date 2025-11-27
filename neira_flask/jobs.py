import logging

from neira.scraper import clean
from neira_flask import db

import neira.scraper.download
import neira.scraper.scrape
from neira_flask.checksum import compute_checksum

logger = logging.getLogger(__name__)

def download_regatta(args):
    url = args["url"]
    logger.info(f"download_regatta({url})")

    # Download step

    downloaded = neira.scraper.download.download_one((args["name"], args["uid"], args["url"]))

    if downloaded["url"].endswith("cat=1"):
        scraped = neira.scraper.scrape.scrape_cat_1(downloaded["name"], downloaded["html"], downloaded["url"])
    elif downloaded["url"].endswith("cat=5"):
        scraped = neira.scraper.scrape.scrape_cat_5(downloaded["name"], downloaded["html"], downloaded["url"])
    else:
        raise Exception("Unhandled cat: " + downloaded["url"])

    # checksum_version, regatta_checksum = compute_checksum(scraped)
    # Compute checksum of parsed result
    with db.get_pool().connection() as conn, conn.cursor() as cursor:
        cursor.execute("select trunc(extract(epoch from now() )* 1000);")
        scrape_id = int(cursor.fetchone()[0])

    db.write_regatta(args["uid"], scraped, "1_parsed", scrape_id)  # Will skip if checksum matches

    # Parse/Scrape step
    cleaned = clean.clean(scraped)
    db.write_regatta(args["uid"], cleaned, "2_cleaned", scrape_id)  # Will skip if checksum matches


def create_download_regatta_jobs():
    for regatta_name, uid, url in neira.scraper.download.get_race_urls(2025):
        if not "7FE2290879E1C3151B93CD8FCA2A71D5" in url:
            continue
        args = "download_regatta", {"url": url, "name": regatta_name, "uid": uid}
        print("inserting", args)
        db.insert_job(*args)


if __name__ == "__main__":
    create_download_regatta_jobs()

