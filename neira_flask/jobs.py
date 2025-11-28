import logging

from neira.scraper import clean
from neira_flask import db

import neira.scraper.download
import neira.scraper.scrape
from neira_flask.apply_corrections import apply_corrections_single

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

    scrape_id = db.get_scrape_id()

    db.write_regatta(args["uid"], scraped, "1_parsed", scrape_id)  # Will skip if checksum matches

    # Parse/Scrape step
    cleaned = clean.clean(scraped)
    db.write_regatta(args["uid"], cleaned, "2_cleaned", scrape_id)  # Will skip if checksum matches


def create_download_regatta_jobs():
    for regatta_name, uid, url in neira.scraper.download.get_race_urls(2025):
        args = "download_regatta", {"url": url, "name": regatta_name, "uid": uid}
        logger.info("inserting", args)
        db.insert_job(*args)


def apply_corrections(args):
    uid = args["uid"]
    correction_id = args["correction_id"]

    scrape_id = db.get_scrape_id()

    corrections = db.get_corrections_by_id(correction_id)[0]

    parent_regatta_id, regatta = db.get_regatta(uid, status="2_cleaned")
    if regatta is None:
        logger.error("Could not apply corrections to " + uid)
        return
    apply_corrections_single(regatta, corrections["corrections"])
    for heat in regatta["heats"]:
        if heat["gender"] not in ("boys", "girls"):
            raise Exception("Unrecognized gender: " + str(heat["gender"]))
        if heat["class"] not in ("eights", "fours"):
            raise Exception("Unrecognized boat class: " + str(heat["class"]))
    db.write_regatta(uid, regatta, status="3_reviewed", scrape_id=scrape_id, parent_id=parent_regatta_id, producer="apply_corrections", correction_id=corrections["correction_id"])


if __name__ == "__main__":
    create_download_regatta_jobs()

