from difflib import SequenceMatcher as sm

matched = set()
unmatched = set()


# def getNeiraSchools():
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


boys_eights = {
    "Andover",
    "BC High",
    "Bedford",
    "Boston Latin",
    "Brookline",
    "Brunswick",
    "Deerfield",
    "Duxbury",
    "East Lyme",
    "E.O. Smith",
    "Exeter",
    "Fairfield Prep",
    "Farmington",
    "Glastonbury",
    "Guilford",
    "Hanover",
    "Hingham",
    "Hotchkiss",
    "Kent",
    "Salisbury",
    "Shrewsbury",
    "Simsbury",
    "St. John's",
    "St. John's Prep",
    "St. Paul's",
    "Stonington",
    "Tabor",
}

boys_fours = {
    "Bancroft",
    "BB&N",
    "Belmont Hill",
    "Berkshire Academy",
    "Berwick",
    "BU Academy",
    "Brewster Academy",
    "Brooks",
    "Canterbury",
    "Choate",
    "Cambridge RLS",
    "Derryfield",
    "Dexter-Southfield",
    "Eagle Hill",
    "Frederick Gunn",
    "Greenwich Country Day",
    "Groton",
    "Hopkins",
    "King School",
    "Lyme/Old Lyme",
    "Marianapolis Prep",
    "Medford",
    "Middlesex",
    "Middletown",
    "Nobles",
    "NMH",
    "Notre Dame",
    "Pingree",
    "Pomfret",
    "St. Mark's",
    "St. Mary's-Lynn",
    "Suffield",
    "Taft",
    "Thayer",
    "Valley Regional",
    "Vermont Academy",
    "Worcester Academy",
}

girls_eights = {
    "Andover",
    "Bedford",
    "Boston Latin",
    "Brookline",
    "Deerfield",
    "Duxbury",
    "E.O. Smith",
    "East Lyme",
    "Exeter",
    "Farmington",
    "Glastonbury",
    "Guilford",
    "Hanover",
    "Hingham",
    "Hotchkiss",
    "Kent",
    "Sacred Heart",
    "Shrewsbury",
    "Simsbury",
    "St. Paul's",
    "Stonington",
    "Tabor",
}

girls_fours = {
    "Bancroft",
    "BB&N",
    "Berkshire Academy",
    "Berwick",
    "BU Academy",
    "Brewster Academy",
    "Brooks",
    "Canterbury",
    "Choate",
    "Cambridge RLS",
    "Derryfield",
    "Dexter-Southfield",
    "Eagle Hill",
    "Greenwich Academy",
    "Greenwich Country Day",
    "Groton",
    "Frederick Gunn",
    "Hopkins",
    "Lincoln",
    "Lyme/Old Lyme",
    "Marianapolis Prep",
    "Medford",
    "Middlesex",
    "Middletown",
    "Miss Porter's",
    "Newton Country Day",
    "Nobles",
    "NMH",
    "Pingree",
    "Pomfret",
    "St. Mark's",
    "St. Mary Academy-Bay View",
    "St. Mary's-Lynn",
    "Suffield",
    "Taft",
    "Thayer",
    "Valley Regional",
    "Vermont Academy",
    "Winsor",
    "Worcester Academy",
}

other_schools = {
    "Andover/Bedford Composite",
    "Andover/St. John's Prep Composite",
    "Avon",
    "Bedford/Hanover Composite",
    "BHS Middle School",
    "Brooks and CRLS",
    "CRI",
    "Worcester Public",
}

neira_schools = boys_eights.union(boys_fours).union(girls_eights).union(girls_fours)

all_schools = neira_schools.union(other_schools)


aliases = {
    "Andover": [],
    "Bancroft": [],
    "BB&N": [],
    "BC High": [],
    "Bedford": [],
    "Belmont Hill": ["BHS"],
    "Berkshire Academy": ["Berkshire"],
    "Berwick": ["Berwick Mixed C"],
    "Boston Latin": ["BLS"],
    "Brewster Academy": ["Brewster"],
    "Brookline": [],
    "Brooks": [],
    "Brunswick": [],
    "BU Academy": [
        "Boston University Academy",
        "BUA",
    ],  # In dad's list but not in dropdown
    "Cambridge RLS": ["Cambridge Ringe and Latin School", "CRLS"],
    "Canterbury": [],
    "Choate": [],
    "Deerfield": [],
    "Derryfield": [],
    "Dexter-Southfield": ["DXSF"],
    "Duxbury": [],
    "E.O. Smith": [],
    "Eagle Hill": [],
    "East Lyme": [],
    "Exeter": [],
    "Fairfield Prep": [],
    "Farmington": [],
    "Frederick Gunn": [
        "The Frederick Gunn School",
        "Gunnery",
        "The Gunnery",
        "Gunn",
        "Frederick Gunn",
        "Gunn School",
    ],
    "Glastonbury": [],
    "Greenwich Academy": [],
    "Greenwich Country Day": ["Greenwich CD", "GCDS"],
    "Groton": [],
    "Guilford": [],
    "Hanover": [],
    "Hingham": [],
    "Hopkins": [],
    "Hotchkiss": [],
    "Kent": [],
    "King School": [],
    "Lincoln": [],
    "Lyme/Old Lyme": ["Lyme Old Lyme", "LOL", "L//OL", "L/OL"],
    "Marianapolis Prep": ["Marianapolis"],
    "Medford": [],
    "Middlesex": ["MX"],
    "Middletown": ["Middletown HS"],
    "Miss Porter's": ["MPS"],
    "Newton Country Day": ["NCDS"],
    "NMH": [],
    "Nobles": [],
    "Notre Dame": ["Notre Dame 3V"],
    "Pingree": [],
    "Pomfret": [],
    "Sacred Heart": [],
    "Salisbury": [],
    "Shrewsbury": [],
    "Simsbury": [],
    "St. John's Prep": [],
    "St. John's": [],
    "St. Mark's": [],
    "St. Mary Academy-Bay View": ["St. Mary Academy - Bay View"],
    "St. Mary's-Lynn": ["St. Mary's - Lynn"],
    "St. Paul's": [],
    "Stonington": [],
    "Suffield": [],
    "Tabor": [],
    "Taft": [],
    "Thayer": [],
    "Valley Regional": [],
    "Vermont Academy": ["VA"],
    "Winsor": [],
    "Worcester Academy": [],
    "Worcester Public": ["Worcester HS"],
}

# return {
#     "Bancroft": [],
#     "BB&N": ["BBN"],
#     "Berkshire Academy": ["Berkshire"],
#     "Berwick": [],
#     "Brewster Academy": ["Brewster"],
#     "Brooks": [],
#     "Canterbury": [],
#     "Choate": [],
#     "Cambridge RLS": ["Cambridge Ringe and Latin School", "CRLS"],
#     "Derryfield": [],
#     "Dexter-Southfield": ["Dexter"],
#     "Eagle Hill": [],
#     "Forman": [],
#     "Greenwich Academy": ["GA", "Greenwich A", "Greenwich Acad", "Greenwich"],
#     "Greenwich Country Day": [],
#     "Groton": [],
#     "Gunn School": [
#         "The Frederick Gunn School",
#         "Gunnery",
#         "The Gunnery",
#         "Gunn",
#         "Frederick Gunn",
#     ],
#     "Hopkins": ["Hop"],
#     "Lincoln": [],
#     "Lyme/Old Lyme": ["LOL", "L//OL", "L/OL"],
#     "Marianapolis Prep": [],
#     "Medford": [],
#     "Middlesex": [],
#     "Middletown": [],
#     "Miss Porter's": [],
#     "Newton Country Day": ["NCDS"],
#     "Nobles": [],
#     "NMH": ["Northfield Mount Hermon"],
#     "Pingree": [],
#     "Pomfret": [],
#     "St. Mark's": [],
#     "St. Mary's - Lynn": [],
#     "Suffield": [],
#     "Taft": [],
#     "Thayer": [],
#     "Valley Regional": [],
#     "Vermont Academy": ["VA"],
#     "Winsor": [],
#     "Worcester Academy": [],
#     "King School": [],
# }


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
def match_school(name, class_, gender):
    relevant_schools = neira_schools
    if class_ == "eights":
        relevant_schools = relevant_schools.intersection(
            boys_eights.union(girls_eights)
        )
    if class_ == "fours":
        relevant_schools = relevant_schools.intersection(boys_fours.union(girls_fours))
    if gender == "boys":
        relevant_schools = relevant_schools.intersection(boys_fours.union(boys_eights))
    if gender == "girls":
        relevant_schools = relevant_schools.intersection(
            girls_fours.union(girls_eights)
        )

    # Preprocess name to remove boat info
    name_for_score = name.replace("Boys", "").replace("Girls", "").replace("Novice", "")
    scores = set()
    for school in all_schools:
        score = compare(school, name_for_score)
        if school in other_schools:
            continue
        for alias in aliases[school]:
            new_score = compare(name_for_score, alias)
            if new_score > score:
                score = new_score
        scores.add((school, score))
    (school, score) = max(scores, key=(lambda x_y: x_y[1]))

    if score > 0.7:
        matched.add((name, school))
        if school in relevant_schools:
            return school
        else:
            if (
                (school in girls_eights.union(girls_fours))
                and not (school in boys_eights.union(boys_fours))
                and gender == "boys"
            ):
                print(school, gender, class_)
                raise Exception("Wrong gender?")

            if (
                (school in boys_eights.union(boys_fours))
                and not (school in girls_eights.union(girls_fours))
                and gender == "girls"
            ):
                print(school, gender, class_)
                raise Exception("Wrong gender?")
            return None
    else:
        unmatched.add(name)
        # return (name, boatNum)
        return None


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
