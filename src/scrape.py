from bs4 import BeautifulSoup
import urllib2
import datetime
from datetime import date
import re
from neiraschools import matchSchool
import json
import os

def scrapeRegatta(name, res_url, url):
    """
    Given the name of the regatta (From the list of regattas) and the link to the row2k page for that regatta,
    return an object representing the important information in that page.
    TODO: Make a class representing the contents of a page
    """

    name = name.strip()

    # Open the url
    html = urllib2.urlopen(res_url+url)
    soup = BeautifulSoup(html)

    # Get the title of the page
    title = soup.findAll("meta", { "name" : "description"})[0]['content']
    dayString =  ','.join(title.split('-')[-2].split(',')[-2:])

    # Get the date of the event
    # day = getDate(dayString.strip())
    day = dayString.strip()

    # Get the comment for the day
    blockquote = soup.findAll("div", { "class" : "res-text"})[0]
    comment = blockquote.text.encode('utf-8')
    p = str(blockquote.p).split('<br>')
    for t in p:
        comment += "\n"
        comment += t.replace('<p>', "").replace('</br>', "").replace('</p>', "").strip()
    if comment == None:
        comment = ""

    # Guess the gender from the name, if possible. Else None
    gender = None
    if "boy" in name.lower() and not "girl" in name.lower():
        gender = "boys"
    elif "girl" in name.lower() and not "boy" in name.lower():
        gender = "girls"

    # Guess the boat size from the name. Else "fours"
    boatSize = "fours" # assume fours
    if "eight" in name.lower() or "8" in name and not ("four" in name.lower() or "4" in name):
        boatSize = "eights"
    elif "four" in name.lower() or "4" in name and not ("eight" in name.lower() or "8" in name):
        boatSize = "fours"

    currentHeat = []
    boatNum = None

    heats = []

    race_object = {
        "day": day,
        "regatta_display_name": name,
        "comment": comment,
        "url": res_url+url
    }

#    results = soup.findAll("div", {"class" : "results-block"})
    results = soup.findAll(True, {"class": ["results-block", "midhead2"]})

    
    for resultBlock in results:
        if resultBlock.name == 'span':
            if 'women' in resultBlock.text.lower():
                gender = "girls"
            # else:
            #     gender = "boys"
            continue

        heat = resultBlock.findAll("tr", {"align" : "center"})[0].text.strip()
        (gender, boatNum, boatSize) = parseBoat(gender, boatSize, heat)

        for school_time in resultBlock.findAll("tr")[1:]:
            school_time = school_time.findAll("td")
            rawschool = school_time[0].text.encode('utf-8').strip()
            if rawschool == "":
                continue
            # (school, num) = matchSchool(rawschool, boatNum=boatNum)
            time = school_time[1].text.encode('utf-8').strip()
            currentHeat.append((rawschool, time))

        heats.append({
            "class": str(boatSize),
            "varsity_index": str(boatNum),
            "results": currentHeat,
            "gender": gender})

        currentHeat = []
    race_object["heats"] = heats
    return race_object

def getMargin(time1, time2):
    time1 = getTime(time1)
    time2 = getTime(time2)
    if time1 == None or time2 == None:
        return None
    return (time2 - time1).total_seconds()

def getTime(time):
    time = cleanTime(time)
    try:
        return datetime.datetime.strptime(time, "%M:%S.%f")
    except:
        try:
            return datetime.datetime.strptime(time, "%M.%S.%f")
        except:
            try:
                return datetime.datetime.strptime(time, "%M:%S")
            except:
                return None

def cleanTime(string):
    return string.replace("!", "1").replace(" ", "")

def parseBoat(gender, boatSize, boatString):
    number = None
    if gender is None:
        if "g" in boatString.lower().replace("eig", ""):
            gender = "girls"
        elif "b" in boatString.lower():
            gender = "boys"


    if "1" in boatString or "one" in boatString.lower() or "first" in boatString.lower() or "st" in boatString.lower():
        number = "1"
    elif "2" in boatString or "two" in boatString.lower() or "second" in boatString.lower() or "nd" in boatString.lower():
        number = "2"
    elif "n" in boatString.lower().replace("nd", "").replace("ne", "").replace("en", ""):
        number = "novice"
    elif "3" in boatString or "three" in boatString.lower() or "third" in boatString.lower() or "rd" in boatString.lower():
        number = "3"
    elif "fourth" in boatString.lower() or "4th" in boatString.lower():
        number = "4"
    elif "5" in boatString or "five" in boatString.lower() or "fifth" in boatString.lower():
        number = "5"
    elif "6" in boatString or "six" in boatString.lower() or "sixth" in boatString.lower():
        number = "6"
    elif "7" in boatString or "seven" in boatString.lower():
        number = "6"
    elif "4" in boatString or "four" in boatString.lower():
        number = "4"

    if number != "4" and ("4" in boatString  or "four" in boatString.lower()):
        boatSize = "fours"
    elif "8" in boatString or "eight" in boatString.lower():
        boatSize = "eights"

    return (gender, number, boatSize)

# string to date object
# Assumes format "Sunday, March 6, 2016"
def getDate(string):
    # f = "%A, %B %d, %Y"
    f = "%B %d, %Y"
    d = datetime.datetime.strptime(string, f).date()
    return d

# Returns a list of urls
def getRaceUrls(res_html):
    urls = []
    soup = BeautifulSoup(res_html)
    highschool = soup.findChildren('span', text="High School/Scholastic")
    for bulletList in highschool:
        links = bulletList.parent.parent.find_all("a")
        for link in links:
            if link.get('href').startswith('/results'):
                raceName = link.text.encode('utf-8')
                url = link.get('href').encode('utf-8')
                urls.append((raceName, url))
            else:
                print(link.get('href'), "could not be scraped")
    return urls

# expected bug: when program terminates mid-scrape, should redo that url next time

def main():
    res_url = 'http://www.row2k.com'
    res_html = urllib2.urlopen(res_url+"/results/index.cfm?league=NEIRA&year=2019")

    urls_scraped = [] #getUrlsScraped()

    urls = getRaceUrls(res_html)
    count = 0

    OVERWRITE = False

    if len(urls) > 0:
        for (race, url) in urls:
            uid = re.match( r'.*UID=([0-9|A-Z]+)', url, re.M|re.I).group(1)
            filename = "data/{}.json".format(uid)
            if OVERWRITE or not os.path.isfile(filename):
                race_object = scrapeRegatta(race, res_url, url)
                with open(filename, "w") as f:
                    f.write(json.dumps(race_object, sort_keys=True, indent=4))

if __name__ == '__main__':
    main()