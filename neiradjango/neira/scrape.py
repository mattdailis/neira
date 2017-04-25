from bs4 import BeautifulSoup
import urllib2
import datetime
from neiraschools import match_school, get_schools
from models import Heat, School, Result, Boat


# def getUrlsScraped():
#     cur.execute("""
#     SELECT race, url FROM Results
#     """)
#     return set([(x[0], x[1]) for x in cur.fetchall()])

def scrape_regatta(name, url, res_url):
    print "Scraping", name
    html = urllib2.urlopen(res_url + url)
    soup = BeautifulSoup(html)
    title = soup.findAll("meta", {"name": "description"})[0]['content']
    day_string = ','.join(title.split('-')[-2].split(',')[-2:])

    day = get_date(day_string.strip())

    block_quote = soup.findAll("div", {"class": "res-text"})[0]

    comment = block_quote.text.encode('utf-8')
    p = str(block_quote.p).split('<br>')
    for t in p:
        comment += "\n"
        comment += t.replace('<p>', "").replace('</br>', "").replace('</p>', "").strip()
    if comment is None:
        comment = ""

    results = soup.findAll(True, {"class": ["results-block", "midhead2"]})

    gender = None
    if "boy" in name.lower() and not "girl" in name.lower():
        gender = "boys"
    elif "girl" in name.lower() and not "boy" in name.lower():
        gender = "girls"

    boat_size = "four"  # assume fours
    if "eight" in name.lower() or "8" in name and not ("four" in name.lower() or "4" in name):
        boat_size = "eight"
    elif "four" in name.lower() or "4" in name and not ("eight" in name.lower() or "8" in name):
        boat_size = "four"

    ## Sometimes the title of the race has a list of all the participating schools - take advantage of that if it exists
    schools_list = None
    if "vs." in name:
        try:
            school_names = map(lambda x: x.strip(), name[name.index(":") + 2:].replace("vs.", ",").split(","))
        except ValueError:
            pass
        schools_list = get_schools(school_names)

    current_heat_times = []

    schoollog = ""
    boatlog = ""

    for resultBlock in results:
        if resultBlock.name == 'span':
            if 'women' in resultBlock.text.lower():
                gender = "girls"
            # else:
            #     gender = "boys"
            continue
        heat = resultBlock.findAll("tr", {"align": "center"})[0].text.strip()
        (gender, boat_num, boat_size) = parse_boat(gender, boat_size, heat)

        for school_time in resultBlock.findAll("tr")[1:]:
            school_time = school_time.findAll("td")
            raw_school = school_time[0].text.encode('utf-8').strip()
            if raw_school == "":
                continue
            (school, num) = match_school(raw_school, boatNum=boat_num, subset=schools_list)
            time = school_time[1].text.encode('utf-8').strip()
            # if school is None, it's not in NEIRA
            if school is not None:
                current_heat_times.append((school, num, time))

        enter_heat(current_heat_times, gender, day, name, comment, res_url + url, boat_size)
        current_heat_times = []
    return schoollog, boatlog


def enter_heat(results, gender, date, race, comment, url, size):
    # Create new Heat object
    h = Heat()
    h.comment = comment
    h.url = url
    h.date = date
    h.save()

    # For each result
    for (school, level, time) in results:
        b = get_boat(school, gender, level, size)
        t = get_time(time)
        r = Result()
        r.raw_boat = str(school) + " " + str(gender) + " " + str(level)
        r.raw_time = str(time)
        r.boat = b
        if t is None:
            t = datetime.timedelta(hours=-1)  # if unable to parse time, set to an invalid (negative) time
        r.time = t
        r.heat = h
        r.save()


def get_boat(school, team, level, size):
    s = get_school(school)
    # Filter school
    boats = s.boat_set.filter(team=team, level=level)
    if boats.count() == 1:
        return boats[0]

    if boats.count() == 0:
        b = Boat()
        b.school = s
        b.team = team
        b.level = level
        b.size = size
        # size
        b.save()
        return b

    raise Exception("There are more than one boat with school {}, team {}, level, {}".format(school, team, level))


def get_school(school):
    return school
    # try:
    #     return School.objects.get(name=school)
    # except School.DoesNotExist:
    #     s = School()
    #     s.name = school
    #     s.save()
    #     return s


def get_margin(time1, time2):
    time1 = get_time(time1)
    time2 = get_time(time2)
    if time1 is None or time2 is None:
        return None
    return (time2 - time1).total_seconds()


def get_time(time):
    time = clean_time(time)
    try:
        dt = datetime.datetime.strptime(time, "%M:%S.%f")
    except:
        try:
            dt = datetime.datetime.strptime(time, "%M.%S.%f")
        except:
            try:
                dt = datetime.datetime.strptime(time, "%M:%S")
            except:
                dt = None
    if dt is not None:
        t = dt.time()
        return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)


def clean_time(string):
    return string.replace("!", "1").replace(" ", "")


def parse_boat(gender, boat_size, boat_string):
    number = None
    if gender is None:
        if "g" in boat_string.lower().replace("eig", ""):
            gender = "girls"
        elif "b" in boat_string.lower():
            gender = "boys"

    if "1" in boat_string or "one" in boat_string.lower() or "first" in boat_string.lower() or "st" in boat_string.lower():
        number = "1"
    elif "2" in boat_string or "two" in boat_string.lower() or "second" in boat_string.lower() or "nd" in boat_string.lower():
        number = "2"
    elif "n" in boat_string.lower().replace("nd", "").replace("ne", "").replace("en", ""):
        number = "novice"
    elif "3" in boat_string or "three" in boat_string.lower() or "third" in boat_string.lower() or "rd" in boat_string.lower():
        number = "3"
    elif "fourth" in boat_string.lower() or "4th" in boat_string.lower():
        number = "4"
    elif "5" in boat_string or "five" in boat_string.lower() or "fifth" in boat_string.lower():
        number = "5"
    elif "6" in boat_string or "six" in boat_string.lower() or "sixth" in boat_string.lower():
        number = "6"
    elif "7" in boat_string or "seven" in boat_string.lower():
        number = "6"
    elif "4" in boat_string or "four" in boat_string.lower():
        number = "4"

    if number != "4" and ("4" in boat_string or "four" in boat_string.lower()):
        boat_size = "four"
    elif "8" in boat_string or "eight" in boat_string.lower():
        boat_size = "eight"

    return gender, number, boat_size


# string to date object
# Assumes format "Sunday, March 6, 2016"
def get_date(string):
    # f = "%A, %B %d, %Y"
    f = "%B %d, %Y"
    d = datetime.datetime.strptime(string, f).date()
    return d


# Returns a list of urls
def get_race_urls(urls_scraped, res_html):
    urls = []
    soup = BeautifulSoup(res_html)
    high_school = soup.findChildren('span', text="High School/Scholastic")
    for bulletList in high_school:
        links = bulletList.parent.parent.find_all("a")
        for link in links:
            if link.get('href').startswith('/results'):
                race_name = link.text.encode('utf-8')
                url = link.get('href').encode('utf-8')
                urls.append((race_name, url))
            else:
                print link.get('href'), "could not be scraped"
    return urls  # .difference(urls_scraped)


# expected bug: when program terminates mid-scrape, should redo that url next time


def main():
    res_url = 'http://www.row2k.com'
    import urllib2
    res_html = urllib2.urlopen(res_url + "/results/index.cfm?league=NEIRA&year=2017")

    urls_scraped = []  # getUrlsScraped()

    urls = get_race_urls(urls_scraped, res_html)
    # schools = open("schoolslog.txt", "w")
    # boats = open("boatslog.txt", "w")
    if len(urls) > 0:
        for (race, url) in urls:
            (schoollog, boatlog) = scrape_regatta(race, url, res_url)
            # schools.write(schoollog)
            # boats.write(boatlog)

            # schools.close()
            # boats.close()


# if __name__ == '__main__':
main()
