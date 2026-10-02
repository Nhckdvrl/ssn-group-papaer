"""E04 CPU-only preparation: same official MT source, matched language budgets."""
import base64
import collections
import hashlib
import json
from pathlib import Path
import random

import nli_learning as nli
import qa_learning as qa

ROOT = Path(__file__).resolve().parents[1]
N = 8192
UNIQUE_CONTEXTS = 4096
MAX_LENGTH = 2048


def context_key(row):
    return hashlib.sha256(" ".join(row["context"].split()).encode()).hexdigest()


def main():
    from datasets import load_dataset
    from transformers import AutoTokenizer
    output = ROOT / "artifacts/qa_bridge/data.json"
    assert not output.exists(), "Never silently replace a prepared intervention pool"
    task = json.loads(qa.DATA.read_text())
    raw_path = ROOT / "artifacts/qa_learning/squad.translate.train.en-de.json"
    raw = raw_path.read_bytes()
    assert len(raw) == 93188862
    assert base64.b64encode(hashlib.md5(raw).digest()).decode() == "uszApqUqjjtUneb/lk9JEQ=="
    translated = {}
    for article in json.loads(raw)["data"]:
        for paragraph in article["paragraphs"]:
            for question in paragraph["qas"]:
                row = dict(id=question["id"],context=paragraph["context"],question=question["question"])
                assert row["id"] not in translated, "Duplicate translated question ID"
                translated[row["id"]] = row
    del raw
    source = load_dataset("rajpurkar/squad",revision=qa.REVISIONS["rajpurkar/squad"])["train"]
    original = {r["id"]:r for r in source}
    assert set(translated) <= set(original), "Translation IDs not from original SQuAD train"
    manifest = json.loads((ROOT / "artifacts/model_manifests/UCLNLP__monoweb__ckpt_exp_en_de_monoweb.json").read_text())
    tok = AutoTokenizer.from_pretrained(manifest["path"],local_files_only=True)
    assert nli.digest(tok.get_vocab()) == task["metadata"]["tokenizer_sha256"]
    excluded = {context_key(r) for name in ("en_dev","en_test") for r in task["splits"][name]}
    forbidden_reuse = excluded | {context_key(r) for r in task["splits"]["train"]}
    removed = collections.Counter()

    def units(rows):
        accepted = []
        for start in range(0,len(rows),128):
            block = []
            for row in rows[start:start+128]:
                if row["id"] not in translated:
                    removed["no_official_translation"] += 1
                    continue
                assert all(row[k] == original[row["id"]][k] for k in ("context","question"))
                block.append(row)
            texts = [[r["context"]+"\n"+r["question"] for r in block],
                     [translated[r["id"]]["context"]+"\n"+translated[r["id"]]["question"] for r in block]]
            if not block:
                continue
            a,b = [tok(t,add_special_tokens=False)["input_ids"] for t in texts]
            for row,en,de in zip(block,a,b):
                source_ids = [tok.bos_token_id]+en+[tok.eos_token_id]
                target_ids = [tok.bos_token_id]+de+[tok.eos_token_id]
                if len(source_ids)+len(target_ids) > MAX_LENGTH:
                    removed["complete_unit_over_2048"] += 1
                    continue
                accepted.append(dict(id=row["id"],context_sha256=context_key(row),
                                     ids=source_ids+target_ids,boundary=len(source_ids)))
        return accepted

    new_rows = [r for r in task["splits"]["train"] if context_key(r) not in excluded]
    random.Random(20261004).shuffle(new_rows)
    def unique_contexts(pool):
        selected, seen = [],set()
        for unit in pool:
            if unit["context_sha256"] not in seen:
                seen.add(unit["context_sha256"])
                selected.append(unit)
        return selected

    new_unique = unique_contexts(units(new_rows))[:UNIQUE_CONTEXTS]
    assert len(new_unique) == UNIQUE_CONTEXTS
    candidates = [r for r in source if context_key(r) not in forbidden_reuse]
    random.Random(20261004).shuffle(candidates)
    reuse_candidates = unique_contexts(units(candidates))
    assert len(reuse_candidates) >= UNIQUE_CONTEXTS, "Not enough context-disjoint complete units"
    buckets = collections.defaultdict(list)
    for unit in reuse_candidates:
        buckets[unit["boundary"],len(unit["ids"])-unit["boundary"]].append(unit)
    reused, exact_matches = [],0
    for unit in new_unique:
        key = unit["boundary"],len(unit["ids"])-unit["boundary"]
        if buckets[key]:
            exact_matches += 1
            reused.append(buckets[key].pop())
        else:
            remaining = [k for k,v in buckets.items() if v]
            nearest = min(remaining,key=lambda k:(abs(k[0]-key[0])+abs(k[1]-key[1]),k))
            reused.append(buckets[nearest].pop())
    assert len({u["id"] for u in reused}) == UNIQUE_CONTEXTS
    assert not {u["context_sha256"] for u in reused} & forbidden_reuse
    # Both pools expose exactly 4096 independent contexts twice, not unequal diversity.
    new = new_unique*2
    reused = reused*2
    assert len(new) == len(reused) == N
    holdout = units(task["splits"]["en_dev"])[:128]
    assert len(holdout) == 128
    pools = dict(new=new,reused=reused,holdout=holdout)
    totals = {k:dict(en=sum(u["boundary"]-1 for u in v),
                     de=sum(len(u["ids"])-u["boundary"]-1 for u in v)) for k,v in pools.items()}
    for language in ("en","de"):
        assert abs(totals["new"][language]-totals["reused"][language])/totals["new"][language] <= .01, "Language exposure mismatch"
    metadata = dict(source_revision=qa.REVISIONS["rajpurkar/squad"],task_hashes=task["metadata"]["hashes"],
                    translation=dict(url="https://storage.googleapis.com/xtreme_translations/SQuAD/translate-train/squad.translate.train.en-de.json",
                                     generation="1591613668067959",size=raw_path.stat().st_size,
                                     sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest()),
                    hashes={k:nli.digest(v) for k,v in pools.items()},token_totals=totals,
                    counts={k:len(v) for k,v in pools.items()},
                    context_repetition={k:dict(unique=len({u["context_sha256"] for u in v}),
                                              max_questions_per_context=max(collections.Counter(u["context_sha256"] for u in v).values())) for k,v in pools.items()},
                    exact_length_matches=exact_matches,removed=dict(removed),candidate_count=len(reuse_candidates),
                    official_translation_ids_verified=True,reuse_context_disjoint=True,answers_in_cpt=False,
                    unique_contexts_per_training_pool=UNIQUE_CONTEXTS,repeat_per_unit=2,
                    tokenizer_sha256=nli.digest(tok.get_vocab()),max_length=MAX_LENGTH,base_model=manifest,pad=tok.eos_token_id)
    nli.dump(output,dict(metadata=metadata,pools=pools))
    nli.dump(ROOT / "results/e04_data_manifest.json",metadata)
    print(json.dumps(metadata),flush=True)


if __name__ == "__main__":
    main()
