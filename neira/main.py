import pprint
import warnings

import neira.founders_day
import neira.head_to_head
import neira.head_to_head.head_to_head
import neira.scraper.apply_corrections
import neira.dot.read

warnings.filterwarnings("ignore")

import json
import os

import click

from neira.scraper.download import download_all
from neira.scraper.scrape import scrapeRegatta

from difflib import unified_diff

import neira.scraper.clean as clean

import neira.scraper.neiraschools as neiraschools

import neira.scraper.review

CONFIG = None


@click.group()
def cli():
    global CONFIG
    with open("neira.config.json", "r") as f:
        CONFIG = json.load(f)


@cli.command()
# @click.argument("out")
# @click.option("--raw-cache", type=str)
@click.option("--refresh/--use-cache")
def scrape(refresh=False):
    global CONFIG
    out_dir = CONFIG["cleaned_dir"]
    raw_cache = CONFIG.get("raw_dir", None)

    OVERWRITE = True

    if refresh and raw_cache:
        for downloaded in download_all(2024):
            print("Downloading " + downloaded["uid"])
            with open(
                os.path.join(raw_cache, downloaded["uid"] + "-raw.json"), "w"
            ) as f:
                json.dump(downloaded, f)

    if raw_cache:
        iterator = read_from_cache(raw_cache)
    else:
        iterator = download_all(2024)

    for downloaded in iterator:
        scraped_filename = os.path.join(
            out_dir, "{}-scraped.json".format(downloaded["uid"])
        )
        cleaned_filename = os.path.join(out_dir, "{}.json".format(downloaded["uid"]))
        if OVERWRITE or not os.path.isfile(cleaned_filename):
            # print(f"Scraping: {downloaded['name']}")
            scraped = scrapeRegatta(downloaded["name"], downloaded["html"])
            scraped["url"] = downloaded["url"]
            # with open(scraped_filename, "w") as f:
            #     f.write(json.dumps(scraped, sort_keys=True, indent=4))

            race_object = clean.clean(scraped)

            if not race_object["heats"]:
                print(
                    "No heats in "
                    + race_object["regatta_display_name"]
                    + " "
                    + race_object["url"]
                )

            new_text = json.dumps(race_object, sort_keys=True, indent=4)

            if os.path.exists(cleaned_filename):
                with open(cleaned_filename, "r") as f:
                    old_text = f.read()
                diff = unified_diff(old_text.splitlines(), new_text.splitlines())
                if diff:
                    for line in diff:
                        print(line)
            with open(cleaned_filename, "w") as f:
                json.dump(race_object, f, sort_keys=True, indent=4)
        # else:
        #     print(f"Already scraped {downloaded['name']}")

    if neiraschools.unmatched:
        print()
        print("Unmatched schools:")
        print("------------------")
        for x in neiraschools.unmatched:
            print(x)


def read_from_cache(cache_dir):
    for filename in os.listdir(cache_dir):
        with open(os.path.join(cache_dir, filename), "r") as f:
            res = json.load(f)
        yield res


@cli.command
# @click.argument("data_dir")
def review():
    data_dir = CONFIG["cleaned_dir"]
    neira.scraper.review.review(data_dir)


@cli.command()
# @click.argument("corrections_file")
# @click.argument("input_dir")
# @click.argument("output_dir")
def apply_corrections():  # corrections_file, input_dir, output_dir):
    corrections_file = CONFIG["corrections_file"]
    input_dir = CONFIG["cleaned_dir"]
    output_dir = CONFIG["reviewed_dir"]
    neira.scraper.apply_corrections.apply_corrections(
        corrections_file, input_dir, output_dir
    )


@cli.command()
@click.argument("data")
@click.argument("out")
def dot(data, out):
    neira.dot.read.main(data, out)


@cli.command()
@click.argument("html_dir")
def head_to_head(html_dir):
    neira.head_to_head.head_to_head.head_to_head(CONFIG["reviewed_dir"], html_dir)


@cli.command()
# @click.argument("html_dir")
def founders_day():
    neira.founders_day.founders_day()


@cli.command()
@click.argument("data_dir")
def ranking(data_dir):
    neira.head_to_head.head_to_head.rank_by_most_recent_head_to_head(data_dir)


@cli.command()
# @click.argument("data_dir")
# @click.option("--class", "class_", is_flag=False)
# @click.option("--gender", is_flag=False)
# @click.option("--varsity", is_flag=False)
# @click.option(
#     "--ranking",
#     is_flag=False,
#     default="",
#     show_default=True,
#     metavar="<ranking>",
#     type=click.STRING,
#     help="List of schools in order",
# )
def critique():  # data_dir, class_, gender, varsity, ranking):
    rankings_files = CONFIG["rankings"]
    data_dir = CONFIG["reviewed_dir"]
    for x in rankings_files:
        print(x)
        class_, gender, varsity = x.split("-")

        with open(rankings_files[x]) as f:
            ranking = json.load(f)

        print(ranking)

        neira.head_to_head.head_to_head.critique(
            data_dir, class_, gender, varsity, ranking
        )


@cli.command()
# @click.option("--class", "class_", is_flag=False)
# @click.option("--gender", is_flag=False)
# @click.option("--varsity", is_flag=False)
@click.argument("school1")
@click.argument("school2")
def compare(school1, school2):
    data_dir = CONFIG["reviewed_dir"]

    class_, gender, varsity = "fours", "girls", "1"

    neira.head_to_head.head_to_head.compare(
        data_dir, class_, gender, varsity, school1, school2
    )


@cli.command()
def compare_all():
    data_dir = CONFIG["reviewed_dir"]

    class_, gender = "fours", "girls"

    for varsity in ("1", "2", "3", "4"):
        out_dir = f"compare/{class_}-{gender}-{varsity}"
        neira.head_to_head.head_to_head.compare_all(
            data_dir, out_dir, class_, gender, varsity
        )


if __name__ == "__main__":
    cli()
