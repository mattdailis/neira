![](https://github.com/mattdailis/neira/blob/28a5e4077755117a01b9d18e1101e82c54cf05dc/remo-rowing.gif)

# neira
http://mattdailis.github.io/neira/

This is a project to help coaches and rowers keep track of how their school is doing compared to other schools in the NEIRA conference.

# Prerequisites
- python >= 3.8
- npm (recommend using nvm to install)

# Installation process
1. Make a virtualenv
2. In that environment, pip install -e .
3. cd neira_ui
4. npm install

# Updating data
Data is updated following this process:
1. Download data from row2k. This saves data in a local `data/0_raw` directory
2. Read from the `data/0_raw` directory and apply an automated cleaning process. This matches the schools in the data with known schools in NEIRA, and determines genders and classes if it can.
3. Guide a human reviewer through reviewing and correcting the cleaned data. This is an interactive process run by the `review.py` script.
4. Apply the corrections to `data/1_cleaned`, and produce data in `data/2_reviewed`.
5. Run any analyses that depend on this data, and save their output to `neira_ui/static`, where it can be included in the website.

Here are the commands needed for the above process. See the Corrections documentation for help with the review process.

```bash
neira scrape data/1_cleaned --raw-cache=data/0_raw
neira review data/1_cleaned 
neira apply-corrections corrections.json data/1_cleaned data/2_reviewed

python neira/dot/read.py data/2_reviewed neira_ui/static/dot

cd neira_ui
npm run build
cd ..
rm -rf docs
mv ./neira_ui/build docs

git commit
git push
```

# Corrections
In order to ensure the validity of the data prior to running any analyses, there is a manual review step after the
automated cleaning process is complete. Corrections are made by adding an entry to `corrections.json`, where the key
is the uid of the race (found in the url of the race on row2k), and the value includes a `corrections` list, as well
as a `checksum` to be used to determine whether any races need to be re-reviewed due to upstream changes.

The `corrections` list contains a list of json objects, each of which has a `type` member. The value of `type` determines what other members are expected.

## "type": "comment"

This "correction" does not make any changes, but gives a space for the reviewer to add notes for themselves.

Example:
```json
{
    "type": "comment",
    "comment": "This race seems strange, I'd like to come back and look at it more closely"
}
```

## "type": "set_class_all_heats"

Overrides the `class` attribute on every heat with whatever the reviewer specifies. Useful for races where the automated cleaner could not determine whether the race included fours or eights.

Example:
```json
{
    "type": "set_class_all_heats",
    "class": "fours"
}
```

## "type": "set_gender_all_heats"

Overrides the `gender` attribute on every heat with whatever the reviewer specifies. Useful for races where the automated cleaner could not determine whether the race included boys or girls teams.

Example:
```json
{
    "type": "set_gender_all_heats",
    "class": "girls"
}
```

## "type": "ignore_heats"

Sometimes, heats are included in a race, but include only novice boats, or are mentioned in the race's comment as not valid for seeding. This correction allows those heats to be removed from the data. Note that the correction will fail to be applied if the heat does not exist. Heats are specified by mentioning a gender and a varsity index.

Example:
```json
{
    "type": "ignore_heats",
    "heats": ["girls 4", "boys 3"]
}
```

# Hosting
This website is hosted on GitHub Pages. GitHub Pages allows for two options for hosting: dedicate a branch to be the hosted branch, or host from the `docs` folder of your main branch. This website is hosted from the `docs` folder.

# Architecture
- `neira/scrape`: a python package responsible for downloading data from row2k and cleaning it
- `neira/dot`: python program that generates graphviz visualizations based on downloaded data
- `neira_ui`: user interface code, using svelte framework

# Glossary
- **varsity index**: A number from 1 to 6, referring to a school's "first boat" through "sixth boat".
- **gender**: Either `boys` or `girls`
- **class**: Either `eights` or `fours`
- **boat**: A combination of *school*, *gender*, *varsity index* and *class*. For example: `Groton Girls Second Four`, or `("fours", "girls", "2", "Groton")`
- **race**: A page on row2k. A race may contain multiple heats
- **heat**: A set of boats that competed simultaneously
- **head-to-head**: A term for comparing boats by using their performance relative to each other in the same heat
