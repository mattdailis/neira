from difflib import SequenceMatcher as sm

def getNeiraSchools():
    return {'BBN': [],
            'Bancroft' : [],
            'Belmont Hill' : [],
            'Berkshire' : [],
            'Brooks' : [],
            'CRLS' : [],
            'Canterbury' : [],
            'Choate' : [],
            'Deerfield' : [],
            'Derryfield' : [],
            'Dexter' : [],
            'Duxbury' : [],
            'Greenwich Academy' : ['GA', 'Greenwich A', 'Greenwich Acad', 'Greenwich'],
            'Groton' : [],
            'Gunnery' : ['The Gunnery'],
            'Hopkins' : ['Hop'],
            'Lincoln' : [],
            'Lyme/Old Lyme' : ['LOL', 'L//OL', 'L/OL'],
            'Medford' : [],
            'Middlesex' : [],
            'Milton' : [],
            'Miss Porters' : ['M Porters', 'MPS'],
            'Newton Country Day' : ['NCDS'],
            'Nobles' : [],
            'Pomfret' : [],
            'Southfield' : [],
            'St Marks' : ['Saint Marks'],
            'Taft' : [],
            'Valley' : ['Valley Regional'],
            'Winsor' : [],
            # NOT ACTUALLY NEIRA:
            'Exeter' : [],
            'Middletown' : [],
            'Suffield': []
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
    neira = getNeiraSchools()
    scores = set([])
    for school in neira:
        score = compare(school, name)
        for nick in neira[school]:
            newscore = compare(name, nick)
            if newscore > score:
                score = newscore
        scores.add((school, score))
    (school, score) = max(scores, key=(lambda (x, y) : y))

    if school in ['Exeter', 'Middletown', 'Suffield']:
        return (None, None)

    if school == 'Greenwich Academy':
        name = name.replace(" A", " Academy ")

    num = boatNum

    if boatNum != None:
        if boatNum == 'novice':
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
        return (school, num)
    else:
        return (None, None)

def parseNum(num):
    if 'nov' in num:
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
    return filter((lambda s : str.isalnum(s) and not s.isdigit()), string.lower())

def compare(school, name):
    return sm(None, deUnique(school), deUnique(name)).ratio()
