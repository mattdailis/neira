from difflib import SequenceMatcher as sm

matched = set()
unmatched = set()


def getNeiraSchools():
    # return {'BBN': ["BB&N"],
    #         'Bancroft' : [],
    #         'Belmont Hill' : [],
    #         'Berkshire' : [],
    #         'Brooks' : [],
    #         'CRLS' : [],
    #         'Canterbury' : [],
    #         'Choate' : [],
    #         'Deerfield' : [],
    #         'Derryfield' : [],
    #         'Dexter' : [],
    #         'Duxbury' : [],
    #         'Greenwich Academy' : ['GA', 'Greenwich A', 'Greenwich Acad', 'Greenwich'],
    #         'Groton' : [],
    #         'Gunnery' : ['The Gunnery'],
    #         'Hopkins' : ['Hop'],
    #         'Lincoln' : [],
    #         'Lyme/Old Lyme' : ['LOL', 'L//OL', 'L/OL'],
    #         'Medford' : [],
    #         'Middlesex' : [],
    #         'Milton' : ['MHS'],
    #         'Miss Porters' : ['M Porters', 'MPS'],
    #         'Newton Country Day' : ['NCDS'],
    #         'Nobles' : [],
    #         'Pomfret' : [],
    #         'Southfield' : [],
    #         'St Marks' : ['Saint Marks'],
    #         'Taft' : [],
    #         'Valley' : ['Valley Regional'],
    #         'Winsor' : [],
    #         # NOT ACTUALLY NEIRA, but included to avoid matching one of the above
    #         'Exeter' : [],
    #         'Middletown' : [],
    #         'Worcester Academy': [],
    #         'Bedford' : [],
    #         'Suffield': [],
    #
    #         # Added 2023:
    #         "Andover": [],
    #         "Bedford": [],
    #         "Berwick": [],
    #         "Boston Latin": [],
    #         "Brewster Academy": [],
    #         "Brookline": [],
    #         "Cambridge Ringe and Latin School": ["Cambridge RLS"],
    #         "East Lyme": [],
    #         "E.O. Smith": [],
    #         "Fairfield Prep": [],
    #         "Farmington": [],
    #         "Glastonbury": [],
    #         "Guilford": [],
    #         "Hingham": [],
    #         "Kent": [],
    #         "Salisbury": [],
    #         "Shrewsbury": [],
    #         "St. John's Prep": [],
    #         "Stonington": [],
    #         "Thayer": ["Thayer 1V"]
    # },

    return {
        # Girls schools
        "Bancroft": [],
        "Berkshire": [],
        "Berwick": [],
        "Brewster": [],
        "Brooks": [],
        "BU Academy": [],
        "BB&N": [],
        "CRLS": [],
        "Canterbury": [],
        "Choate": [],
        "Derryfield": [],
        "DXSF": [],
        "Eagle Hill": [],
        "Frederick Gunn": [],
        "Greenwich Academy": [],
        "Greenwich CD": [],
        "Groton": [],
        "Hopkins": [],
        "Lincoln": [],
        "Lyme Old Lyme": ["LOL", "L//OL", "L/OL"],
        "Marianapolis": [],
        "Medford": [],
        "Middlesex": [],
        "Middletown HS": [],
        "MPS": [],
        "NCDS": [],
        "Nobles": [],
        "NMH": [],
        "Pingree": [],
        "Pomfret": [],
        "SMS": [],
        "St. Mary's - Bay View": [],
        "St. Mary's -Lynn": [],
        "Suffield": [],
        "Taft": [],
        "Thayer": [],
        "Valley Regional": [],
        "Vermont Academy": [],
        "Winsor": [],
        "Worcester Academy": [],
        "Worcester HS": [],
        # Additional boys schools
        "Belmont Hill": [],
    }

    return {
        "Bancroft": [],
        "BB&N": ["BBN"],
        "Berkshire Academy": ["Berkshire"],
        "Berwick": [],
        "Brewster Academy": ["Brewster"],
        "Brooks": [],
        "Canterbury": [],
        "Choate": [],
        "Cambridge RLS": ["Cambridge Ringe and Latin School", "CRLS"],
        "Derryfield": [],
        "Dexter-Southfield": ["Dexter"],
        "Eagle Hill": [],
        "Forman": [],
        "Greenwich Academy": ["GA", "Greenwich A", "Greenwich Acad", "Greenwich"],
        "Greenwich Country Day": [],
        "Groton": [],
        "Gunn School": [
            "The Frederick Gunn School",
            "Gunnery",
            "The Gunnery",
            "Gunn",
            "Frederick Gunn",
        ],
        "Hopkins": ["Hop"],
        "Lincoln": [],
        "Lyme/Old Lyme": ["LOL", "L//OL", "L/OL"],
        "Marianapolis Prep": [],
        "Medford": [],
        "Middlesex": [],
        "Middletown": [],
        "Miss Porter's": [],
        "Newton Country Day": ["NCDS"],
        "Nobles": [],
        "NMH": ["Northfield Mount Hermon"],
        "Pingree": [],
        "Pomfret": [],
        "St. Mark's": [],
        "St. Mary's - Lynn": [],
        "Suffield": [],
        "Taft": [],
        "Thayer": [],
        "Valley Regional": [],
        "Vermont Academy": ["VA"],
        "Winsor": [],
        "Worcester Academy": [],
        "King School": [],
    }


# If boatNum provided, check if a different number is present in the string.
# If a different number is present in the string, append that number to the school name
# For example, if Boys 1 is competing in a Boys 2 race, it should be considered a different
# boat from that school's Boys 2.
# Ex:
# boys 2 fours:
# Hopkins 2 : time
# Derryfield 2 : time
# Hopkins 3 : time
# Results:
# Hopkins > Derryfield
# Hopkins > Hopkins 3
# Derryfield > Hopkins 3


# What about a boys 3 boat that still wants to be considered a 3rd boat, but races 2nd boats occasionally
# should those races count? Towards what? Margins????
def matchSchool(name, boatNum=None):
    if name is None:
        return (None, None)
    # Preprocess name to remove boat info
    name_for_score = name.replace("Boys", "").replace("Girls", "").replace("Novice", "")

    neira = getNeiraSchools()
    scores = set([])
    for school in neira:
        score = compare(school, name_for_score)
        for nick in neira[school]:
            newscore = compare(name_for_score, nick)
            if newscore > score:
                score = newscore
        scores.add((school, score))
    (school, score) = max(scores, key=(lambda x_y: x_y[1]))

    if name in ["Exeter", "Bedford", "Suffield", "Kent School", "Kent"]:
        return (None, None)

    # if school == 'Greenwich Academy':
    #     name = name.replace(" A", " Academy ")

    num = boatNum

    if boatNum != None:
        if boatNum == "novice":
            expectedNum = 0
        else:
            expectedNum = int(boatNum)

        # Check for the boat number. Ex: "Hopkins 4"
        if len(name.split(" ")) > 1:
            numStrings = name.replace("/", " ").split(" ")
            for numString in numStrings:
                try:
                    num = parseNum(numString)
                    # if expectedNum != num:
                    #     if num == 0:
                    #         num = "novice"
                    #         school += " " + str(num)
                    break
                except ValueError:
                    pass

    if score > 0.7:
        if (name, school) not in matched and name != school:
            print(name, "~", school)
        matched.add((name, school))
        return (school, num)
    else:
        unmatched.add(name)
        # return (name, boatNum)
        return (None, None)


def parseNum(num):
    if "nov" in num:
        return 0
    if len(num) == 1:
        return int(replaceLetters(num))
    else:
        raise ValueError


def replaceLetters(string):
    # n first for novice
    alpha = "nabcdefghijklmopqrstuvwxyz"
    low = string.lower()
    for letter in alpha:
        low = low.replace(letter, str(alpha.index(letter)))
    return low


def deUnique(string):
    return list(filter((lambda s: str.isalnum(s) and not s.isdigit()), string.lower()))


def compare(school, name):
    return sm(None, deUnique(school), deUnique(name)).ratio()
