"""S03 / E02 — run the E01 instrument on a trained arm."""
import argparse, json, os, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from e01_run import STAGE_REPOS, stop_token_ids, measure
from e02_arms import ArmModel, StopReadout


class Wrapped:
    """Expose an ArmModel through the plain-model interface e01_run.measure wants."""
    def __init__(self, arm, device):
        self.arm = arm; self.device = device
    def __call__(self, x):
        class O: pass
        o = O(); o.logits = self.arm(x)
        return o


def load_arm(outdir, family):
    cfg = json.load(open(f"{outdir}/config.json"))
    arm_name = cfg["arm"]
    tmpl = AutoTokenizer.from_pretrained(STAGE_REPOS[family]["sft"])
    if arm_name in ("R", "Rmlp"):
        repo = STAGE_REPOS[family]["base"]
        tok = AutoTokenizer.from_pretrained(repo)
        model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.bfloat16).cuda().eval()
        arm = ArmModel(model, cfg["stop_ids"], arm_name).cuda()
        arm.readout = arm.readout.cuda().float()
        arm.readout.load_state_dict(torch.load(f"{outdir}/readout.pt"))
    else:
        tok = AutoTokenizer.from_pretrained(f"{outdir}/model")
        model = AutoModelForCausalLM.from_pretrained(f"{outdir}/model",
                                                     dtype=torch.bfloat16).cuda().eval()
        arm = ArmModel(model, cfg["stop_ids"], "base").cuda()
    arm.eval()
    tok.chat_template = tmpl.chat_template
    return tok, arm, cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--family", default="olmo3-7b")
    ap.add_argument("--stimuli", default="stimuli/e01_pairs.jsonl")
    ap.add_argument("--plain", action="store_true")
    args = ap.parse_args()

    tok, arm, cfg = load_arm(args.outdir, args.family)
    sids = cfg["stop_ids"]
    wrapped = Wrapped(arm, "cuda"); wrapped.device = "cuda"
    chat = (tok.chat_template is not None) and not args.plain

    items = [json.loads(l) for l in open(args.stimuli)]
    rows = []
    for it in items:
        c = measure(wrapped, tok, it, "complete", chat, sids)
        i = measure(wrapped, tok, it, "incomplete", chat, sids)
        assert c.pop("_prefix_ids") == i.pop("_prefix_ids")
        comp = c.pop("_comp_tok_p2"); i.pop("_comp_tok_p2")
        row = dict(item_id=it["item_id"], family=it["family"], n_given=it["n_given"],
                   comp_token=comp, stage=cfg["arm"], model_family=args.family, chat=chat)
        row.update({"cmp_" + k: v for k, v in c.items()})
        row.update({"inc_" + k: v for k, v in i.items()})
        for tag in ("p1", "p2"):
            row[f"d_goal_{tag}"] = row[f"cmp_{tag}_margin"] - row[f"inc_{tag}_margin"]
        rows.append(row)
    out = f"{args.outdir}/e01{'_plain' if args.plain else ''}.jsonl"
    with open(out, "w") as fh:
        for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", out, len(rows))


if __name__ == "__main__":
    main()
