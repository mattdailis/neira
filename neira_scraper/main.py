import json
import os

import click

from download import download_all
from scrape import scrapeRegatta

import clean

import neiraschools


@click.command()
@click.argument("out")
@click.option("--raw-cache", type=str)
@click.option("--refresh/--use-cache")
def main(out, raw_cache=None, refresh=False):
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
            with open(cleaned_filename, "w") as f:
                f.write(json.dumps(race_object, sort_keys=True, indent=4))
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


if __name__ == "__main__":
    main()
