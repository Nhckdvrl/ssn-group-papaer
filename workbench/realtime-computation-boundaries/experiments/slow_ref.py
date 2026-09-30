"""Slow-only reference on FDB-v3: the same backend (and tools/prompt) as the driver, given the human reference
transcript directly (no fast model). Output uses the driver's schema so score_fdb.py can score it."""
import json, sys
from pathlib import Path
from openai import OpenAI
sys.argv += [] 
from venus_fdb_driver import run_slow, FDB
client = OpenAI(base_url="http://localhost:8100/v1", api_key="x")
out = []
for e in sorted(x for x in (FDB / "fdb_v3_data_released").iterdir() if x.is_dir()):
    meta = json.load(open(e / "metadata.json"))
    tr = " ".join(t["user"] for t in meta["dialogue"])
    res, calls = run_slow(client, "Qwen/Qwen3-32B", "", tr, "transcript")
    out.append(dict(id=e.name, meta=meta, delegates=[{"objective": "(transcript)"}], actual_tool_calls=calls,
                    spoken_after_backend=res))
json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
print(len(out))
