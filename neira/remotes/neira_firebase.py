import json
import os
from firebase import firebase as fb


def main():
    firebase_config = {
        "apiKey": "AIzaSyC4wR7v4I0iMKzy_h_BjQ-RGgJrJV7knsc",
        "authDomain": "neira-f9621.firebaseapp.com",
        "databaseURL": "https://neira-f9621.firebaseio.com",
        "projectId": "neira-f9621",
        "storageBucket": "neira-f9621.appspot.com",
        "messagingSenderId": "107972862685",
        "appId": "1:107972862685:web:58b89d4c93648c3bc63134",
    }

    firebase = fb.FirebaseApplication(firebase_config["databaseURL"], None)

    data_dir = "data/2_reviewed"
    for filename in os.listdir(data_dir):
        uid = os.path.splitext(filename)[-2]
        with open(os.path.join(data_dir, filename), "r") as f:
            contents = json.load(f)
        result = firebase.put("/races", uid, contents)
        print(result)

    with open("founders-day-head-to-head.json", "r") as f:
        contents = json.load(f)
    result = firebase.put("/founders-day", "2025", contents)


if __name__ == "__main__":
    main()
