import json
import os
import re

import click
import requests

from scrape import scrapeRegatta, getRaceUrls

import clean

import neiraschools


@click.command()
@click.argument("out")
def main(out):
    out_dir = out
    year = 2024
    res_url = "https://www.row2k.com"
    res_html = requests.get(
        res_url + f"/results/index.cfm?league=NEIRA&year={year}"
    ).text

    urls = getRaceUrls(res_html)

    OVERWRITE = False

    total = len(urls)

    if len(urls) > 0:
        for i, (race, url) in enumerate(urls):
            i = i + 1
            uid = re.match(r".*UID=([0-9|A-Z]+)", url, re.M | re.I).group(1)
            scraped_filename = os.path.join(out_dir, "{}-scraped.json".format(uid))
            cleaned_filename = os.path.join(out_dir, "{}.json".format(uid))
            if OVERWRITE or not os.path.isfile(cleaned_filename):
                print(f"Scraping {i}/{total}: {race}")
                scraped = scrapeRegatta(race, res_url, url)
                # with open(scraped_filename, "w") as f:
                #     f.write(json.dumps(scraped, sort_keys=True, indent=4))
                race_object = clean.clean(scraped)
                with open(cleaned_filename, "w") as f:
                    f.write(json.dumps(race_object, sort_keys=True, indent=4))
            else:
                print(f"{i}/{total}: Already scraped {race}")

    if neiraschools.unmatched:
        print()
        print("Unmatched schools:")
        print("------------------")
        for x in neiraschools.unmatched:
            print(x)


if __name__ == "__main__":
    main()
