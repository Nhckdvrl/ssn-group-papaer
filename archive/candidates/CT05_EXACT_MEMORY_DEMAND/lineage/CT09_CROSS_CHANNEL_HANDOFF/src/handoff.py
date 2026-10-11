"""Cache surgery for the CT09 handoff test on Qwen3.5 (GDN + full attention).

A row of a batch is built from two prefilled contexts:
  kv_src  -> attention KV of every full-attention layer
  rec_src -> conv + recurrent state of every GDN layer (State-swap, 2609.04434 style)
All contexts in a batch have the same token length N, so positions line up.

Then two chunks run on the stacked cache, each with its own per-row 4D mask (True = attend):
  query chunk (len Lq): q_drop hides context columns [SINK, N)
  probe chunk (len Lp): p_drop hides every earlier column [SINK, N + Lq), i.e. the context KV
                        and the query-local KV; only the recurrent state carries the past.
Columns [0, SINK) are the same template tokens in every context, so keeping them carries no
A/B information.
"""
import copy
import torch

SINK = 4


def load(model_path, dtype=torch.bfloat16, device="cuda"):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, dtype=dtype, attn_implementation="sdpa", device_map=device)
    model.eval()
    return tok, model


def is_linear_layer(layer):
    return hasattr(layer, "recurrent_states")


@torch.no_grad()
def prefill(model, ids):
    from transformers import DynamicCache
    cache = DynamicCache(config=model.config)
    model(input_ids=ids[None], past_key_values=cache, use_cache=True, logits_to_keep=1)
    return cache


def stack(kv_srcs, rec_srcs):
    """New batch cache: row b takes attention KV from kv_srcs[b], GDN state from rec_srcs[b]."""
    new = copy.copy(kv_srcs[0])
    new.layers = []
    for li, l in enumerate(kv_srcs[0].layers):
        nl = copy.copy(l)
        if is_linear_layer(l):
            nl.conv_states = torch.cat([c.layers[li].conv_states for c in rec_srcs]).clone()
            nl.recurrent_states = torch.cat([c.layers[li].recurrent_states for c in rec_srcs]).clone()
        else:
            nl.keys = torch.cat([c.layers[li].keys for c in kv_srcs]).clone()
            nl.values = torch.cat([c.layers[li].values for c in kv_srcs]).clone()
        new.layers.append(nl)
    return new


def chunk_mask(prev, L, drop, device):
    """drop: list[bool] per row. Hide columns [SINK, prev) for dropped rows."""
    B = len(drop)
    m = torch.ones(B, 1, L, prev + L, dtype=torch.bool, device=device)
    m[:, :, :, prev:] = torch.tril(torch.ones(L, L, dtype=torch.bool, device=device))
    for b, d in enumerate(drop):
        if d:
            m[b, :, :, SINK:prev] = False
    return m


@torch.no_grad()
def run_rows(model, N, kv_srcs, rec_srcs, q_ids, q_drop, p_ids, p_drop, n_score):
    """q_ids (Lq,), p_ids (B, Lp) — probe tokens followed by the scored value tokens.
    Returns (B,) summed log-prob of the last n_score tokens of each p_ids row."""
    B, Lq, Lp = len(kv_srcs), q_ids.shape[0], p_ids.shape[1]
    dev = q_ids.device
    c = stack(kv_srcs, rec_srcs)
    pos = torch.arange(N, N + Lq, device=dev)[None].expand(B, Lq)
    model(input_ids=q_ids[None].expand(B, Lq), attention_mask=chunk_mask(N, Lq, q_drop, dev),
          position_ids=pos, past_key_values=c, use_cache=True, logits_to_keep=1)
    pos = torch.arange(N + Lq, N + Lq + Lp, device=dev)[None].expand(B, Lp)
    out = model(input_ids=p_ids, attention_mask=chunk_mask(N + Lq, Lp, p_drop, dev),
                position_ids=pos, past_key_values=c, use_cache=True,
                logits_to_keep=n_score + 1)
    lp = torch.log_softmax(out.logits[:, :-1].float(), -1)          # predicts last n_score tokens
    tgt = p_ids[:, -n_score:]
    return lp.gather(-1, tgt[..., None])[..., 0].sum(-1)
