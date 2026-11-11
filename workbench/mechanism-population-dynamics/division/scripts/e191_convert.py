"""E191 (card: division/experiments/E191-flame-early-trajectory-decomposition.md): FLAME-MoE Megatron torch_dist
checkpoint (model tensors fetched by e191_fetch.py) -> transformers Qwen2MoeForCausalLM.
Mapping (Megatron-core names, TP = PP = 1):
  embedding.word_embeddings -> model.embed_tokens; output_layer -> lm_head; decoder.final_layernorm -> model.norm
  layer l: self_attention.linear_qkv.layer_norm_weight -> input_layernorm
           linear_qkv.weight [ng*(q+k+v)*hd, h], per head group interleaved [q_h; k_h; v_h] (MHA: ng = heads) -> q/k/v_proj
           linear_proj -> o_proj
  dense layer 0: mlp.linear_fc1.layer_norm_weight -> post_attention_layernorm; fc1 = [gate; up] -> gate_proj/up_proj; fc2 -> down
  MoE layer: pre_mlp_layernorm -> post_attention_layernorm; mlp.router -> mlp.gate;
             experts.experts.linear_fc1 [E, 2f, h] = [gate; up] per expert; linear_fc2 [E, h, f]
             shared_experts.linear_fc1/fc2 -> shared_expert (no gate in Megatron: output added as is) ->
             shared_expert_gate weight = 0 (sigmoid = .5) and shared down_proj x 2 (exact in bf16).
Router: Megatron pre-softmax softmax over 64 then top-k, no renormalisation == Qwen2Moe softmax -> topk, norm_topk_prob=False.
Ablation flags (positive control (a3) only): qkv_blocks (wrong layout [Q;K;V] blocks), swap_gateup, no_shared."""
import argparse, json, os, sys, time
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e191_fetch import patch_pickle, PM  # noqa: E402


def load_megatron(d):
    patch_pickle()
    import torch.distributed.checkpoint as dcp
    from torch.distributed.checkpoint import FileSystemReader
    from torch.distributed.checkpoint.metadata import TensorStorageMetadata
    r = FileSystemReader(d); md = r.read_metadata()
    sd = {k: torch.empty(m.size, dtype=m.properties.dtype) for k, m in md.state_dict_metadata.items()
          if isinstance(m, TensorStorageMetadata) and not k.startswith("chained_")}
    dcp.load(sd, storage_reader=r, no_dist=True)
    args = vars(torch.load(os.path.join(d, "common.pt"), map_location="cpu", weights_only=False, pickle_module=PM)["args"])
    return sd, args


def make_config(a):
    from transformers import Qwen2MoeConfig
    assert a["num_query_groups"] == a["num_attention_heads"] and a["normalization"] == "RMSNorm" and a["swiglu"]
    assert a["moe_router_score_function"] == "softmax" and a["moe_router_pre_softmax"] and not a["add_bias_linear"]
    assert not a["qk_layernorm"] and a["untie_embeddings_and_output_weights"] and a["position_embedding_type"] == "rope"
    assert a["rotary_percent"] == 1.0 and not a["rotary_interleaved"] and not a["moe_router_enable_expert_bias"]
    freq = a["moe_layer_freq"]
    return Qwen2MoeConfig(
        vocab_size=a["padded_vocab_size"], hidden_size=a["hidden_size"], intermediate_size=a["ffn_hidden_size"],
        num_hidden_layers=a["num_layers"], num_attention_heads=a["num_attention_heads"],
        num_key_value_heads=a["num_query_groups"], hidden_act="silu", max_position_embeddings=a["seq_length"],
        rms_norm_eps=a["norm_epsilon"], tie_word_embeddings=False, rope_theta=a["rotary_base"], use_sliding_window=False,
        decoder_sparse_step=1, moe_intermediate_size=a["moe_ffn_hidden_size"],
        shared_expert_intermediate_size=a["moe_shared_expert_intermediate_size"], num_experts_per_tok=a["moe_router_topk"],
        num_experts=a["num_experts"], norm_topk_prob=False, output_router_logits=False, qkv_bias=False,
        mlp_only_layers=[i for i, f in enumerate(freq) if f == 0], torch_dtype="bfloat16")


def convert(d, qkv_blocks=False, swap_gateup=False, no_shared=False):
    sd, a = load_megatron(d)
    cfg = make_config(a)
    H, nh = cfg.hidden_size, cfg.num_attention_heads; hd = H // nh
    out = {"model.embed_tokens.weight": sd["embedding.word_embeddings.weight"],
           "lm_head.weight": sd["output_layer.weight"], "model.norm.weight": sd["decoder.final_layernorm.weight"]}

    def gu(w, f):
        g, u = w[:f], w[f:]
        return (u, g) if swap_gateup else (g, u)
    for l in range(cfg.num_hidden_layers):
        m, o = f"decoder.layers.{l}.", f"model.layers.{l}."
        out[o + "input_layernorm.weight"] = sd[m + "self_attention.linear_qkv.layer_norm_weight"]
        qkv = sd[m + "self_attention.linear_qkv.weight"]
        if qkv_blocks:
            q, k, v = qkv.split(H, 0)
        else:
            t = qkv.view(nh, 3, hd, H); q, k, v = (t[:, i].reshape(H, H) for i in range(3))
        out[o + "self_attn.q_proj.weight"], out[o + "self_attn.k_proj.weight"], out[o + "self_attn.v_proj.weight"] = q, k, v
        out[o + "self_attn.o_proj.weight"] = sd[m + "self_attention.linear_proj.weight"]
        if l in cfg.mlp_only_layers:
            out[o + "post_attention_layernorm.weight"] = sd[m + "mlp.linear_fc1.layer_norm_weight"]
            g, u = gu(sd[m + "mlp.linear_fc1.weight"], cfg.intermediate_size)
            out[o + "mlp.gate_proj.weight"], out[o + "mlp.up_proj.weight"] = g, u
            out[o + "mlp.down_proj.weight"] = sd[m + "mlp.linear_fc2.weight"]
            continue
        out[o + "post_attention_layernorm.weight"] = sd[m + "pre_mlp_layernorm.weight"]
        out[o + "mlp.gate.weight"] = sd[m + "mlp.router.weight"]
        f = cfg.moe_intermediate_size
        W1, W2 = sd[m + "mlp.experts.experts.linear_fc1.weight"], sd[m + "mlp.experts.experts.linear_fc2.weight"]
        for e in range(cfg.num_experts):
            g, u = gu(W1[e], f)
            out[o + f"mlp.experts.{e}.gate_proj.weight"], out[o + f"mlp.experts.{e}.up_proj.weight"] = g, u
            out[o + f"mlp.experts.{e}.down_proj.weight"] = W2[e]
        fs = cfg.shared_expert_intermediate_size
        g, u = gu(sd[m + "mlp.shared_experts.linear_fc1.weight"], fs)
        out[o + "mlp.shared_expert.gate_proj.weight"], out[o + "mlp.shared_expert.up_proj.weight"] = g, u
        out[o + "mlp.shared_expert.down_proj.weight"] = sd[m + "mlp.shared_experts.linear_fc2.weight"] * (0 if no_shared else 2)
        out[o + "mlp.shared_expert_gate.weight"] = torch.zeros(1, H, dtype=torch.bfloat16)
    out = {k: v.contiguous().to(torch.bfloat16) for k, v in out.items()}
    return cfg, out, a


def build_model(cfg, sdict, device="cuda"):
    from transformers import Qwen2MoeForCausalLM
    torch.set_default_dtype(torch.bfloat16)
    with torch.device(device):
        model = Qwen2MoeForCausalLM(cfg)
    torch.set_default_dtype(torch.float32)
    model.load_state_dict(sdict, strict=True)
    model = model.to(dtype=torch.bfloat16).eval()
    model.model.rotary_emb = type(model.model.rotary_emb)(config=cfg, device=device)   # inv_freq kept in fp32
    return model


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dcp", required=True); ap.add_argument("--out", required=True)
    x = ap.parse_args(); t0 = time.time()
    cfg, sdict, a = convert(x.dcp)
    os.makedirs(x.out, exist_ok=True)
    from safetensors.torch import save_file
    save_file(sdict, os.path.join(x.out, "model.safetensors")); cfg.save_pretrained(x.out)
    json.dump({"iteration": int(os.path.basename(x.dcp.rstrip("/")).split("_")[-1]), "tokens": None,
               "global_batch_size": a["global_batch_size"], "seq_length": a["seq_length"],
               "consumed_train_samples": a.get("consumed_train_samples")}, open(os.path.join(x.out, "_flame.json"), "w"))
    print(f"[{time.time() - t0:.0f}s] converted {x.dcp} -> {x.out}", flush=True)
