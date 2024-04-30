import json
import os
import tempfile

import click
import editor


import hashlib


@click.command
@click.argument("data_dir")
def review(data_dir):
    with open("corrections.json", "r") as f:
        corrections = json.load(f)

    print("corrections.json")

    for filename in sorted(os.listdir(data_dir)):
        uid = os.path.splitext(os.path.basename(filename))[0]

        if uid in corrections:
            if corrections[uid]["checksum"] == "...":
                with open(os.path.join(data_dir, filename)) as f:
                    corrections[uid]["checksum"] = hashlib.md5(
                        f.read().encode()
                    ).hexdigest()

            with open("corrections.json", "w") as f:
                json.dump(corrections, f, sort_keys=True, indent=4)

            continue

        with open(os.path.join(data_dir, filename)) as f:
            file_contents = f.read()
            race_object = json.loads(file_contents)
            checksum = hashlib.md5(file_contents.encode()).hexdigest()

        print(race_object["regatta_display_name"])
        print(race_object["url"])
        print(os.path.join(data_dir, filename))

        input("Press Enter to edit corrections...")

        with open("corrections.json", "r") as f:
            corrections = json.load(f)

        contents = b"[]"
        while True:
            contents = editor.edit(contents=contents)
            try:
                corrections[uid] = {
                    "corrections": json.loads(contents.decode()),
                    "checksum": checksum,
                }
                break
            except json.JSONDecodeError:
                if contents.decode().strip() == "exit":
                    return
                contents = b"# Not valid json, please try again\n" + contents
                pass  # Try again

        # Check validity of json
        json.dumps(corrections)

        with open("corrections.json", "w") as f:
            json.dump(corrections, f, sort_keys=True, indent=4)

        input("Press Enter to continue...")
        print()


if __name__ == "__main__":
    review()
