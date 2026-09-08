#!/usr/bin/env python3
"""Use a local LLM to propose one exact old/new pair per notice for review.

The model is a recall aid only. A proposal is retained only when both strings
are literal normalized substrings of publisher-authored notice text. Human
review and original-article verification remain mandatory.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from audit_original_state import normalized


def parse_object(value: str) -> dict | None:
    match = re.search(r"\{.*?\}", value, re.S)
    if not match:
        return None
    try:
        item = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(item, dict) or not isinstance(item.get("old"), str) or not isinstance(item.get("new"), str):
        return None
    return item


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()
    project = args.config.resolve().parent.parent
    config = json.loads(args.config.read_text(encoding="utf-8"))
    notices = [
        row for row in map(json.loads, (project / "data/processed/e003/notices.jsonl").read_text().splitlines())
        if row["parser_category"] == "exact_replacement_candidate"
    ]

    prompts = []
    evidence_by_pmid = {}
    instruction = (
        "You are screening a publisher-authored correction notice. Find at most one scientifically substantive "
        "replacement operation for article content. Exclude authors, affiliations, funding, references/citations, "
        "licenses, acknowledgements, and spelling-only changes. Both obsolete and corrected content must be explicit. "
        "Copy the shortest distinguishing OLD and NEW strings verbatim from the notice; do not paraphrase or infer. "
        "Return exactly one JSON object {\"old\":\"...\",\"new\":\"...\",\"location\":\"...\"}, "
        "or {} if no qualifying pair exists.\n\nNOTICE:\n"
    )
    for row in notices:
        evidence = "\n".join(row["evidence_snippets"])[: int(config["max_input_characters"])]
        evidence_by_pmid[row["pmid"]] = evidence
        prompts.append(instruction + evidence)

    tokenizer = AutoTokenizer.from_pretrained(config["model"], local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        config["model"], local_files_only=True, dtype=torch.bfloat16, device_map={"": args.device}
    )
    model.eval()
    outputs = []
    for start in range(0, len(prompts), args.batch_size):
        batchilho = prompts[start : start + args.batch_size]
        chats = [[{"role": "user", "content": prompt}] for prompt in batchilho]
        rendered = tokenizer.apply_chat_template(chats, tokenize=False, add_generation_prompt=True)
        encoded = tokenizer(rendered, return_tensors="pt", padding=True).to(args.device)
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                do_sample=bool(config["do_sample"]),
                max_new_tokens=int(config["max_new_tokens"]),
                pad_token_id=tokenizer.pad_token_id,
            )
        outputs.extend(
            tokenizer.batch_decode(generated[:, encoded["input_ids"].shape[1] :], skip_special_tokens=True)
        )

    accepted = []
    raw_rows = []
    for row, output in zip(notices, outputs):
        item = parse_object(output)
        status = "no_json_or_empty"
        if item and item.get("old") and item.get("new"):
            notice_text = evidence_by_pmid[row["pmid"]]
            old = " ".join(item["old"].split())
            new = " ".join(item["new"].split())
            if normalized(old) == normalized(new):
                status = "identical_after_normalization"
            elif normalized(old) not in normalized(notice_text):
                status = "old_not_verbatim"
            elif normalized(new) not in normalized(notice_text):
                status = "new_not_verbatim"
            else:
                status = "verbatim_proposal"
                accepted.append({
                    "candidate_id": f"{row['pmid']}-llm",
                    "correction_pmid": row["pmid"],
                    "correction_pmcid": row["pmcid"],
                    "original_pmids": [ref["pmid"] for ref in row["erratum_for"] if ref["pmid"]],
                    "year": row["year"],
                    "journal": row["journal"],
                    "title": row["title"],
                    "old": old,
                    "new": new,
                    "location": str(item.get("location", "")),
                    "evidence": notice_text,
                    "source_pmc_url": row["source_pmc_url"],
                    "review_label": "",
                    "review_note": "",
                })
        raw_rows.append({"correction_pmid": row["pmid"], "status": status, "output": output})

    processed = project / "data/processed/e003"
    (processed / "llm_pair_proposals.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in accepted), encoding="utf-8"
    )
    result_dir = project / "results/e003"
    (result_dir / "llm_extractor_raw.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in raw_rows), encoding="utf-8"
    )
    summary = {
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "model": config["model"],
        "notices_screened": len(notices),
        "verbatim_proposals": len(accepted),
        "records_with_verbatim_proposal": len({row["correction_pmid"] for row in accepted}),
        "status_counts": {
            status: sum(row["status"] == status for row in raw_rows)
            for status in sorted({row["status"] for row in raw_rows})
        },
        "warning": "LLM proposals are not gold; human review and original-state checks are mandatory.",
    }
    (result_dir / "llm_extractor_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
