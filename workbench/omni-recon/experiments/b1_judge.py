"""Label B1 trials: what did the model do with a mid-stream correction? Qwen3-32B on port 8100.
usage: b1_judge.py <run.json> [...]  -> <run>.judged.json + a cond x label table"""
import json
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI

ITEMS = {x["id"]: x for x in json.load(open(__file__.rsplit("/", 2)[0] + "/probes/update.json"))}
LABELS = ["ADAPT", "ACK_ONLY", "CONTINUE", "STOP", "CONFUSED"]
PROMPT = """A spoken assistant was answering this request: "{q}" (topic: {old}).
While it was talking (or right after the request), the user said: "{c}" (new topic: {new}).
What the assistant had said BEFORE the correction: "{before}"
What the assistant said AFTER the correction started: "{after}"
Label the assistant's handling of the correction:
- ADAPT: after the correction it gives content about the new topic ({new})
- ACK_ONLY: acknowledges the correction but gives no real content about the new topic
- CONTINUE: keeps talking about the old topic ({old}) as if the correction had not happened
- STOP: says nothing meaningful after the correction (empty or a fragment)
- CONFUSED: mixes the topics incorrectly, e.g. attributes old-topic facts to the new topic
Output exactly one label on the last line."""


def label(c, r):
    it = ITEMS[r["id"]]
    if r["cstart"] is None:
        return "NO_TRIAL"
    if not r["after"].strip():
        return "STOP"
    out = c.chat.completions.create(model="Qwen/Qwen3-32B", temperature=0.0, max_tokens=12, messages=[
        {"role": "user", "content": PROMPT.format(q=it["q"], old=it["old"], c=it["corr"], new=it["new"],
                                                  before=r["before"][:500], after=r["after"][:700])}],
        extra_body={"chat_template_kwargs": {"enable_thinking": False}}).choices[0].message.content or ""
    last = (out.strip().upper().splitlines() or [""])[-1]
    return next((L for L in LABELS if L in last), "CONFUSED")


def main():
    c = OpenAI(base_url="http://localhost:8100/v1", api_key="x")
    for p in sys.argv[1:]:
        rows = json.load(open(p))
        todo = [r for r in rows if r["cond"] != "none"]
        with ThreadPoolExecutor(24) as ex:
            for r, lab in zip(todo, ex.map(lambda r: label(c, r), todo)):
                r["label"] = lab
        json.dump(rows, open(p.replace(".json", ".judged.json"), "w"), indent=1, ensure_ascii=False)
        tab = defaultdict(Counter)
        for r in todo:
            tab[r["cond"]][r["label"]] += 1
        none = [r for r in rows if r["cond"] == "none"]
        print(p.rsplit("/", 1)[-1], "| natural response length (chunks after onset):",
              sorted(sum(1 for t in r["timeline"][r["onset"]:] if t) for r in none if r["onset"] is not None))
        for cond in ["pre", "on1", "on3", "on6"]:
            n = sum(tab[cond].values())
            print(f"  {cond:4s} n={n:3d} " + " ".join(f"{L}={tab[cond][L]}" for L in LABELS + ["NO_TRIAL"]))


if __name__ == "__main__":
    main()
