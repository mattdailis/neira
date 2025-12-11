import logging

from neira.scraper import clean
from neira_flask import db

import neira.scraper.download
import neira.scraper.scrape
from neira_flask.apply_corrections import apply_corrections_single

logger = logging.getLogger(__name__)

def download_regatta(args):
    year = 2025

    url = args["url"]
    logger.info(f"download_regatta({url})")

    # Download step

    downloaded = neira.scraper.download.download_one((args["name"], args["uid"], args["url"]))

    if downloaded["url"].endswith("cat=1"):
        scraped = neira.scraper.scrape.scrape_cat_1(downloaded["name"], downloaded["html"], downloaded["url"], year)
    elif downloaded["url"].endswith("cat=5"):
        scraped = neira.scraper.scrape.scrape_cat_5(downloaded["name"], downloaded["html"], downloaded["url"], year)
    else:
        raise Exception("Unhandled cat: " + downloaded["url"])

    scrape_id = db.get_scrape_id()

    db.write_regatta(args["uid"], scraped, "1_parsed", scrape_id)  # Will skip if checksum matches

    # Parse/Scrape step
    cleaned = clean.clean(scraped)

    db.write_regatta(args["uid"], cleaned, "2_cleaned", scrape_id)  # Will skip if checksum matches


def apply_corrections(args):
    with db.get_cursor() as cursor:
        uid = args["uid"]
        correction_id = args["correction_id"]

        scrape_id = db.get_scrape_id(cursor=cursor)

        corrections = db.get_corrections_by_id(correction_id, cursor=cursor)[uid]

        parent_regatta_id, regatta = db.get_regatta_by_checksum(uid, checksum=corrections["checksum"], cursor=cursor)
        if regatta is None:
            logger.error("Could not apply corrections to " + uid)
            return
        apply_corrections_single(regatta, corrections["corrections"])
        for heat in regatta["heats"]:
            if heat["gender"] not in ("boys", "girls"):
                raise Exception("Unrecognized gender: " + str(heat["gender"]))
            if heat["class"] not in ("eights", "fours"):
                raise Exception("Unrecognized boat class: " + str(heat["class"]))
        db.write_regatta(uid, regatta, status="3_reviewed", scrape_id=scrape_id, parent_id=parent_regatta_id, producer="apply_corrections", correction_id=corrections["correction_id"], cursor=cursor)


def create_download_regatta_jobs():
    for regatta_name, uid, url in neira.scraper.download.get_race_urls(2025):
        args = "download_regatta_local", {"url": url, "name": regatta_name, "uid": uid}
        logger.info("inserting", args)
        db.insert_job(*args)


def create_apply_corrections_jobs():
    uid = "3E2795D2BE91D9DEA1F8805FF62566D7"
    correction_id = 819

    args = "apply_corrections", {"uid": uid, "correction_id": correction_id}
    db.insert_job(*args)


# alter table neira.jobs add constraint job_type_check check (job_type in ('download_regatta', 'apply_corrections'));
if __name__ == "__main__":
    create_download_regatta_jobs()
    # create_apply_corrections_jobs()

