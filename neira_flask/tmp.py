import json

uid = "95FD106DFDCEC13E4123EEAA631894B9"

with open(f"data/0_raw/{uid}-raw.json", "r") as f:
  data = json.load(f)
breakpoint()
with open(f"row2k-backup/{uid}.html", "w") as f:
  f.write(data["html"])
