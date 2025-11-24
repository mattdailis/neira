import json

import editor

from neira_flask import db
from neira_flask.checksum import compute_checksum


def review():
    corrections = db.get_corrections()
    # filenames = sorted(os.listdir(data_dir))
    uids = sorted(db.get_regatta_uids(2025))

    to_review = []

    regattas = {}

    for i, uid in enumerate(uids):
        if uid in corrections:
            parent_regatta_id, regatta = db.get_regatta(uid, status="2_cleaned")
            regattas[uid] = parent_regatta_id, regatta
            if regatta is None:
                continue
            checksum_version, new_checksum = compute_checksum(regatta)

            if corrections[uid]["checksum"] == new_checksum:
                continue
            else:
                to_review.append(
                    (uid, (uid + " has changed since it was last reviewed"))
                )
        else:
            to_review.append((uid, (uid + " has not been reviewed")))

    if len(to_review) == 0:
        print("Everything has already been reviewed 🚀")
    
    for i, (uid, message) in enumerate(to_review):
        print(str(len(to_review) - i) + " to go...")
        print(message)

        parent_regatta_id, regatta = regattas[uid] # db.get_regatta(uid, status="2_cleaned")  # TODO we've already queried this above, could cache

        print(regatta["name"])
        print(regatta["url"])

        with open("review-sandbox/tmp.json", "w") as f:
            f.write(json.dumps(regatta, sort_keys=True, indent=4))
        print("review-sandbox/tmp.json")

        input("Press Enter to edit corrections...")

        corrections = db.get_corrections()

        contents = (
            json.dumps(corrections[uid]["corrections"], indent=4).encode()
            if uid in corrections
            else b"[]"
        )

        should_skip = False
        while True:
            contents = editor.edit(contents=contents)
            try:
                corrections[uid] = {
                    "corrections": json.loads(contents.decode()),
                    "checksum": new_checksum,
                }
                break
            except json.JSONDecodeError:
                if contents.decode().strip() == "exit":
                    return
                if contents.decode().strip() == "skip":
                    should_skip = True
                    break
                contents = b"# Not valid json, please try again\n" + contents
                pass  # Try again

        if not should_skip:    
            # Check validity of json
            json.dumps(corrections)

            # with open("corrections.json", "w") as f:
            #     json.dump(corrections, f, sort_keys=True, indent=4)
            db.update_correction(uid, corrections[uid]["corrections"], new_checksum)

        input("Press Enter to continue...")
        print()


if __name__ == "__main__":
    review()
