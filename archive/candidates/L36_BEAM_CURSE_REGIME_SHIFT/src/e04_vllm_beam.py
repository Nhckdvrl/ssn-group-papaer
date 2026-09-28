"""E04 — cross-implementation check: is the rank -> onset relation a HuggingFace artefact?

Runs the *same* prompts and the *same* beam widths through vLLM's independently written beam
search and compares the empty-rate / length-ratio curves against the HuggingFace curves measured
everywhere else in this candidate.

Scope note (important, and stated in the results doc): vLLM's `LLM.beam_search` terminates a
hypothesis only on `tokenizer.eos_token_id`, so it cannot express the multi-token "a line break ends
the translation" stop contract used by the few-shot cells. The comparison is therefore run on the
E02 checkpoints, whose *only* boundary symbol is a single dedicated token -- exactly the setting
where the two implementations are expressing the same stopping rule.
"""
import argparse, json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M                                    # noqa: E402

FMT_A = "### User: Translate the following English sentence into German.\n{src}\n### Assistant: "
FMT_B = "English: {src}\nGerman: "


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--fmt", choices=["A", "B"], required=True)
    p.add_argument("--end-token", default="<|quad_start|>")
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--beams", default="1,4,16,64")
    p.add_argument("--max-new-tokens", type=int, default=128)
    p.add_argument("--gpu-frac", type=float, default=0.85)
    a = p.parse_args()

    src = [l.rstrip("\n") for l in open(os.path.join(ROOT, "data", "newstest2019.en"))][:a.n]
    rw = [l.rstrip("\n") for l in open(os.path.join(ROOT, "data", "newstest2019.wmtref.de"))][:a.n]
    ra = [l.rstrip("\n") for l in open(os.path.join(ROOT, "data", "newstest2019.arref.de"))][:a.n]
    tmpl = FMT_A if a.fmt == "A" else FMT_B
    prompts = [tmpl.format(src=s) for s in src]
    ref_len = float(np.mean([len(r.split()) for r in rw]))

    from vllm import LLM
    from vllm.sampling_params import BeamSearchParams

    beams = [int(x) for x in a.beams.split(",")]
    llm = LLM(model=a.model, dtype="bfloat16", gpu_memory_utilization=a.gpu_frac,
              max_model_len=1024, enforce_eager=True, disable_log_stats=True,
              max_logprobs=2 * max(beams) + 1)
    tok = llm.get_tokenizer()
    end_id = tok.convert_tokens_to_ids(a.end_token)
    assert isinstance(end_id, int) and end_id > 0, a.end_token
    # make vLLM's beam search terminate on the E02 boundary symbol, which is this model's only
    # stop symbol; without this it would only honour the base model's original EOS.
    tok.eos_token_id = end_id

    res = {"model": a.model, "tag": a.tag, "fmt": a.fmt, "impl": "vllm",
           "end_token": a.end_token, "end_id": end_id, "n": a.n, "beam": {}}
    prompt_ids = [tok(q, add_special_tokens=False)["input_ids"] for q in prompts]

    for b in beams:
        outs = llm.beam_search(
            [{"prompt_token_ids": ids} for ids in prompt_ids],
            BeamSearchParams(beam_width=b, max_tokens=a.max_new_tokens,
                             length_penalty=0.0, temperature=0.0))
        hyps = []
        for o, ids in zip(outs, prompt_ids):
            seq = o.sequences[0]
            # seq.tokens includes the prompt (vLLM sets text = decode(tokens)), so slice it off.
            # Post-processing must match src/e02_train.py:measure_behaviour EXACTLY --
            # decode(skip_special_tokens=True).strip(), NO newline truncation -- otherwise the
            # run-on channel is clipped and the cross-implementation comparison is meaningless.
            gen = seq.tokens[len(ids):]
            t = tok.decode(gen, skip_special_tokens=True)
            hyps.append(t.strip())
        empty = float(np.mean([len(h.strip()) == 0 for h in hyps]))
        lenr = float(np.mean([len(h.split()) for h in hyps]) / ref_len)
        bleu = M.corpus_bleu(hyps, [[rw[i], ra[i]] for i in range(len(hyps))])
        chrf = M.corpus_chrf(hyps, [[rw[i], ra[i]] for i in range(len(hyps))])
        res["beam"][str(b)] = {"bleu_multi": bleu, "chrf2": chrf,
                               "empty_rate": empty, "len_ratio": lenr}
        print(f"[vllm {a.tag}/{a.fmt}] beam {b:3d}: BLEU {bleu:6.2f} chrF2 {chrf:6.2f} "
              f"empty {100*empty:5.2f}% lenR {lenr:.3f}", flush=True)

    out = os.path.join(ROOT, "results", "e04", f"vllm_{a.tag}_{a.fmt}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
