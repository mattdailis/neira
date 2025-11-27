import hashlib
import json


def get_checksum_version():
    return 4


def compute_checksum(regatta):
    regatta = dict(regatta)  # Make copy so we can mutate it to remove some keys
    if "status" in regatta:
        del regatta["status"]

    if "day" in regatta:
        del regatta["day"]

    regatta["comment"] = regatta["comment"].strip()

    regatta_json = json.dumps(regatta, sort_keys=True, indent=4)
    return get_checksum_version(), hashlib.md5(regatta_json.encode()).hexdigest()
