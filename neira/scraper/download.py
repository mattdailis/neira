import json
import os
import re
from bs4 import BeautifulSoup
import requests


def download_all(year):
    urls = getRaceUrls(year)

    yield from map(download_one, urls)


def download_one(name_uid_url):
    name, uid, url = name_uid_url
    html = requests.get(url).text
    return {"html": html, "name": name, "url": url, "uid": uid}


# Returns a list of urls
def getRaceUrls(year):
    res_url = "https://www.row2k.com"
    res_html = requests.get(
        res_url + f"/results/index.cfm?league=NEIRA&year={year}"
    ).text
    urls = []
    soup = BeautifulSoup(res_html, features="html.parser")
    highschool = soup.findChildren("span", string="High School/Scholastic")
    for bulletList in highschool:
        links = bulletList.parent.parent.find_all("a")
        for link in links:
            if link.get("href").startswith("/results"):
                raceName = link.text.encode("utf-8").decode()
                url = link.get("href").encode("utf-8").decode()
                uid = re.match(r".*UID=([0-9|A-Z]+)", url, re.M | re.I).group(1)
                urls.append((raceName, uid, res_url + url))
            else:
                print((link.get("href"), "could not be scraped"))
    return urls
