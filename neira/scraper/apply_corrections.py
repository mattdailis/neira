import json
import os


def apply_corrections(corrections_file, input_dir, output_dir):
    with open(corrections_file, "r") as f:
        all_corrections = json.load(f)
    for uid, corrections in all_corrections.items():
        with open(os.path.join(input_dir, uid + ".json"), "r") as f:
            race_object = json.load(f)
        print(uid, corrections)
        for correction in corrections["corrections"]:
            if correction["type"] == "ignore_heats":
                ignore_heats(race_object, correction)
            elif correction["type"] == "set_gender_all_heats":
                for heat in race_object["heats"]:
                    heat["gender"] = correction["gender"]
            elif correction["type"] == "set_class_all_heats":
                for heat in race_object["heats"]:
                    heat["class"] = correction["class"]
            elif correction["type"] == "exclude_schools_from_heat":
                exclude_schools_from_heat(race_object, correction)
            elif correction["type"] == "rename_heat":
                gender, varsity_index = correction["from"].split()
                new_gender, new_varsity_index = correction["to"].split()
                for heat in race_object["heats"]:
                    if (
                        heat["gender"] == gender
                        and heat["varsity_index"] == varsity_index
                    ):
                        heat["gender"] = new_gender
                        heat["varsity_index"] = new_varsity_index
            elif correction["type"] == "set_margins":
                set_margins(race_object, correction)
            elif correction["type"] == "comment":
                pass
            else:
                raise Exception("Unhandled correction type: " + correction["type"])

        for heat in race_object["heats"]:
            if heat["gender"] not in ("boys", "girls"):
                raise Exception("Unrecognized gender: " + str(heat["gender"]))
            if heat["class"] not in ("eights", "fours"):
                raise Exception("Unrecognized boat class: " + str(heat["class"]))
        with open(os.path.join(output_dir, uid + ".json"), "w") as f:
            json.dump(race_object, f, sort_keys=True, indent=4)


def ignore_heats(race_object, correction):
    for entry in correction["heats"]:
        gender, varsity_index = entry.split()
        for i, heat in enumerate(race_object["heats"]):
            if heat["gender"] == gender and heat["varsity_index"] == varsity_index:
                break
        else:
            raise Exception("No heat matched " + entry)
        del race_object["heats"][i]


def exclude_schools_from_heat(race_object, correction):
    entry = correction["heat"]
    gender, varsity_index = entry.split()
    for heat in race_object["heats"]:
        if heat["gender"] == gender and heat["varsity_index"] == varsity_index:
            results = []
            for result in heat["results"]:
                if result["school"] not in correction["schools"]:
                    results.append(result)
            heat["results"] = results
            break
    else:
        raise Exception("No heat matched " + entry)


def set_margins(race_object, correction):
    entry = correction["heat"]
    gender, varsity_index = entry.split()
    for heat in race_object["heats"]:
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


if __name__ == "__main__":
    apply_corrections()
