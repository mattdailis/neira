from bs4 import BeautifulSoup
import datetime
import re
import json
import os
import requests

import click


def scrapeRegatta(name, res_url, url):
    """
    Given the name of the regatta (From the list of regattas) and the link to the row2k page for that regatta,
    return an object representing the important information in that page.
    TODO: Make a class representing the contents of a page
    """
    name = name.strip()

    # Open the url
    html = requests.get(res_url + url).text
    soup = BeautifulSoup(html, features="html.parser")

    # Get the title of the page
    try:
        title = soup.findAll("meta", {"name": "description"})[0]["content"]
        date = ",".join(title.split("-")[-2].split(",")[-2:]).strip()
    except Exception as e:
        print(e)
        # title = soup.findAll("meta", { "name" : "description"})[0]['content']
        # dayString =  ','.join(title.split('-')[-2].split(',')[-2:])
        date = " ".join(
            (soup.findAll("title")[0].text.split("2024")[0] + "2024").split()[-3:]
        ).strip()

    # Get the comment for the day
    blockquote = soup.findAll("div", {"class": "res-text"})[0]
    comment = blockquote.text.encode("utf-8").decode()
    p = str(blockquote.p).split("<br>")
    for t in p:
        comment += "\n"
        comment += t.replace("<p>", "").replace("</br>", "").replace("</p>", "").strip()
    if comment == None:
        comment = ""

    spans = []
    heats = []
    for result_block in soup.findAll(True, {"class": ["results-block", "midhead2"]}):
        if result_block.name == "span":
            heats = []
            spans.append({"name": result_block.text, "heats": heats})
            continue
        elif not spans:
            spans.append({"name": None, "heats": heats})

        heat = result_block.findAll("tr", {"align": "center"})[0].text.strip()

        school_times = []
        for school_time in result_block.findAll("tr")[1:]:
            school_time = school_time.findAll("td")
            rawschool = school_time[0].text.encode("utf-8").strip().decode()
            if rawschool == "":
                continue
            time = school_time[1].text.encode("utf-8").strip().decode()
            school_times.append({"school": rawschool, "time": time})

        heats.append(
            {
                "heat": heat,
                "school_times": school_times,
            }
        )

    scraped = {
        "spans": spans,
        "date": date,
        "name": name,
        "date": date,
        "comment": comment,
        "url": res_url + url,
    }

    return scraped


# Returns a list of urls
def getRaceUrls(res_html):
    urls = []
    soup = BeautifulSoup(res_html, features="html.parser")
    highschool = soup.findChildren("span", string="High School/Scholastic")
    for bulletList in highschool:
        links = bulletList.parent.parent.find_all("a")
        for link in links:
            if link.get("href").startswith("/results"):
                raceName = link.text.encode("utf-8")
                url = link.get("href").encode("utf-8")
                urls.append((raceName.decode(), url.decode()))
            else:
                print((link.get("href"), "could not be scraped"))
    return urls
