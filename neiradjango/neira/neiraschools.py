from difflib import SequenceMatcher

from models import School
import re

# def get_neira_schools():
#     return {'BBN': [],
#             'Bancroft' : [],
#             'Belmont Hill' : [],
#             'Berkshire' : [],
#             'Brooks' : [],
#             'CRLS' : [],
#             'Canterbury' : [],
#             'Choate' : [],
#             'Deerfield' : [],
#             'Derryfield' : [],
#             'Dexter' : [],
#             'Duxbury' : [],
#             'Greenwich Academy' : ['GA', 'Greenwich A', 'Greenwich Acad', 'Greenwich'],
#             'Groton' : [],
#             'Gunnery' : ['The Gunnery'],
#             'Hopkins' : ['Hop'],
#             'Lincoln' : [],
#             'Lyme/Old Lyme' : ['LOL', 'L//OL', 'L/OL'],
#             'Medford' : [],
#             'Middlesex' : [],
#             'Milton' : ['MHS'],
#             'Miss Porters' : ['M Porters', 'MPS'],
#             'Newton Country Day' : ['NCDS'],
#             'Nobles' : [],
#             'Pomfret' : [],
#             'Southfield' : [],
#             'St Marks' : ['Saint Marks'],
#             'Taft' : [],
#             'Valley' : ['Valley Regional'],
#             'Winsor' : [],
#             # NOT ACTUALLY NEIRA:
#             'Exeter' : [],
#             'Middletown' : [],
#             'Suffield': []
#         }

def get_neira_schools():
    return set(School.objects.all())


def get_school(school_name, subset=None):
    pattern = re.compile("school", re.IGNORECASE)
    school_name = pattern.sub("", school_name)

    if subset is None:
        subset = get_neira_schools()

    scores = set([(None, 0)])
    for school in subset:
        score = compare(school.name, school_name)
        # for nick in school.alternate_names:
        #     newscore = compare(name, nick)
        #     if newscore > score:
        #         score = newscore
        scores.add((school, score))
    (school, score) = max(scores, key=(lambda (x, y): y))
    if score > 0.7:
        school.add_alternate_names([school_name])
        if alpha_only(school_name) != alpha_only(school.name):
            print school_name, "  is close enough to  ", school.name
            s = School()
            s.name = school_name
            s.save()
            s.merge_into(school)
            school = s
    else:
        print school_name, "  is unique <----------------------------------"
        school = School()
        school.name = school_name
        school.save()
    
    if subset is not None:
        subset.add(school)
        
    return school
    

def get_schools(school_list):
    return set(map(get_school, school_list))

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
def match_school(name, boatNum=None, subset=None):
    
    school = get_school(name, subset=subset)

    num = boatNum

    if boatNum is not None:
        if boatNum == 'novice':
            expectedNum = 0
        else:
            expectedNum = int(boatNum)

        # Check for the boat number. Ex: "Hopkins 4"
        if len(name.split(" ")) > 1:
            num_strings = name.replace("/", " ").split(" ")
            for numString in num_strings:
                try:
                    num = parse_num(numString)
                    break
                except ValueError:
                    pass

    return school, num


def parse_num(num):
    if 'nov' in num:
        return 0
    if len(num) == 1:
        return int(replace_letters(num))
    else:
        raise ValueError


def replace_letters(string):
    # n first for novice
    alpha = "nabcdefghijklmopqrstuvwxyz"
    low = string.lower()
    for letter in alpha:
        low = low.replace(letter, str(alpha.index(letter)))
    return low


def alpha_only(string):
    return filter((lambda s: str.isalnum(str(s)) and not str(s).isdigit()), string.lower())


def compare(school, name):
    return SequenceMatcher(None, alpha_only(school), alpha_only(name)).ratio()
