import datetime
from bs4 import BeautifulSoup


def scrape_cat_1(name, html, url, year):
    name = name.strip()

    # Open the url
    soup = BeautifulSoup(html, features="html.parser")
    
    date, comment, location = scrape_regatta_metadata(soup, year)

    heats = []
    for result_block in soup.findAll(True, {"class": ["results-block"]}):
        scrape_result_block(result_block, heats)

    scraped = {
        "date": date,
        "name": name,
        "date": date,
        "comment": comment,
        "url": url,
        "heats": heats,
        "location": location,
    }

    return scraped


def scrape_cat_5(name, html, url, year):
    name = name.strip()

    # Open the url
    soup = BeautifulSoup(html, features="html.parser")

    date, comment, location = scrape_regatta_metadata(soup, year)

    span_name_to_gender = {
        "Men's Racing": "boys",
        "Women's Racing": "girls",
    }

    gender = None
    heats = []
    for result_block in soup.findAll(True, {"class": ["results-block", "midhead2"]}):
        if result_block.name == "span":
            gender = span_name_to_gender.get(result_block.text)
        else:
            scrape_result_block(result_block, heats, gender=gender)

    scraped = {
        "date": date,
        "name": name,
        "date": date,
        "comment": comment,
        "url": url,
        "heats": heats,
        "location": location
    }

    return scraped


def scrape_regatta_metadata(soup, year):
    # Get the title of the page
    try:
        title = soup.findAll("meta", {"name": "description"})[0]["content"]
        date = ",".join(title.split("-")[-2].split(",")[-2:]).strip()
    except Exception as e:
        date = " ".join(
            (soup.findAll("title")[0].text.split(year)[0] + year).split()[-3:]
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

    date = clean_date(date)

    for line in soup.findAll("span", {"class": "midhead"})[0].parent.text.strip().split("\n"):
        if str(year) in line and "-" in line and "NEIRA" not in line:
            location = "-".join(line.split("-")[1:]).strip()
            break
    else:
        location = ""

    return date, comment.strip(), location

def scrape_result_block(result_block, heats, gender=None):
    heat = result_block.findAll("tr", {"align": "center"})[0].text.strip()

    varsity_indexes = {
        "First Boat": "1",
        "Second Boat": "2",
        "Third Boat": "3",
        "Fourth Boat": "4",
        "Fifth Boat": "5",
        "Sixth Boat": "6",
    }

    varsity_index = varsity_indexes.get(heat.rstrip(':'))

    if varsity_index is None:
        if "1V" in heat:
            varsity_index = "1"
        if "2V" in heat:
            varsity_index = "2"
        if "3V" in heat:
            varsity_index = "3"
        if "4V" in heat:
            varsity_index = "4"
        if "5V" in heat:
            varsity_index = "5"
        if "6V" in heat:
            varsity_index = "6"

    school_times = []
    for school_time in result_block.findAll("tr")[1:]:
        school_time = school_time.findAll("td")
        rawschool = school_time[0].text.encode("utf-8").strip().decode()
        if rawschool == "":
            continue
        time = school_time[1].text.encode("utf-8").strip().decode()
        school_times.append({"school": rawschool, "raw_time": time, "margin_from_winner": None, "finish_order": len(school_times) + 1})

    heats.append(
        {
            "class": None,
            "varsity_index": varsity_index,
            "results": school_times,
            "gender": gender,
        }
    )


def clean_date(date):
    return datetime.datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")


if __name__ == "__main__":
    import requests
    url = "https://www.row2k.com/results/resultspage.cfm?UID=F633B39B972009BAAE9DBEA29158C86C&cat=5"
    html = requests.get(url).text
    downloaded = {"html": html, "name": "foo", "url": url, "uid": "F633B39B972009BAAE9DBEA29158C86C"}
    scrape_cat_5("foo", html, url)