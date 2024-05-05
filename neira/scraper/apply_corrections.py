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
                for entry in correction["heats"]:
                    gender, varsity_index = entry.split()
                    for i, heat in enumerate(race_object["heats"]):
                        if (
                            heat["gender"] == gender
                            and heat["varsity_index"] == varsity_index
                        ):
                            break
                    else:
                        raise Exception("No heat matched " + entry + " in " + uid)
                    del race_object["heats"][i]
            elif correction["type"] == "set_gender_all_heats":
                for heat in race_object["heats"]:
                    heat["gender"] = correction["gender"]
            elif correction["type"] == "set_class_all_heats":
                for heat in race_object["heats"]:
                    heat["class"] = correction["class"]
            elif correction["type"] == "exclude_schools_from_heat":
                entry = correction["heat"]
                gender, varsity_index = entry.split()
                for i, heat in enumerate(race_object["heats"]):
                    if (
                        heat["gender"] == gender
                        and heat["varsity_index"] == varsity_index
                    ):
                        results = []
                        for result in heat["results"]:
                            if result["school"] not in correction["schools"]:
                                results.append(result)
                        heat["results"] = results
                        break
                else:
                    raise Exception("No heat matched " + entry + " in " + uid)
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


if __name__ == "__main__":
    apply_corrections()
