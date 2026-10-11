"""POST-HOC content audit: distinguish final judgments from labels in reasoning."""
import argparse
import json
import re
from pathlib import Path
import numpy as np
from e88_criterion_transfer import interval


def final_label(s):
    if s["truncated"]:
        return -1, "censored"
    lines = [line.strip() for line in s["text"].splitlines() if line.strip()]
    if not lines:
        return -1, "empty"
    matches = set(re.findall(r"\b(negative|positive)\b", lines[-1].lower()))
    if len(matches) == 1:
        return int(next(iter(matches)) == "positive"), "unambiguous_last_line"
    matches = set(re.findall(r"\b(negative|positive)\b", s["text"].lower()))
    if len(matches) == 1:
        return int(next(iter(matches)) == "positive"), "unambiguous_whole_answer"
    return -1, "ambiguous"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    a = ap.parse_args()
    dest = Path(a.directory)
    rows = [json.loads(x) for x in (dest/"behavior.jsonl").read_text().splitlines()]
    out = {"status": "POST-HOC final-content audit; original whole-answer parser retained",
           "rule": "Completed responses: unambiguous label in final nonempty line; else unique label in whole answer. No correctness-based selection.",
           "conditions": {}, "changed_response_tails": [], "unparsed_response_tails": []}
    for key in rows[0]["conditions"]:
        labels=[]; signs=[]; methods={}
        for row in rows:
            rr=[]; gg=[]
            for qi,(q,s) in enumerate(zip(row["queries"],row["conditions"][key]["application"])):
                label,method=final_label(s)
                methods[method]=methods.get(method,0)+1
                rr.append(label); gg.append(int((q["donor_gold"] if "flip" in key else q["recipient_gold"])>0))
                item={"context":row["context"],"condition":key,"query":qi,"label":label,"method":method,"tail":s["text"][-500:]}
                if label != s["generated_class"]: out["changed_response_tails"].append(item)
                if label == -1: out["unparsed_response_tails"].append(item)
            labels.append(rr); signs.append(gg)
        labels,signs=np.array(labels),np.array(signs)
        disagree=np.array([q["food"] != q["service"] for q in rows[0]["queries"]])
        out["conditions"][key]={"application_accuracy":interval((labels==signs).mean(1)),
            "discordant_accuracy":interval((labels[:,disagree]==signs[:,disagree]).mean(1)),
            "parse_fraction":interval((labels>=0).mean(1)),"methods":methods}
    (dest/"final_answer_audit_posthoc.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out["conditions"],indent=2))
    print("Changed tails",len(out["changed_response_tails"]),"unknown tails",len(out["unparsed_response_tails"]))


if __name__ == "__main__":
    main()
