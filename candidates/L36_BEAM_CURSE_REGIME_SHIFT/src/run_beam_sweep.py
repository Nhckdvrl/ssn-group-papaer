"""L36 E00/E01 — beam sweep with an explicit, logged generation contract.

One (model, beam width, scoring semantics) cell per invocation. Writes one JSONL row per
segment plus a header row holding the full contract, so that no decoding detail is implicit.
"""

import argparse
import json
import os
import time

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--revision", default="main")
    p.add_argument("--src", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--beam", type=int, required=True)
    p.add_argument("--semantics", choices=["RAW", "NORM"], required=True)
    p.add_argument("--max-new-tokens", type=int, default=256)
    p.add_argument("--beam-budget", type=int, default=256,
                   help="beam * batch_size cap, controls memory")
    p.add_argument("--dtype", default="float32")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--score-mode", choices=["generate", "rescore", "none"], default="generate",
                   help="generate: take the beam's own transition scores (correct for FSMT, whose "
                        "full-forward path disagrees with its incremental path in transformers "
                        "4.57.6); rescore: teacher-forced full forward; none: skip scoring")
    return p.parse_args()


def main():
    a = parse_args()
    src = [l.rstrip("\n") for l in open(a.src, encoding="utf-8")]
    if a.limit:
        src = src[:a.limit]

    tok = AutoTokenizer.from_pretrained(a.model, revision=a.revision)
    dtype = getattr(torch, a.dtype)
    model = AutoModelForSeq2SeqLM.from_pretrained(a.model, revision=a.revision, torch_dtype=dtype)
    model.eval().cuda()

    length_penalty = 0.0 if a.semantics == "RAW" else 1.0
    batch = max(1, a.beam_budget // a.beam)

    # length-sorted batching for throughput; original order restored on write
    order = sorted(range(len(src)), key=lambda i: -len(src[i]))
    results = [None] * len(src)
    t0 = time.time()
    done = 0
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        enc = tok([src[i] for i in idx], return_tensors="pt", padding=True,
                  truncation=True, max_length=512).to("cuda")
        with torch.no_grad():
            out = model.generate(
                **enc,
                num_beams=a.beam,
                do_sample=False,
                length_penalty=length_penalty,
                early_stopping=False,
                max_new_tokens=a.max_new_tokens,
                min_new_tokens=0,
                no_repeat_ngram_size=0,
                repetition_penalty=1.0,
                num_return_sequences=1,
                return_dict_in_generate=True,
                output_scores=(a.score_mode == "generate"),
            )
        seqs = out.sequences
        texts = tok.batch_decode(seqs, skip_special_tokens=True)

        # Raw cumulative log-probability of the selected hypothesis, i.e. the quantity the
        # length-normalisation question is about.  Default path takes the beam's own transition
        # scores: FSMT's full-forward decoder disagrees with its incremental decoding path in
        # transformers 4.57.6 (differences of tens of nats), so teacher-forced rescoring is not
        # trustworthy for it.
        if a.score_mode == "generate":
            # beam search already log-softmaxes its scores; greedy returns processed logits, so
            # only the greedy path must be normalised here
            ts = model.compute_transition_scores(
                seqs, out.scores, getattr(out, "beam_indices", None),
                normalize_logits=(a.beam == 1))
            keep = torch.isfinite(ts) & (seqs[:, 1:] != tok.pad_token_id)
            ts = torch.where(keep, ts, torch.zeros_like(ts))   # -inf or padding after EOS
            sum_lp = ts.sum(dim=1)
            n_tok = keep.sum(dim=1).clamp(min=1)
        elif a.score_mode == "rescore":
            labels = seqs[:, 1:].contiguous()
            with torch.no_grad():
                logits = model(**enc, decoder_input_ids=seqs[:, :-1], use_cache=False).logits.float()
            logprobs = torch.log_softmax(logits, dim=-1)
            tok_lp = logprobs.gather(2, labels.unsqueeze(-1)).squeeze(-1)
            mask = labels != tok.pad_token_id
            sum_lp = (tok_lp * mask).sum(dim=1)
            n_tok = mask.sum(dim=1).clamp(min=1)
        else:
            sum_lp = torch.full((seqs.shape[0],), float("nan"))
            n_tok = torch.ones(seqs.shape[0])

        for k, i in enumerate(idx):
            gen_len = int((seqs[k] != tok.pad_token_id).sum())
            results[i] = {
                "idx": i,
                "hyp": texts[k].strip(),
                "gen_tokens": gen_len,
                "truncated": bool(gen_len >= a.max_new_tokens),
                "sum_logprob": float(sum_lp[k]),
                "mean_logprob": float(sum_lp[k] / n_tok[k]),
                "scored_tokens": int(n_tok[k]),
            }
        done += len(idx)
        if s % (batch * 20) == 0:
            el = time.time() - t0
            print(f"  {done}/{len(src)}  {el:.0f}s  eta {el / max(done,1) * (len(src)-done):.0f}s",
                  flush=True)

    contract = {
        "_header": True,
        "model": a.model,
        "revision": a.revision,
        "src": os.path.basename(a.src),
        "n": len(src),
        "beam": a.beam,
        "semantics": a.semantics,
        "length_penalty": length_penalty,
        "early_stopping": False,
        "do_sample": False,
        "max_new_tokens": a.max_new_tokens,
        "min_new_tokens": 0,
        "no_repeat_ngram_size": 0,
        "repetition_penalty": 1.0,
        "num_return_sequences": 1,
        "dtype": a.dtype,
        "batch": batch,
        "score_mode": a.score_mode,
        "eos_token_id": model.generation_config.eos_token_id,
        "pad_token_id": model.generation_config.pad_token_id,
        "decoder_start_token_id": getattr(model.config, "decoder_start_token_id", None),
        "transformers_version": __import__("transformers").__version__,
        "torch_version": torch.__version__,
        "gpu": torch.cuda.get_device_name(0),
        "wall_seconds": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(contract, ensure_ascii=False) + "\n")
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", a.out, f"({contract['wall_seconds']}s)")


if __name__ == "__main__":
    main()
