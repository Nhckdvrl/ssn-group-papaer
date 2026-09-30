"""Independent check of every generated prompt by opencode free models.

The checker never sees the gold label.  It (1) solves the item, (2) reports which
suppositions it believes are in force at the question, (3) audits wording/scope clarity.
Disagreement with the programmatic gold, or any 'clear': false, flags the item.
Usage: verify_opencode.py items.jsonl out.jsonl model [--limit N] [--workers K]
"""
import json, re, subprocess, sys, tempfile, os, concurrent.futures as cf, time

CHECK = """You are a careful data auditor for a logic-puzzle dataset. Do NOT use any tools, do NOT read or write files; just answer in text.

Below is a puzzle exactly as a test-taker would see it. Do two things.

TASK 1 - Solve it yourself, from scratch, using only the stated rules and the stated complete attribute lists. Work step by step and be literal:
 - A person has an attribute only if it is listed for them (the lists are complete) OR it is added by a supposition that is CURRENTLY in force at the moment the question is asked.
 - A supposition is in force from the sentence that introduces it until a later sentence explicitly ends/drops it. Once a supposition has been dropped it no longer holds anywhere, and things that were only concluded under it no longer hold either.
 - If the question says "Under this supposition ...", "Under the first supposition only ...", "Under this second supposition only ..." it asks about the situation in which exactly those suppositions hold. If it says "In the actual situation" or has no such phrase, the question is about the situation with no supposition in force (or, when a sentence says a statement was added as a fact with 'In addition', with that fact true).
 - Apply the rules exactly, including the 'but does not ...' exceptions. Derived labels can feed later rules.

TASK 2 - Audit the puzzle text. Report problems a human annotator would flag:
 - "grammar": any sentence that is ungrammatical, missing punctuation that changes readability, or awkward enough to confuse a reader (quote the sentence).
 - "scope_unclear": it is not fully determined which suppositions are in force when the question is asked.
 - "rule_unclear": a rule can be read in more than one way.
 - "other": anything else that could make the correct answer debatable.

Return your final output as ONE line of JSON and nothing after it, with exactly these keys:
{"answer": "Yes" or "No", "active_suppositions_at_question": [list of the supposed statements you believe are in force, [] if none], "derivation": "one or two short sentences", "clear": true or false, "issues": [list of short strings, [] if none]}

=== PUZZLE START ===
%s
=== PUZZLE END ===
"""


def call(model, prompt, timeout=240):
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(["opencode", "run", "--standalone", "-m", f"opencode/{model}", prompt], cwd=d,
                           capture_output=True, text=True, timeout=timeout)
    out = r.stdout
    js = re.findall(r"\{.*\}", out, flags=re.S)
    for cand in reversed(js):
        # the last balanced {...} that parses
        for m in re.finditer(r"\{[^{}]*(?:\[[^\]]*\][^{}]*)*\}", cand):
            pass
    lines = [l for l in out.splitlines() if l.strip().startswith("{") and l.strip().endswith("}")]
    for l in reversed(lines):
        try:
            return json.loads(l), out
        except Exception:
            continue
    # fallback: try any {...} substring
    for m in reversed(list(re.finditer(r"\{[^{}]*\"answer\"[^{}]*\}", out, flags=re.S))):
        try:
            return json.loads(m.group(0)), out
        except Exception:
            continue
    return None, out


def work(model, it):
    for attempt in range(3):
        try:
            res, raw = call(model, CHECK % it["prompt"])
            if res is not None:
                return dict(id=it["id"], model=model, res=res, gold=it["gold"], cond=it["cond"],
                            family=it["family"], depth=it["depth"])
        except Exception as e:
            raw = repr(e)
        time.sleep(2 + 3 * attempt)
    return dict(id=it["id"], model=model, res=None, gold=it["gold"], cond=it["cond"], family=it["family"],
                depth=it["depth"], raw=raw[-500:])


def main():
    a = sys.argv[1:]
    items_p, out_p, model = a[0], a[1], a[2]
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    workers = int(a[a.index("--workers") + 1]) if "--workers" in a else 8
    items = [json.loads(l) for l in open(items_p)]
    if limit:
        import random
        random.Random(0).shuffle(items)
        items = items[:limit]
    done = set()
    if os.path.exists(out_p):
        done = {json.loads(l)["id"] for l in open(out_p) if json.loads(l).get("res")}
    todo = [it for it in items if it["id"] not in done]
    with open(out_p, "a") as f, cf.ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(work, model, it) for it in todo]
        for k, fu in enumerate(cf.as_completed(futs)):
            f.write(json.dumps(fu.result()) + "\n"); f.flush()
            if k % 50 == 0:
                print(model, k, "/", len(todo), flush=True)


if __name__ == "__main__":
    main()
