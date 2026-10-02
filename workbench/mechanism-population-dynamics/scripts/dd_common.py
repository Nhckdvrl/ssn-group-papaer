"""DataDecide (OLMo-v1 `hf_olmo` checkpoints) -> transformers LlamaForCausalLM, without installing ai2-olmo.

The DataDecide 1B config is Llama-equivalent: RMSNorm with affine, SwiGLU, RoPE (rotate-half), no biases,
untied output layer. Fused OLMo weights are split as in OLMo's own code:
  att_proj -> [q; k; v];  ff_proj -> [up; gate] with act = silu(gate) * up  (OLMo: `x, gate = x.chunk(2)`).
Sanity: verify_mapping() compares NLL against the alternative (swapped up/gate) mapping.
"""
import json
from pathlib import Path

import torch
from huggingface_hub import snapshot_download
from safetensors.torch import load_file
from transformers import LlamaConfig, LlamaForCausalLM, PreTrainedTokenizerFast

import mp_common as mc

SEEDS = ["default", "large-aux-2", "large-aux-3"]
FINAL_1B = 69369


def rev(step, seed):
    return f"step{step}-seed-{seed}"


def fetch(repo, revision):
    return Path(snapshot_download(repo, revision=revision, cache_dir=str(mc.HF_CACHE),
                                  allow_patterns=["*.json", "*.safetensors"]))


def load(repo, revision, dtype=torch.float32, swap_glu=False, device="cuda", attn="sdpa"):
    path = fetch(repo, revision)
    c = json.loads((path / "config.json").read_text())
    assert c["layer_norm_type"] == "rms" and c["activation_type"] == "swiglu" and c["rope"] and not c["alibi"]
    assert not c["include_bias"] and not c["weight_tying"] and c["block_type"] == "sequential"
    d, nl, nh = c["d_model"], c["n_layers"], c["n_heads"]
    hid = c["mlp_ratio"] * d // 2
    cfg = LlamaConfig(vocab_size=c["embedding_size"], hidden_size=d, intermediate_size=hid, num_hidden_layers=nl,
                      num_attention_heads=nh, num_key_value_heads=nh, max_position_embeddings=c["max_sequence_length"],
                      rms_norm_eps=c["layer_norm_eps"], rope_theta=c["rope_theta"], tie_word_embeddings=False,
                      attention_bias=False, mlp_bias=False, bos_token_id=None, eos_token_id=c["eos_token_id"],
                      pad_token_id=c["pad_token_id"], torch_dtype=dtype)
    cfg._attn_implementation = attn  # "eager" when attention weights are needed
    sd = {}
    for f in sorted(path.glob("*.safetensors")):
        sd.update(load_file(str(f)))
    pre = "model.transformer."
    out = {"model.embed_tokens.weight": sd[pre + "wte.weight"], "model.norm.weight": sd[pre + "ln_f.weight"],
           "lm_head.weight": sd[pre + "ff_out.weight"]}
    for i in range(nl):
        b, o = f"{pre}blocks.{i}.", f"model.layers.{i}."
        q, k, v = sd[b + "att_proj.weight"].split(d, 0)
        up, gate = sd[b + "ff_proj.weight"].split(hid, 0)
        if swap_glu:
            up, gate = gate, up
        out.update({o + "self_attn.q_proj.weight": q, o + "self_attn.k_proj.weight": k, o + "self_attn.v_proj.weight": v,
                    o + "self_attn.o_proj.weight": sd[b + "attn_out.weight"],
                    o + "mlp.up_proj.weight": up, o + "mlp.gate_proj.weight": gate,
                    o + "mlp.down_proj.weight": sd[b + "ff_out.weight"],
                    o + "input_layernorm.weight": sd[b + "attn_norm.weight"],
                    o + "post_attention_layernorm.weight": sd[b + "ff_norm.weight"]})
    src = {k for k in sd if not k.endswith("inv_freq")}
    assert len(src) == 3 + 6 * nl and len(out) == 3 + 9 * nl, (len(src), len(out))  # every source tensor consumed
    with torch.device("meta"):
        model = LlamaForCausalLM(cfg)
    model.load_state_dict({k: t.to(dtype) for k, t in out.items()}, assign=True, strict=True)
    model.model.rotary_emb = type(model.model.rotary_emb)(config=cfg)  # rebuild inv_freq buffer off meta
    tok = PreTrainedTokenizerFast(tokenizer_file=str(path / "tokenizer.json"), eos_token="<|endoftext|>",
                                  pad_token="<|padding|>")  # OLMoTokenizer class is not in transformers
    assert tok.eos_token_id == c["eos_token_id"] and tok.pad_token_id == c["pad_token_id"]
    return model.to(device).eval(), tok


@torch.no_grad()
def nll(model, tok, texts, max_len=512):
    tot, n = 0.0, 0
    for t in texts:
        ids = [tok.eos_token_id] + tok(t, add_special_tokens=False)["input_ids"][:max_len - 1]
        x = torch.tensor([ids], device=model.device)
        tot += float(model(x, labels=x).loss) * (len(ids) - 1)
        n += len(ids) - 1
    return tot / n


def verify_mapping(repo, revision, texts):
    a = nll(*load(repo, revision), texts)
    torch.cuda.empty_cache()
    b = nll(*load(repo, revision, swap_glu=True), texts)
    return {"nll": a, "nll_swapped_glu": b, "ok": a < 4.0 and a < b - 1.0}
