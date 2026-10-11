"""Merge sharded generation JSONL files back into one cell file, in global index order."""
import json, os, sys

def main(out, parts):
    header, rows = None, []
    for p in parts:
        recs = [json.loads(l) for l in open(p, encoding="utf-8")]
        h, body = recs[0], recs[1:]
        if header is None:
            header = dict(h)
            header["n"] = h.get("n_total", h["n"])
            header["merged_from"] = [os.path.basename(x) for x in parts]
            header["wall_seconds_max_shard"] = h["wall_seconds"]
        header["wall_seconds_max_shard"] = max(header["wall_seconds_max_shard"], h["wall_seconds"])
        rows.extend(body)
    rows.sort(key=lambda r: r["idx"])
    assert [r["idx"] for r in rows] == list(range(len(rows))), "shard coverage is not complete"
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"merged {len(parts)} shards -> {out} ({len(rows)} rows)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
