import re
from typing import Tuple
from bs4 import BeautifulSoup
import requests


def download_all(year):
    urls = get_race_urls(year)

    yield from map(download_one, urls)


def download_one(name_uid_url):
    name, uid, url = name_uid_url
    html = requests.get(url).text
    return {"html": html, "name": name, "url": url, "uid": uid}

# https://www.row2k.com/results/index.cfm?league=NEIRA&year=2026

# Returns a list of urls
def get_race_urls(year) -> Tuple[str, str, str]:
    base_url = "https://www.row2k.com"
    html = requests.get(
        base_url + f"/results/index.cfm?league=NEIRA&year={year}"
    ).text
    urls = get_urls_from_html(base_url, html)
    html = requests.get(
        base_url + f"/results/index.cfm?year={year}"
    ).text
    urls.extend(get_urls_from_html(base_url, html, filter="NEIRA"))
    return sorted(set(urls))

def get_urls_from_html(base_url, html, filter=None):
    urls = []
    soup = BeautifulSoup(html, features="html.parser")
    highschool = soup.findChildren("span", string="High School/Scholastic")
    for bulletList in highschool:
        links = bulletList.parent.parent.find_all("a")
        for link in links:
            regatta_name = link.text.encode("utf-8").decode()
            if link.get("href").startswith("/results") and filter is None or filter in regatta_name:
                url = link.get("href").encode("utf-8").decode()
                uid = re.match(r".*UID=([0-9|A-Z]+)", url, re.M | re.I).group(1)
                urls.append((regatta_name, uid, base_url + url))
            else:
                print((link.get("href"), "could not be scraped"))        
    return urls
