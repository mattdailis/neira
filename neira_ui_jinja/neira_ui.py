import json
import os.path
import shutil
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DOT_DIRECTORY = os.path.join(PROJECT_ROOT, "dot-2024")
CSS_DIRECTORY = os.path.join(os.path.dirname(__file__), "css")
CONTENT_DIRECTORY = os.path.join(os.path.dirname(__file__), "content")
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "output")
# YEAR_ROOT = os.path.join(OUTPUT_DIRECTORY, "2025")

def main():
    build()

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
                    for heat in contents["heats"]:
                        entry = heats[heat["class"]][heat["gender"]][int(heat["varsity_index"])]
                        if date not in entry:
                            entry[date] = []
                        entry[date].append([dict(x, url=contents["url"]) for x in heat["results"]])
                    g.write(regatta_template.render(contents))

        for class_ in heats:
            for gender in heats[class_]:
                for varsity_index in heats[class_][gender]:
                    old_entry = heats[class_][gender][varsity_index]
                    new_entry = []
                    for date, results in sorted(old_entry.items(), key=lambda x: x[0], reverse=True):
                        parsed_date = datetime.strptime(date, "%Y-%m-%d")
                        new_entry.append({
                            "date": parsed_date.strftime("%A, %B {}, %Y").format(parsed_date.day), # Day without leading zero
                            "results": results
                        })
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