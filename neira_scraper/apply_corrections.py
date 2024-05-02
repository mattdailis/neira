import json
import os
import click


@click.command()
@click.argument("corrections_file")
@click.argument("input_dir")
@click.argument("output_dir")
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
            elif correction["type"] == "comment":
                pass
            else:
                raise Exception("Unhandled correction type: " + correction["type"])

        for heat in race_object["heats"]:
            if heat["gender"] not in ("boys", "girls"):
                raise Exception("Unrecognized gender: " + heat["gender"])
        with open(os.path.join(output_dir, uid + ".json"), "w") as f:
            json.dump(race_object, f, sort_keys=True, indent=4)


if __name__ == "__main__":
    apply_corrections()
