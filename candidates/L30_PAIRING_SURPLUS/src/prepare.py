"""Build the shared L30 E01 pool from Alpaca-Cleaned and freeze the S permutation.

Follows An et al.'s Response Tuning repo for data provenance and formatting:
  dataset  : yahma/alpaca-cleaned
  prompt   : instruction, or f"{instruction}\n\n{input}" when input is non-empty
  template : Tulu-style <|user|> / <|assistant|> delimiters

All four arms draw from this one pool, so the prompt marginal and the response
marginal are identical by construction across arms.
"""
import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from arms import SEG_ASST_OPEN, SEG_USER_OPEN, derangement  # noqa: E402


def sha256_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="google/gemma-2-2b")
    ap.add_argument("--max-prompt-tokens", type=int, default=768)
    ap.add_argument("--max-response-tokens", type=int, default=1024)
    ap.add_argument("--perm-seed", type=int, default=1730)
    ap.add_argument("--out", default=str(ROOT / "results" / "pool"))
    args = ap.parse_args()

    from datasets import load_dataset
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(args.model)
    ds = load_dataset("yahma/alpaca-cleaned")["train"]

    prompts, responses = [], []
    for ex in ds:
        inp = (ex["input"] or "").strip()
        instr = ex["instruction"]
        prompts.append(instr if not inp else f"{instr}\n\n{inp}")
        responses.append(ex["output"])

    enc = lambda xs: tok(xs, add_special_tokens=False)["input_ids"]
    x_ids_all = enc(prompts)
    y_ids_all = enc(responses)

    keep = [
        i
        for i in range(len(prompts))
        if 0 < len(x_ids_all[i]) <= args.max_prompt_tokens
        and 0 < len(y_ids_all[i]) <= args.max_response_tokens
    ]

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "pool.jsonl").open("w") as f:
        for new_i, i in enumerate(keep):
            f.write(
                json.dumps(
                    {
                        "idx": new_i,
                        "src_idx": i,
                        "x": prompts[i],
                        "y": responses[i],
                        "x_ids": x_ids_all[i],
                        "y_ids": y_ids_all[i],
                    }
                )
                + "\n"
            )

    perm = derangement(len(keep), args.perm_seed)
    (out / "perm.json").write_text(json.dumps({"seed": args.perm_seed, "perm": perm}))

    special = {
        "bos_id": tok.bos_token_id,
        "eos_id": tok.eos_token_id,
        "user_open_ids": tok(SEG_USER_OPEN, add_special_tokens=False)["input_ids"],
        "asst_open_ids": tok(SEG_ASST_OPEN, add_special_tokens=False)["input_ids"],
    }

    xl = [len(x_ids_all[i]) for i in keep]
    yl = [len(y_ids_all[i]) for i in keep]
    manifest = {
        "model": args.model,
        "dataset": "yahma/alpaca-cleaned",
        "n_source": len(prompts),
        "n_kept": len(keep),
        "dropped": len(prompts) - len(keep),
        "max_prompt_tokens": args.max_prompt_tokens,
        "max_response_tokens": args.max_response_tokens,
        "worst_case_seq_len": 1
        + len(special["user_open_ids"])
        + max(xl)
        + len(special["asst_open_ids"])
        + max(yl)
        + 1,
        "total_response_tokens": sum(yl) + len(yl),
        "prompt_tokens_mean": sum(xl) / len(xl),
        "response_tokens_mean": sum(yl) / len(yl),
        "perm_seed": args.perm_seed,
        "special": special,
        "pool_sha256": sha256_text((out / "pool.jsonl").read_text()),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "special"}, indent=2))


if __name__ == "__main__":
    main()
