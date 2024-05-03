from bs4 import BeautifulSoup


def scrapeRegatta(name, html):
    """
    Given the name of the regatta (From the list of regattas) and the link to the row2k page for that regatta,
    return an object representing the important information in that page.
    TODO: Make a class representing the contents of a page
    """
    name = name.strip()

    # Open the url
    soup = BeautifulSoup(html, features="html.parser")

    # Get the title of the page
    try:
        title = soup.findAll("meta", {"name": "description"})[0]["content"]
        date = ",".join(title.split("-")[-2].split(",")[-2:]).strip()
    except Exception as e:
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
    }

    return scraped
