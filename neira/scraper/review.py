import json
import os

import editor

import hashlib


def review(data_dir):
    with open("corrections.json", "r") as f:
        corrections = json.load(f)

    print("Corrections are saved in corrections.json")

    filenames = sorted(os.listdir(data_dir))

    to_review = []
    for i, filename in enumerate(filenames):
        uid = os.path.splitext(os.path.basename(filename))[0]

        if uid in corrections:
            with open(os.path.join(data_dir, filename)) as f:
                new_checksum = hashlib.md5(f.read().encode()).hexdigest()

            if corrections[uid]["checksum"] == new_checksum:
                continue
            else:
                to_review.append(
                    (filename, (uid + " has changed since it was last reviewed"))
                )
        else:
            to_review.append((filename, (uid + " has not been reviewed")))

    for i, (filename, message) in enumerate(to_review):
        print(str(len(to_review) - i) + " to go...")

        print(message)
        uid = os.path.splitext(os.path.basename(filename))[0]

        # if uid in corrections:
        #     with open(os.path.join(data_dir, filename)) as f:
        #         new_checksum = hashlib.md5(f.read().encode()).hexdigest()

        #     if corrections[uid]["checksum"] == new_checksum:
        #         continue
        #     else:
        #         print(uid + " has changed since it was last reviewed")
        # else:
        #     print(uid + " has not been reviewed")

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

        contents = (
            json.dumps(corrections[uid]["corrections"], indent=4).encode()
            if uid in corrections
            else b"[]"
        )

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
