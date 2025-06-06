import json
import os.path
import shutil
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from neira.data_provider.data_provider import parse_distance

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DOT_DIRECTORY = os.path.join(PROJECT_ROOT, "dot-2024")
CSS_DIRECTORY = os.path.join(os.path.dirname(__file__), "css")
CONTENT_DIRECTORY = os.path.join(os.path.dirname(__file__), "content")
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "output")
# YEAR_ROOT = os.path.join(OUTPUT_DIRECTORY, "2025")

def main():
    build()

# def compute_boatlengths(margin, t1, t2, distance, class_):
#     match class_:
#         case "fours":
#             boat_length = 13.4
#         case "eights":
#             boat_length = 18.9
#         case _:
#             raise Exception("Unhandled class_: " + repr(class_))
#     boat_speed


def build():
    base = "/neira"
    # base = ""
    current_year = 2025
    # with open(os.path.join(CONTENT_DIRECTORY, "index.jinja")) as f:
    #     template = f.read()
    shutil.rmtree(OUTPUT_DIRECTORY)
    os.makedirs(OUTPUT_DIRECTORY)
    env = Environment(loader=FileSystemLoader(CONTENT_DIRECTORY))
    with open(os.path.join(OUTPUT_DIRECTORY, "index.html"), "w") as f:
        # Redirect to current year
        f.write(f"""<html><meta http-equiv="Refresh" content="0; url='{base}/{current_year}'" /></html>""")

    shutil.copyfile(os.path.join(CSS_DIRECTORY, "w3.css"), os.path.join(OUTPUT_DIRECTORY, "w3.css"))
    shutil.copyfile(os.path.join(CSS_DIRECTORY, "raleway.css"), os.path.join(OUTPUT_DIRECTORY, "raleway.css"))
    shutil.copyfile(os.path.join(CSS_DIRECTORY, "font-awesome.min.css"), os.path.join(OUTPUT_DIRECTORY, "font-awesome.min.css"))

    years = {
        "2024": {
            "template": 'index.jinja2',
            "reviewed_data": "/Users/dailis/neira/data-2024/2_reviewed",
            "dot": DOT_DIRECTORY,
        },
        "2025": {
            "template": 'index.jinja2',
            "reviewed_data": "/Users/dailis/neira/data/2_reviewed",
            "dot": None
        },
    }

    for year, config in years.items():
        YEAR_ROOT = os.path.join(OUTPUT_DIRECTORY, year)
        os.makedirs(YEAR_ROOT)

        template = env.get_template(config["template"])
        output = template.render({"base": base, "year": year})

        with open(os.path.join(YEAR_ROOT, "index.html"), "w") as f:
            f.write(output)

        if config["dot"]:
            shutil.copytree(DOT_DIRECTORY, os.path.join(YEAR_ROOT, "dot"))

        heats = {}
        for class_ in ("fours", "eights"):
            heats[class_] = {}
            for gender in ("boys", "girls"):
                heats[class_][gender] = {}
                for varsity_index in (1, 2, 3, 4, 5, 6):
                    heats[class_][gender][varsity_index] = {}
        if config["reviewed_data"]:
            regatta_template = env.get_template('regatta.jinja2')
            for file in os.listdir(config["reviewed_data"]):
                basename = os.path.splitext(os.path.basename(file))[0]
                with open(os.path.join(config["reviewed_data"], file), "r") as f, open(os.path.join(YEAR_ROOT, basename + ".html"), "w") as g:
                    contents = json.load(f)
                    date = contents["day"]
                    distance = parse_distance(contents["comment"])
                    for heat in contents["heats"]:
                        entry = heats[heat["class"]][heat["gender"]][int(heat["varsity_index"])]
                        if date not in entry:
                            entry[date] = []
                        entry[date].append([dict(x, url=contents["url"], distance=distance) for x in heat["results"]])
                    g.write(regatta_template.render(contents))

        for class_ in heats:
            for gender in heats[class_]:
                for varsity_index in heats[class_][gender]:
                    old_entry = heats[class_][gender][varsity_index]
                    new_entry = []
                    included_founders = False
                    for date, results in sorted(old_entry.items(), key=lambda x: x[0], reverse=True):
                        parsed_date = datetime.strptime(date, "%Y-%m-%d")
                        if class_ == "fours" and date == "2025-05-04":
                            results.insert(0, "founders-day")
                            included_founders = True
                        new_entry.append({
                            "date": parsed_date.strftime("%A, %B {}, %Y").format(parsed_date.day), # Day without leading zero
                            "date-yyyy-mm-dd": date,
                            "results": results
                        })
                    if class_ == "fours" and not included_founders:
                        parsed_date = datetime.strptime("2025-05-04", "%Y-%m-%d")
                        new_entry.append({
                            "date": parsed_date.strftime("%A, %B {}, %Y").format(parsed_date.day), # Day without leading zero
                            "date-yyyy-mm-dd": "2025-05-04",
                            "results": "founders-day"
                        })
                        new_entry.sort(key=lambda x: x["date-yyyy-mm-dd"], reverse=True)
                    heats[class_][gender][varsity_index] = new_entry

        template = env.get_template("category-index.jinja2")
        for class_ in ("fours", "eights"):
            os.makedirs(os.path.join(YEAR_ROOT, class_))
            for gender in ("boys", "girls"):
                os.makedirs(os.path.join(YEAR_ROOT, class_, gender))
                for varsity_index in (1, 2, 3, 4):
                    os.makedirs(os.path.join(YEAR_ROOT, class_, gender, str(varsity_index)))
                    with open(os.path.join(YEAR_ROOT, class_, gender, str(varsity_index), "index.html"), "w") as f:
                        f.write(template.render(
                            base=base,
                            year=year,
                            class_=class_,
                            gender=gender,
                            varsity_index=varsity_index,
                            results=heats[class_][gender][varsity_index]
                        ))

    with open("/Users/dailis/neira/founders-day.json", "r") as f:
        founders_day_data = json.load(f)
        # TODO I removed Taft (B) from B4H1 and Brewster from B3H1

    template = env.get_template("founders-day.jinja2")
    with open(os.path.join(YEAR_ROOT, "founders-day.html"), "w") as f:
        f.write(template.render(
            base=base,
            year=year,
            founders_day_data=founders_day_data,
        ))

if __name__ == "__main__":
    main()


"""
Site structure:

Landing page is neira/2025
Links to:
- Weekly blog posts
- Drill down to -> fours/eights, --> boys/girls --> 1,2,3,4
- List of participating schools
- Seeding tool (separate project...?)


"""