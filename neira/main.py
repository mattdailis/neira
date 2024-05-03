import warnings

import neira.scraper.apply_corrections

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


@click.group()
def cli():
    pass


@cli.command()
@click.argument("out")
@click.option("--raw-cache", type=str)
@click.option("--refresh/--use-cache")
def scrape(out, raw_cache=None, refresh=False):
    out_dir = out
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
@click.argument("data_dir")
def review(data_dir):
    neira.scraper.review.review(data_dir)


@cli.command()
@click.argument("corrections_file")
@click.argument("input_dir")
@click.argument("output_dir")
def apply_corrections(corrections_file, input_dir, output_dir):
    neira.scraper.apply_corrections.apply_corrections(
        corrections_file, input_dir, output_dir
    )


if __name__ == "__main__":
    cli()
