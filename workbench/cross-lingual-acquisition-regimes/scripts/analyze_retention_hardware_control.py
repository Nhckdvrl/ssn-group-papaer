"""E08 audit and same-hardware translation retention, all conditions together."""
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import sacrebleu
from sacrebleu.metrics import BLEU, CHRF

import translation_control as tc

ROOT = Path(__file__).resolve().parents[1]


def generation_loop(path):
    tree = ast.parse(path.read_text())
    loops = [node for node in ast.walk(tree) if isinstance(node,ast.For)
             and isinstance(node.target,ast.Name) and node.target.id == "mode"]
    assert len(loops) == 1
    return ast.dump(loops[0],include_attributes=False)


def main():
    control_script = ROOT / "scripts/retention_hardware_control.py"
    post_script = ROOT / "scripts/qa_translation_retention.py"
    assert generation_loop(control_script) == generation_loop(post_script)
    reports = {}
    for condition in ("baseline","monoweb","onlyparallel"):
        folder = ROOT / "artifacts/retention_hardware_control" / condition
        done = json.loads((folder / "completion.json").read_text())
        post_folder = ROOT / "artifacts/qa_retention" / f"{condition}_seed17"
        post_done = json.loads((post_folder / "completion.json").read_text())
        assert done["condition"] == condition and done["device"] == post_done["device"]
        assert done["torch"] == post_done["qa_provenance"]["torch"]
        assert done["script_sha256"] == hashlib.sha256(control_script.read_bytes()).hexdigest()
        assert done["protocol_reference_sha256"] == post_done["script_sha256"] == hashlib.sha256(post_script.read_bytes()).hexdigest()
        assert done["weight_dtype"] == done["compute_dtype"] == "fp32" and done["use_cache"]
        paths = dict(legacy=ROOT / "artifacts/p2" / f"translation_{condition}_34k.jsonl",
            pre=folder / "primary.jsonl",pre_instruction=folder / "instruction.jsonl",
            post=post_folder / "primary.jsonl",post_instruction=post_folder / "instruction.jsonl")
        rows = {key:[json.loads(line) for line in path.read_text().splitlines()] for key,path in paths.items()}
        ids = [(r["id"],r["direction"]) for r in rows["legacy"]]
        assert len(ids) == len(set(ids)) == 400
        for sample in rows.values():
            assert [(r["id"],r["direction"]) for r in sample] == ids
            assert tc.digest([{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in sample]) == done["items_sha256"] == post_done["items_sha256"]
        directions = {}
        for direction in ("en->de","de->en"):
            selected = {key:[r for r in sample if r["direction"] == direction] for key,sample in rows.items()}
            refs = [r["reference"] for r in selected["pre"]]
            n = len(refs)
            draws = np.random.default_rng(20261002).integers(0,n,size=(2000,n))
            metrics, contrasts = {}, {}
            for name,metric in (("bleu",BLEU(tokenize="13a")),("chrf",CHRF())):
                distributions, points = {}, {}
                for key,sample in selected.items():
                    hyp = [r["prediction"] for r in sample]
                    points[key] = metric.corpus_score(hyp,[refs]).score
                    stats = np.asarray(metric._extract_corpus_statistics(hyp,[refs]))
                    assert abs(metric._compute_score_from_stats(stats.sum(0).tolist()).score-points[key]) < 1e-8
                    distributions[key] = np.array([metric._compute_score_from_stats(s.tolist()).score for s in stats[draws].sum(1)])
                    metrics[key+"_"+name] = dict(score=points[key],sentence_bootstrap95=np.quantile(distributions[key],[.025,.975]).tolist(),signature=str(metric.get_signature()))
                for a,b in (("pre","legacy"),("post","pre"),("post_instruction","pre"),("post_instruction","pre_instruction")):
                    contrasts[a+"-"+b+"_"+name] = dict(delta=points[a]-points[b],
                        paired_sentence_bootstrap95=np.quantile(distributions[a]-distributions[b],[.025,.975]).tolist())
            directions[direction] = dict(n=n,metrics=metrics,contrasts=contrasts,
                legacy_prediction_matches=sum(a["prediction"] == b["prediction"] for a,b in zip(selected["pre"],selected["legacy"])),
                diagnostics={key:dict(source_copies=sum(r["source_copied"] for r in sample),empty=sum(not r["prediction"] for r in sample),
                    cap=sum(r["token_cap_reached"] for r in sample),overflow=sum(r.get("overflow",False) for r in sample)) for key,sample in selected.items()})
        reports[condition] = dict(completion=done,directions=directions,
            prediction_sha256={key:hashlib.sha256(path.read_bytes()).hexdigest() for key,path in paths.items()})
    report = dict(models=reports,protocol_ast_equal=True,resamples=2000,bootstrap_seed=20261002,sacrebleu_version=sacrebleu.__version__,
        limits="One QA adaptation seed and fixed 200 news sentences. Same-hardware calibration is not a new seed or evidence of a universal forgetting mechanism.")
    path = ROOT / "results/e08_retention_hardware_control.json"
    path.write_text(json.dumps(report,indent=2)+"\n")
    for condition,r in reports.items():
        for direction,v in r["directions"].items():
            print(condition,direction,"legacy_matches",v["legacy_prediction_matches"],
                  {k:round(x["score"],2) for k,x in v["metrics"].items() if k.endswith("_bleu")})
    print(path)


if __name__ == "__main__":
    main()
