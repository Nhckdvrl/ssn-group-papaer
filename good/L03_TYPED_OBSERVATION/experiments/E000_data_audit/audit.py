#!/usr/bin/env python3
"""Standard-library ACS audit. All outputs confined to this experiment directory."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol.json"
NOTES = {
    "-666666666": ("-", "NOT_COMPUTABLE"),
    "-999999999": ("N", "NOT_DISPLAYABLE_INSUFFICIENT_CASES"),
    "-888888888": ("(X)", "NOT_APPLICABLE_OR_NOT_AVAILABLE"),
}
MOE_ONLY = {"-222222222", "-333333333", "-555555555"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def classify(estimate, annotation):
    """Reject unresolved pairs rather than deriving labels from intuition."""
    if estimate is None:
        if annotation is not None:
            raise ValueError("null estimate with annotation")
        return {"status": "NO_DATA_FOR_GEOGRAPHY", "value": None}
    if not isinstance(estimate, str):
        raise ValueError("estimate must be an API string or null")
    if estimate in NOTES:
        expected, status = NOTES[estimate]
        if annotation != expected:
            raise ValueError("sentinel/annotation disagreement")
        return {"status": status, "value": None}
    if estimate in MOE_ONLY:
        raise ValueError("margin-of-error sentinel in estimate field")
    if re.fullmatch(r"-([1-9])\1{8}", estimate):
        raise ValueError("unrecognized sentinel-shaped estimate; review required")
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", estimate):
        raise ValueError("not an ordinary decimal estimate")
    try:
        number = Decimal(estimate)
    except InvalidOperation as exc:
        raise ValueError("invalid numeric estimate") from exc
    if annotation is None:
        return {"status": "VALUE", "value": estimate}
    if isinstance(annotation, str) and re.fullmatch(r"\d[\d,]*(?:\.\d+)?[+-]", annotation):
        bound = annotation[:-1].replace(",", "")
        # Conservative: inconsistent numeric/annotation bounds require review.
        if Decimal(bound) != number:
            raise ValueError("numeric estimate differs from annotation bound")
        return {"status": "MEDIAN_LOWER_BOUND" if annotation[-1] == "+" else "MEDIAN_UPPER_BOUND",
                "value": None, "bound": bound}
    raise ValueError("unrecognized annotation")


def inventory(metadata, source):
    variables = metadata["variables"]
    pairs = sorted(v for v in variables if re.fullmatch(re.escape(source["group"]) + r"_.*E", v)
                   and v + "A" in variables)
    for v in source["estimates"]:
        if v not in pairs:
            raise ValueError("selected estimate lacks paired metadata: " + v)
        if variables[v].get("group") != source["group"]:
            raise ValueError("metadata group mismatch")
        expected = source.get("expected_labels", {}).get(v)
        if expected is not None and variables[v]["label"] != expected:
            raise ValueError("metadata semantic label changed: " + v)
    return {"group": source["group"], "paired_estimate_count": len(pairs), "pairs": pairs,
            "selected": {v: variables[v]["label"] for v in source["estimates"]}}


def extract(payload, source, metadata, source_hash):
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[0], list):
        raise ValueError("API response is not a populated rectangular table")
    header = payload[0]
    if len(set(header)) != len(header):
        raise ValueError("duplicate columns")
    required = {"NAME", "state", "county"}
    required.update(source["estimates"])
    required.update(v + "A" for v in source["estimates"])
    if not required.issubset(header):
        raise ValueError("missing required columns")
    records, unresolved, seen = [], [], set()
    for row in payload[1:]:
        if len(row) != len(header):
            raise ValueError("ragged API table")
        item = dict(zip(header, row))
        geo = item["state"] + item["county"]
        if not re.fullmatch(r"\d{5}", geo) or geo in seen:
            raise ValueError("invalid or duplicate county")
        seen.add(geo)
        for variable in source["estimates"]:
            record = {"id": source["dataset"] + ":" + geo + ":" + variable,
                      "dataset": source["dataset"], "group": source["group"],
                      "geography": geo, "name": item["NAME"], "variable": variable,
                      "label": metadata["variables"][variable]["label"],
                      "estimate": item[variable], "annotation": item[variable + "A"],
                      "source_sha256": source_hash}
            try:
                record["gold"] = classify(record["estimate"], record["annotation"])
                records.append(record)
            except ValueError as exc:
                record["reason"] = str(exc)
                unresolved.append(record)
    return records, unresolved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--replay", help="Replay a prior run ID with hash verification, no network")
    args = parser.parse_args()
    for name in (args.run_id, args.replay):
        if name is not None and not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            parser.error("run IDs may contain only letters, digits, underscores, hyphens")
    run = HERE / "runs" / args.run_id
    run.mkdir(parents=True, exist_ok=False)
    raw = run / "raw"
    raw.mkdir()
    prior = HERE / "runs" / args.replay if args.replay else None
    config_bytes = (prior / "protocol.json" if prior else PROTOCOL).read_bytes()
    config = json.loads(config_bytes)
    (run / "protocol.json").write_bytes(config_bytes)
    script_bytes = Path(__file__).read_bytes()
    (run / "audit.py").write_bytes(script_bytes)
    manifest = {"experiment": config["experiment_id"], "started_utc": datetime.now(timezone.utc).isoformat(),
                "python": platform.python_version(), "protocol_sha256": digest(config_bytes),
                "script_sha256": digest(script_bytes), "replay_of": args.replay, "requests": []}
    prior_entries = {}
    if prior:
        old = json.loads((prior / "manifest.json").read_text())
        if old["protocol_sha256"] != digest(config_bytes):
            raise ValueError("replay protocol changed")
        prior_entries = {r["file"]: r for r in old["requests"]}

    def acquire(url, filename, want_json=True):
        entry = {"url": url, "file": filename}
        manifest["requests"].append(entry)
        try:
            if prior:
                previous = prior_entries[filename]
                if "sha256" not in previous:
                    entry["error"] = previous.get("error", "ORIGINAL_ACQUISITION_FAILED")
                    return None
                body = (prior / "raw" / filename).read_bytes()
                if digest(body) != previous["sha256"]:
                    raise ValueError("cached response hash mismatch")
                entry["http_status"] = previous.get("http_status")
            else:
                request_url = url
                key = os.environ.get("CENSUS_API_KEY")
                if key and url.startswith("https://api.census.gov/") and "?" in url:
                    request_url += "&" + urllib.parse.urlencode({"key": key})
                with urllib.request.urlopen(request_url, timeout=30) as response:
                    body = response.read()
                    entry["http_status"] = response.status
            (raw / filename).write_bytes(body)
            entry.update(sha256=digest(body), bytes=len(body))
            if want_json:
                if b"<title>Missing Key</title>" in body:
                    entry["error"] = "API_KEY_REQUIRED_HTTP_200_HTML"
                    return None
                return json.loads(body)
            return body
        except Exception as exc:
            # Exception URLs may include credentials: never persist their text.
            entry["error"] = type(exc).__name__
            return None

    docs = acquire(config["documentation_url"], "official_notes.html", False)
    inventories, records, unresolved, errors = [], [], [], []
    for source in config["sources"]:
        base = "https://api.census.gov/data/" + source["dataset"]
        group = source["group"]
        meta = acquire(base + "/groups/" + group + ".json", group + "_metadata.json")
        try:
            if meta is None:
                raise ValueError("metadata unavailable")
            inventories.append(inventory(meta, source))
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"group": group, "stage": "metadata", "reason": str(exc)})
            continue
        fields = ["NAME"] + [x for v in source["estimates"] for x in (v, v + "A")]
        url = base + "?" + urllib.parse.urlencode({"get": ",".join(fields), "for": config["geography"]})
        data = acquire(url, group + "_observations.json")
        if data is None:
            errors.append({"group": group, "stage": "observations", "reason": "see request manifest"})
            continue
        try:
            rows, rejected = extract(data, source, meta, manifest["requests"][-1]["sha256"])
            records.extend(rows)
            unresolved.extend(rejected)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"group": group, "stage": "extract", "reason": str(exc)})
    counts = Counter(r["gold"]["status"] for r in records)
    strata = {}
    for r in records:
        status = r["gold"]["status"]
        if status == "VALUE":
            status = "VALUE_ZERO" if Decimal(r["gold"]["value"]) == 0 else "VALUE_NONZERO"
        strata.setdefault(status, []).append(r["geography"])
    coverage = {s: {"cells": len(geos), "counties": len(set(geos))} for s, geos in sorted(strata.items())}
    enough = all(coverage.get(s, {}).get("cells", 0) >= config["minimum_cells_per_required_stratum"]
                 and coverage.get(s, {}).get("counties", 0) >= config["minimum_counties_per_required_stratum"]
                 for s in config["required_strata"])
    complete = not errors and docs is not None and not any("error" in r for r in manifest["requests"])
    status = "BLOCKED_ACQUISITION_OR_SCHEMA" if not complete else (
        "REVIEW_UNKNOWN_PAIRS" if unresolved else "COUNTS_READY_FOR_MANUAL_AUDIT" if enough else "INSUFFICIENT_COVERAGE")
    report = {"status": status, "complete": complete, "model_calls": 0,
              "valid_cells_observed": len(records), "unresolved_cells": len(unresolved),
              "status_counts_observed": dict(sorted(counts.items())), "coverage_observed": coverage,
              "errors": errors, "interpretation": "Counts refer only to successfully acquired selected cells; absent data are not zero population prevalence. No model or paper claim is established."}
    for filename, obj in [("manifest.json", manifest), ("inventory.json", inventories), ("report.json", report), ("unresolved.json", unresolved)]:
        dump(run / filename, obj)
    with (run / "observations.jsonl").open("w", encoding="utf-8") as stream:
        for record in sorted(records, key=lambda r: r["id"]):
            stream.write(json.dumps(record, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if status == "COUNTS_READY_FOR_MANUAL_AUDIT" else 2


if __name__ == "__main__":
    sys.exit(main())
