import csv
import io
import re

from validation import valid_node_id

REQUIRED_FIELDS = ("node_id", "name", "site", "machine_class")


def auto_node_id(name, site):
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", "%s-%s" % (site, name)).strip("-").lower()
    return slug[:64] or "vs-node"


def parse_csv(text):
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("missing CSV header")
    missing = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
    if missing:
        raise ValueError("missing fields: " + ",".join(missing))
    rows = []
    seen = set()
    for row in reader:
        item = {field: (row.get(field) or "").strip() for field in REQUIRED_FIELDS}
        if not item["node_id"]:
            item["node_id"] = auto_node_id(item["name"], item["site"])
        if not valid_node_id(item["node_id"]):
            raise ValueError("invalid node id: " + item["node_id"])
        if item["node_id"] in seen:
            raise ValueError("duplicate node id: " + item["node_id"])
        seen.add(item["node_id"])
        rows.append(item)
    return rows


def hierarchy(rows):
    result = {}
    for row in rows:
        site = result.setdefault(row["site"], {})
        machine_class = site.setdefault(row["machine_class"], [])
        machine_class.append(row["node_id"])
    return result


def qr_payload(node_id):
    if not valid_node_id(node_id):
        raise ValueError("invalid node id")
    return "vs://node/" + node_id
