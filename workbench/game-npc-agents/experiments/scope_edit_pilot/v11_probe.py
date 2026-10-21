#!/usr/bin/env python3
"""V1.1 situated creative-feedback adapter; protocol smoke test, not research evidence.

The same actor gets either an explicit author rule or one situated correction.
The two modes contain DIFFERENT INFORMATION; they are not equivalent algorithms.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import scope_probe as v1


def load_extra(path):
    obj = v1.read_json(path)
    if obj.get("version") != "1.1" or not isinstance(obj.get("stories"), dict):
        raise ValueError("Expected version 1.1 and story override objects")
    return obj


def make_tasks(fixtures, overrides):
    v1.validate(fixtures)
    output = []
    for story in fixtures["stories"]:
        sid = story["story_id"]
        info = overrides["stories"].get(sid)
        if not info:
            raise ValueError("Missing situated critique for " + sid)
        for field in ("source_scene", "bad_performance", "author_feedback", "preferred_performance"):
            if not isinstance(info.get(field), str) or not info[field].strip():
                raise ValueError("Missing " + field + " for " + sid)
        quadrants = info.get("cases", {})
        if set(quadrants) != {c["case_id"] for c in story["cases"]}:
            raise ValueError("Every existing case needs a quadrant/ambiguity annotation for " + sid)
        for case in story["cases"]:
            cid = case["case_id"]
            meta = quadrants[cid]
            if meta.get("category") not in ("target", "relation_near", "trigger_near", "other_control"):
                raise ValueError("Bad category for " + sid + "/" + cid)
            if meta.get("situated_scope") not in ("supported", "underspecified"):
                raise ValueError("Missing scope identifiability for " + sid + "/" + cid)
            scenes = [("base", case["scenario"])]
            pressure = meta.get("pressure_suffix")
            if pressure:
                if case["scope"] != "preserve":
                    raise ValueError("Pressure twin must start with an out-of-edit-scope control")
                scenes.append(("pressure", case["scenario"] + "\n\nPlayer adds: " + pressure))
            choices = "\n".join(f"{key}: {description}" for key, description in case["actions"].items())
            for variant, scene in scenes:
                for mode in ("original", "explicit", "situated"):
                    profile = story["persona"]
                    if mode == "explicit":
                        profile += "\n\nFULL AUTHOR REVISION:\n" + story["author_edit"]
                    elif mode == "situated":
                        profile += (
                            "\n\nAUTHOR FEEDBACK ABOUT ONE PREVIOUS REHEARSAL (not a complete universal rule):"
                            f"\nScene: {info['source_scene']}"
                            f"\nUnwanted performance: {info['bad_performance']}"
                            f"\nAuthor feedback: {info['author_feedback']}"
                            f"\nCorrected performance: {info['preferred_performance']}"
                        )
                    user = (
                        "CHARACTER BACKGROUND:\n" + profile +
                        "\n\nCURRENT SCENE:\n" + scene +
                        "\n\nAVAILABLE PHYSICAL/NARRATIVE ACTIONS (tone is expressed separately):\n" + choices
                    )
                    instructions = (
                        "Role-play as the given fictional character. Select a plausible next action and separately "
                        "write one line of dialogue in the character's existing style. Use only available actions; "
                        "avoid invented plot facts. Return only JSON with action_id and utterance. "
                        "Do not output inner thought or chain-of-thought."
                    )
                    output.append(dict(
                        task_id=f"{sid}/{cid}/{variant}/{mode}", story_id=sid, case_id=cid, variant=variant,
                        mode=mode, category=meta["category"], scope=case["scope"],
                        situated_scope=meta["situated_scope"],
                        author_verified=bool(meta.get("author_verified", False)),
                        decision_identifiable=bool(meta.get("decision_identifiable", False)),
                        expected_actions=case["expected_before" if mode == "original" else "expected_after"],
                        allowed_actions=list(case["actions"]),
                        messages=[{"role":"system","content":instructions},{"role":"user","content":user}]
                    ))
    return output


def evaluate(tasks, responses):
    answers = {}
    for r in responses:
        if r["task_id"] in answers:
            raise ValueError("Duplicate response in same run/seed: " + r["task_id"])
        answers[r["task_id"]] = r
    if set(answers) - {t["task_id"] for t in tasks}:
        raise ValueError("Some responses do not match this task batch")
    groups = defaultdict(list)
    rows = []
    for task in tasks:
        r = answers.get(task["task_id"], {})
        action = r.get("action_id")
        if action is None and isinstance(r.get("raw"), str):
            action, _ = v1.parse_reply(r["raw"])
        valid = action in task["allowed_actions"]
        correct = bool(valid and action in task["expected_actions"])
        # Developer-written scope labels are not independent evidence of author intent.
        # Require independent confirmation AND decision-identifiability before strict scoring.
        annotated = task["mode"] != "situated" or (
            task.get("author_verified", False) and task.get("decision_identifiable", False)
        )
        item = {k:task[k] for k in
                ("task_id","story_id","case_id","variant","mode","category","scope","situated_scope")}
        utterance = r.get("utterance")
        if utterance is None and isinstance(r.get("raw"), str):
            _, utterance = v1.parse_reply(r["raw"])
        item.update(
            action=action, valid=valid, author_intent_agreement=correct, strictly_scored=annotated,
            response_received=(task["task_id"] in answers), model_error=bool(r.get("error")),
            utterance_present=(isinstance(utterance, str) and bool(utterance.strip())),
        )
        rows.append(item)
        groups[(task["mode"], task["category"], task["variant"])].append(item)
    metrics = []
    for (mode, cat, variant), items in sorted(groups.items()):
        n = sum(i["strictly_scored"] for i in items)
        acc = sum(i["author_intent_agreement"] for i in items if i["strictly_scored"])
        metrics.append(dict(mode=mode, category=cat, variant=variant, n_scored=n,
                            correct_scored=acc, n_author_intent_only=len(items)-n,
                            author_intent_agreement_total=sum(i["author_intent_agreement"] for i in items)))
    indexed = {(x["story_id"], x["case_id"], x["variant"], x["mode"]):x for x in rows}
    pairs = []
    for item in rows:
        if item["mode"] == "original":
            continue
        baseline = indexed[(item["story_id"], item["case_id"], item["variant"], "original")]
        pairs.append(dict(story_id=item["story_id"], case_id=item["case_id"],
                          variant=item["variant"], mode=item["mode"], scope=item["scope"],
                          reference_before_correct=baseline["author_intent_agreement"],
                          reference_after_correct=item["author_intent_agreement"],
                          strictly_scored=item["strictly_scored"],
                          paired_correct=baseline["author_intent_agreement"] and item["author_intent_agreement"],
                          observed_action_changed=bool(baseline["valid"] and item["valid"] and baseline["action"]!=item["action"])))
    # A controlled synthetic world's predeclared generating rule IS scoreable.
    # This is separate from whether that rule is identifiable from a single critique.
    # Nonempty counts are important: an uncertified situated scope must not erase
    # legitimate synthetic-oracle measurements.
    synthetic_oracle_by_mode = {}
    synthetic_oracle_by_bucket = []
    for mode in ("original", "situated", "explicit"):
        subset = [r for r in rows if r["mode"] == mode]
        n_requested = len(subset)
        n_received = sum(r["response_received"] for r in subset)
        n_valid = sum(r["valid"] for r in subset)
        n_matched = sum(r["author_intent_agreement"] for r in subset)
        synthetic_oracle_by_mode[mode] = {
            "n_requested": n_requested, "n_received": n_received,
            "n_valid_action": n_valid,
            "n_action_oracle_match": n_matched,
            "oracle_match_per_received": (n_matched / n_received if n_received else None),
            "oracle_match_given_valid_action": (n_matched / n_valid if n_valid else None),
            "n_with_utterance": sum(r["utterance_present"] for r in subset),
            "n_model_error": sum(r["model_error"] for r in subset),
        }
        for scope in ("change", "preserve"):
            block = [r for r in subset if r["scope"] == scope]
            n_recd = sum(r["response_received"] for r in block)
            synthetic_oracle_by_bucket.append({
                "mode": mode, "scope": scope, "n_requested": len(block),
                "n_received": n_recd,
                "n_action_oracle_match": sum(r["author_intent_agreement"] for r in block),
                "oracle_match_per_received": (
                    sum(r["author_intent_agreement"] for r in block) / n_recd
                    if n_recd else None
                ),
            })
    # Pressure variants are dependent twins, not additional independent worlds.
    pressure_pairs = []
    by_context = {
        (r["story_id"], r["case_id"], r["mode"], r["variant"]): r for r in rows
    }
    for row in rows:
        if row["variant"] != "pressure":
            continue
        key = (row["story_id"], row["case_id"], row["mode"], "base")
        baseline = by_context.get(key)
        if baseline is None:
            raise ValueError("Missing base case for pressure twin: " + repr(key))
        pressure_pairs.append({
            "story_id": row["story_id"], "case_id": row["case_id"],
            "mode": row["mode"],
            "both_valid": bool(baseline["valid"] and row["valid"]),
            "action_changed": (
                baseline["action"] != row["action"]
                if baseline["valid"] and row["valid"] else None
            ),
            "base_oracle_match": baseline["author_intent_agreement"],
            "pressure_oracle_match": row["author_intent_agreement"],
        })
    all_received = sum(r["response_received"] for r in rows)
    strict_situated = [r for r in rows if r["mode"] == "situated" and r["strictly_scored"]]
    return {
        "warning": (
            "Developer-authored synthetic ORACLE action labels are valid scores under the "
            "chosen generating rule, NOT proof the rule is uniquely inferable from "
            "persona and situated critique or valid for real authors. The present "
            "situated fixture has no independently certified consensus labels. "
            "Utterance text is saved but tone is NOT evaluated here."
        ),
        "n_stories": len({i["story_id"] for i in rows}),
        "n_tasks": len(tasks), "n_responses": len(responses),
        "complete": all_received == len(tasks),
        "synthetic_oracle_by_mode": synthetic_oracle_by_mode,
        "synthetic_oracle_by_bucket": synthetic_oracle_by_bucket,
        "n_certified_situated": len(strict_situated),
        "metrics": metrics, "pressure_pairs": pressure_pairs,
        "paired_comparisons": pairs, "details": rows
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="cmd", required=True)
    for name in ("render", "validate"):
        p = sub.add_parser(name)
        p.add_argument("--fixtures",default="fixtures.json")
        p.add_argument("--overrides",default="v11_annotations.json")
        if name == "render":
            p.add_argument("--out",required=True)
    p = sub.add_parser("score")
    p.add_argument("--tasks",required=True)
    p.add_argument("--responses",required=True)
    p.add_argument("--out")
    args = cli.parse_args()
    if args.cmd in ("validate", "render"):
        rows = make_tasks(v1.read_json(args.fixtures),load_extra(args.overrides))
        if args.cmd == "validate":
            print(json.dumps({"stories":len({r["story_id"] for r in rows}),
                              "tasks":len(rows),"modes":dict(Counter(r["mode"] for r in rows))},indent=2))
        else:
            v1.write_jsonl(args.out, rows)
            print("Wrote",len(rows),"requests:",args.out)
    else:
        obj = evaluate(v1.read_jsonl(args.tasks),v1.read_jsonl(args.responses))
        data = json.dumps(obj,ensure_ascii=False,indent=2) + "\n"
        if args.out:
            Path(args.out).write_text(data,encoding="utf-8")
        else:
            print(data)

if __name__ == "__main__":
    main()
