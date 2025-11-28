from neira_flask import db


def apply_corrections():
    with db.get_cursor(cursor=None) as cursor:
        scrape_id = db.get_scrape_id(cursor=cursor)
        
        all_corrections = db.get_corrections(cursor=cursor)
        for uid, corrections in all_corrections.items():
            parent_regatta_id, regatta = db.get_regatta(uid, status="2_cleaned", cursor=cursor)
            print(uid, corrections)
            if regatta is None:
                print("Could not apply corrections to " + uid)
                continue
            apply_corrections_single(regatta, corrections["corrections"])
            for heat in regatta["heats"]:
                if heat["gender"] not in ("boys", "girls"):
                    raise Exception("Unrecognized gender: " + str(heat["gender"]))
                if heat["class"] not in ("eights", "fours"):
                    raise Exception("Unrecognized boat class: " + str(heat["class"]))
            db.write_regatta(uid, regatta, status="3_reviewed", scrape_id=scrape_id, parent_id=parent_regatta_id, producer="apply_corrections", correction_id=corrections["correction_id"], cursor=cursor)


def ignore_heats(regatta, correction):
    for entry in correction["heats"]:
        gender, varsity_index = entry.split()
        for i, heat in enumerate(regatta["heats"]):
            if heat["gender"] == gender and heat["varsity_index"] == varsity_index:
                break
        else:
            raise Exception("No heat matched " + entry)
        del regatta["heats"][i]


def exclude_schools_from_heat(regatta, correction):
    entry = correction["heat"]
    gender, varsity_index = entry.split()
    for heat in regatta["heats"]:
        if heat["gender"] == gender and heat["varsity_index"] == varsity_index:
            results = []
            for result in heat["results"]:
                if result["school"] not in correction["schools"]:
                    results.append(result)
            heat["results"] = results
            break
    else:
        raise Exception("No heat matched " + entry)


def set_margins(regatta, correction):
    entry = correction["heat"]
    gender, varsity_index = entry.split()
    for heat in regatta["heats"]:
        if heat["gender"] == gender and heat["varsity_index"] == varsity_index:
            if len(heat["results"]) != len(correction["margins"]):
                raise Exception(
                    "Length mismatch between "
                    + heat["results"]
                    + " and "
                    + correction["margins"]
                )
            for result, new_margins in zip(heat["results"], correction["margins"]):
                if result["school"] != new_margins["school"]:
                    raise Exception(
                        "School mismatch: "
                        + result["school"]
                        + " != "
                        + new_margins["school"]
                    )
                result["margin_from_winner"] = new_margins["margin_from_winner"]
            break
    else:
        raise Exception("No heat matched " + entry)


def apply_corrections_single(regatta, corrections):
    for correction in corrections:
        if correction["type"] == "comment":
            pass
        elif correction["type"] == "ignore_heats":
            ignore_heats(regatta, correction)
        elif correction["type"] == "exclude_schools_from_heat":
            exclude_schools_from_heat(regatta, correction)
        elif correction["type"] == "rename_heat":
            gender, varsity_index = correction["from"].split()
            new_gender, new_varsity_index = correction["to"].split()
            for heat in regatta["heats"]:
                if (
                    heat["gender"] == gender
                    and heat["varsity_index"] == varsity_index
                ):
                    heat["gender"] = new_gender
                    heat["varsity_index"] = new_varsity_index
        elif correction["type"] == "set_class_all_heats":
            for heat in regatta["heats"]:
                heat["class"] = correction["class"]
        elif correction["type"] == "set_gender_all_heats":
            for heat in regatta["heats"]:
                heat["gender"] = correction["gender"]
        elif correction["type"] == "set_margins":
            set_margins(regatta, correction)
        elif correction["type"] == "set_varsity_index":
            regatta["heats"][correction["heat_index"]]["varsity_index"] = (
                correction["varsity_index"]
            )
        elif correction["type"] == "manual_override":
            regatta = correction["new_contents"]
        else:
            raise Exception("Unhandled correction type: " + correction["type"])

    for heat in regatta["heats"]:
        if heat["gender"] not in ("boys", "girls"):
            raise Exception("Unrecognized gender: " + str(heat["gender"]))
        if heat["class"] not in ("eights", "fours"):
            raise Exception("Unrecognized boat class: " + str(heat["class"]))


if __name__ == "__main__":
    apply_corrections()
