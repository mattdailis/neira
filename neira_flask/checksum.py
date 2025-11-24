import hashlib
import json


def get_checksum_version():
    return 3


def compute_checksum(regatta):
    regatta_json = json.dumps(regatta, sort_keys=True, indent=4)
    return get_checksum_version(), hashlib.md5(regatta_json.encode()).hexdigest()
