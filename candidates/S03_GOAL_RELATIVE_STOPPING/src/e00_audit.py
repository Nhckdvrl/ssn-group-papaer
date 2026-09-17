"""
S03 Step 0 — implementation-fact audit for the OLMo lineages.

Purpose: before any scientific run, verify the facts S03 relies on:
  1. checkpoint lineage identity (same tokenizer/vocab/architecture/shape);
  2. what token actually terminates an assistant turn under the chat template;
  3. tie_word_embeddings is False AND the weight objects really do not share storage;
  4. the stop output row can be isolated (lm_head row for the stop token);
  5. generation_config stopping criteria (single vs multiple EOS ids, stop_strings).

Any mismatch here is an implementation confound, not a scientific result.
"""
import json
import os
import sys
import hashlib

import torch
from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM

OLMO2_1B = [
    ("base", "allenai/OLMo-2-0425-1B"),
    ("sft", "allenai/OLMo-2-0425-1B-SFT"),
    ("dpo", "allenai/OLMo-2-0425-1B-DPO"),
    ("instruct", "allenai/OLMo-2-0425-1B-Instruct"),
]
OLMO3_7B = [
    ("base", "allenai/Olmo-3-1025-7B"),
    ("sft", "allenai/Olmo-3-7B-Instruct-SFT"),
    ("dpo", "allenai/Olmo-3-7B-Instruct-DPO"),
    ("instruct", "allenai/Olmo-3-7B-Instruct"),
]

PROBE_MESSAGES = [
    {"role": "user", "content": "List the first 3 planets from the Sun."},
    {"role": "assistant", "content": "Mercury\nVenus\nEarth"},
]


def audit_tokenizer(name, repo, out):
    tok = AutoTokenizer.from_pretrained(repo)
    cfg = AutoConfig.from_pretrained(repo)
    rec = {
        "stage": name,
        "repo": repo,
        "architectures": cfg.architectures,
        "vocab_size_config": cfg.vocab_size,
        "tokenizer_len": len(tok),
        "tie_word_embeddings": getattr(cfg, "tie_word_embeddings", None),
        "config_eos_token_id": cfg.eos_token_id,
        "config_pad_token_id": cfg.pad_token_id,
        "tok_eos_token": tok.eos_token,
        "tok_eos_token_id": tok.eos_token_id,
        "tok_pad_token": tok.pad_token,
        "tok_pad_token_id": tok.pad_token_id,
        "has_chat_template": tok.chat_template is not None,
    }
    # generation config
    gc_path = None
    try:
        from transformers import GenerationConfig
        gc = GenerationConfig.from_pretrained(repo)
        rec["gen_eos_token_id"] = gc.eos_token_id
        rec["gen_pad_token_id"] = gc.pad_token_id
        rec["gen_stop_strings"] = getattr(gc, "stop_strings", None)
    except Exception as e:  # pragma: no cover
        rec["gen_config_error"] = repr(e)

    # what actually terminates the assistant turn
    if tok.chat_template is not None:
        rendered = tok.apply_chat_template(PROBE_MESSAGES, tokenize=False)
        ids = tok.apply_chat_template(PROBE_MESSAGES, tokenize=True)
        rec["rendered_full"] = rendered
        rec["tail_ids"] = ids[-8:]
        rec["tail_tokens"] = [tok.convert_ids_to_tokens(i) if i < len(tok) else str(i) for i in ids[-8:]]
        # generation prompt form
        gen_prompt = tok.apply_chat_template(PROBE_MESSAGES[:1], tokenize=False, add_generation_prompt=True)
        rec["gen_prompt"] = gen_prompt
        gen_ids = tok.apply_chat_template(PROBE_MESSAGES[:1], tokenize=True, add_generation_prompt=True)
        rec["gen_prompt_tail_tokens"] = [tok.convert_ids_to_tokens(i) for i in gen_ids[-6:]]
        # how many times does a stop-ish token appear at the end
        stop_ids = set()
        for t in ["<|endoftext|>", "<|im_end|>"]:
            tid = tok.convert_tokens_to_ids(t)
            if tid is not None and tid >= 0:
                stop_ids.add((t, tid))
        rec["stop_candidate_ids"] = sorted(stop_ids, key=lambda x: x[1])
        rec["tail_stop_counts"] = {
            t: sum(1 for i in ids if i == tid) for t, tid in stop_ids
        }
    out.append(rec)
    return rec


def audit_weights(name, repo, out_rec):
    """Load on CPU (meta-free) and check embedding tying + lm_head row isolation."""
    model = AutoModelForCausalLM.from_pretrained(repo, torch_dtype=torch.float32, device_map="cpu")
    emb = model.get_input_embeddings().weight
    head = model.get_output_embeddings().weight
    out_rec["shared_storage"] = emb.data_ptr() == head.data_ptr()
    out_rec["emb_shape"] = list(emb.shape)
    out_rec["head_shape"] = list(head.shape)
    out_rec["head_has_bias"] = model.get_output_embeddings().bias is not None
    out_rec["lm_head_param_name"] = [n for n, p in model.named_parameters() if p is head][0]
    # fingerprint the stop rows so we can later verify freezes
    for tname in ["<|endoftext|>", "<|im_end|>"]:
        tok = AutoTokenizer.from_pretrained(repo)
        tid = tok.convert_tokens_to_ids(tname)
        if tid is None or tid < 0 or tid >= head.shape[0]:
            continue
        row = head[tid].detach()
        out_rec[f"head_row_{tname}_norm"] = float(row.norm())
        out_rec[f"head_row_{tname}_sha"] = hashlib.sha1(row.numpy().tobytes()).hexdigest()[:16]
    del model
    return out_rec


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "olmo2"
    heavy = "--weights" in sys.argv
    lineage = {"olmo2": OLMO2_1B, "olmo3": OLMO3_7B}[which]
    out = []
    for name, repo in lineage:
        try:
            rec = audit_tokenizer(name, repo, out)
            if heavy:
                audit_weights(name, repo, rec)
            print(f"[ok] {name} {repo}", flush=True)
        except Exception as e:
            print(f"[FAIL] {name} {repo}: {e!r}", flush=True)
            out.append({"stage": name, "repo": repo, "error": repr(e)})
    os.makedirs("results/e00", exist_ok=True)
    path = f"results/e00/audit_{which}.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", path)

    # console summary of the load-bearing facts
    print("\n=== load-bearing facts ===")
    for r in out:
        if "error" in r:
            continue
        print(f"\n-- {r['stage']} --")
        print("  tie_word_embeddings :", r.get("tie_word_embeddings"),
              "| shared_storage:", r.get("shared_storage", "n/a"))
        print("  config eos          :", r.get("config_eos_token_id"))
        print("  generation eos      :", r.get("gen_eos_token_id"))
        print("  chat template       :", r.get("has_chat_template"))
        if r.get("tail_tokens"):
            print("  assistant turn tail :", r["tail_tokens"])
            print("  stop token counts   :", r.get("tail_stop_counts"))


if __name__ == "__main__":
    main()
