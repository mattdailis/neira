from bs4 import BeautifulSoup
import urllib2
import datetime
from datetime import date
import re
from neiraschools import matchSchool
from models import Heat, School, Result, Boat

#--- Set up database ---#

import sqlite3

def createTable(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Results
    (date TEXT, gender TEXT, heat TEXT, fasterSchool TEXT, fasterBoat INTEGER, slowerSchool TEXT, slowerBoat TEXT, margin DECIMAL(5, 2), race TEXT, comment TEXT, url TEXT)""")
#   (date TEXT, faster TEXT, slower TEXT, boat TEXT, margin DECIMAL(5, 2), race TEXT, comment TEXT, url TEXT)""")

def sqlify(string):
    return string.replace("'", "")

def insert(date, gender, heat, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url):
    print slowerSchool, slowerBoat
    try:
        cur.execute(("""
        INSERT INTO Results (date, gender, heat, fasterSchool, fasterBoat, slowerSchool, slowerBoat,"""+(" margin," if margin != None else "")+""" race, comment, url) VALUES (
        '{date}', '{gender}', '{heat}', '{fasterSchool}', '{fasterBoat}', '{slowerSchool}', '{slowerBoat}',"""+(" {margin}," if margin != None else "")+""" '{race}', '{comment}', '{url}')""")\
                    .format(date=str(date),
                            gender=gender,
                            heat=sqlify(heat),
                            fasterSchool=sqlify(fasterSchool),
                            fasterBoat=str(fasterBoat),
                            slowerSchool=sqlify(slowerSchool),
                            slowerBoat=str(slowerBoat),
                            margin=str(margin),
                            race=sqlify(race),
                            comment=sqlify(comment),
                            url=sqlify(url)))
    except:
        print "NOT ENTERED: ", date, gender, heat, fasterSchool, fasterBoat, slowerSchool, slowerBoat, margin, race, comment, url

def getUrlsScraped():
    cur.execute("""
    SELECT race, url FROM Results
    """)
    return set([(x[0], x[1]) for x in cur.fetchall()])

#--- Set up scraper ---#

def scrapeRegatta(name, url):
    print "Scraping", name
    html = urllib2.urlopen(res_url+url)
    soup = BeautifulSoup(html)
    title = soup.findAll("meta", { "name" : "description"})[0]['content']
    dayString =  ','.join(title.split('-')[-2].split(',')[-2:])

    day = getDate(dayString.strip())

    blockquote = soup.findAll("div", { "class" : "res-text"})[0]


    comment = blockquote.text.encode('utf-8')
    p = str(blockquote.p).split('<br>')
    for t in p:
        comment += "\n"
        comment += t.replace('<p>', "").replace('</br>', "").replace('</p>', "").strip()
    if comment == None:
        comment = ""

    results = soup.findAll("div", {"class" : "results-block"})

    gender = None
    if "boy" in name.lower() and not "girl" in name.lower():
        gender = "boys"
    elif "girl" in name.lower() and not "boy" in name.lower():
        gender = "girls"

    boatSize = "four" # assume fours
    if "eight" in name.lower() or "8" in name and not ("four" in name.lower() or "4" in name):
        boatSize = "eight"
    elif "four" in name.lower() or "4" in name and not ("eight" in name.lower() or "8" in name):
        boatSize = "four"

    boat = None
    currentHeat = []
    boatNum = None

    schoollog = ""
    boatlog = ""

    for resultBlock in results:
        heat = resultBlock.findAll("tr", {"align" : "center"})[0].text.strip()
        (gender, boatNum, boatSize) = parseBoat(gender, boatSize, heat)

        for school_time in resultBlock.findAll("tr")[1:]:
            school_time = school_time.findAll("td")
            rawschool = school_time[0].text.encode('utf-8').strip()
            if rawschool == "":
                continue
            (school, num) = matchSchool(rawschool, boatNum=boatNum)
            schoollog +=  rawschool + " -> " + str(school) + "\n"
            time = school_time[1].text.encode('utf-8').strip()
            # if school is None, it's not in NEIRA
            if school != None:
                currentHeat.append((school, num, time))

        enterHeat(str(gender)+str(boatNum)+str(boatSize), currentHeat, gender, day, name, comment, res_url+url)
        currentHeat = []
    return (schoollog, boatlog)


def enterHeat(heat, results, gender, date, race, comment, url):
    i = 0
    while i < len(results) - 1:
        (fastSchool, fastBoat, t1) = results[i]
        for (slowSchool, slowBoat, t2) in results[i+1:]:
            margin = getMargin(t1, t2)
            insert(date, gender, heat, fastSchool, fastBoat, slowSchool, slowBoat, margin, race, comment, url)
        i += 1

    # Create new Heat object
    h = Heat()
    h.comment = comment
    h.url = url
    h.date = date
    
    
    # For each result
    for (school, level, time) in results:
        b = getBoat(school, gender, level)
        t = getTime(time)
        r = Result()
        r.raw_boat = str(school) + " " + str(gender) + " " + str(level)
        r.raw_time = str(time)
        r.boat = b
        r.time = t
        r.heat = h
        r.save()

def getBoat(school, team, level):
    return Boat()

def getSchool(school):
    return School.objects.get(name=school)

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
        boatSize = "four"
    elif "8" in boatString or "eight" in boatString.lower():
        boatSize = "eight"

    return (gender, number, boatSize)

# string to date object
# Assumes format "Sunday, March 6, 2016"
def getDate(string):
    # f = "%A, %B %d, %Y"
    f = "%B %d, %Y"
    d = datetime.datetime.strptime(string, f).date()
    return d

# Returns a list of urls
def getRaceUrls(urls_scraped):
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
                print link.get('href'), "could not be scraped"
    return urls#.difference(urls_scraped)

# expected bug: when program terminates mid-scrape, should redo that url next time

if __name__ == '__main__':
    conn = sqlite3.connect('../bin/row2k.sqlite3')
    cur = conn.cursor()

    createTable(cur)

    res_url = 'http://www.row2k.com'
    res_html = urllib2.urlopen(res_url+"/results/index.cfm?league=NEIRA&year=2017")

    urls_scraped = getUrlsScraped()

    urls = getRaceUrls(urls_scraped)
    schools = open("schoolslog.txt", "w")
    boats = open("boatslog.txt", "w")
    if len(urls) > 0:
        for (race, url) in urls:
            (schoollog, boatlog) = scrapeRegatta(race, url)
            schools.write(schoollog)
            boats.write(boatlog)

    schools.close()
    boats.close()

    conn.commit()
    cur.close()
