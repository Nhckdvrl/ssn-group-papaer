"""Cache-level interventions for hybrid (Qwen3.5 GDN+attention) and pure-attention (Qwen3) models.

Conventions
-----------
history ids  h[0:N]  are prefilled once with a DynamicCache.
decision ids a[0:L]  are then run as ONE chunk on a (batch-replicated) copy of that cache,
with a custom 4D boolean attention mask (True = may attend) that only affects
full-attention layers. Recurrent (conv + GDN) state is whatever the cache holds.

Interventions on the decision chunk
  FULL      : all columns visible, recurrent state from the full history.
  KV-drop   : columns of span e_i hidden from the decision tokens (attention layers only);
              recurrent state untouched (it has already absorbed e_i).
  REC-swap  : recurrent/conv state replaced by the state of a prefill of history-without-e_i;
              attention KV from the full history (State-swap, Chen et al. 2609.04434 style).
"""
import copy
import torch


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
    """ids: 1D LongTensor on device. Returns cache after consuming ids."""
    from transformers import DynamicCache
    cache = DynamicCache(config=model.config)
    out = model(input_ids=ids[None], past_key_values=cache, use_cache=True, logits_to_keep=1)
    return out.past_key_values


def cache_len(cache):
    for l in cache.layers:
        if not is_linear_layer(l) and getattr(l, "keys", None) is not None and l.keys.numel():
            return l.keys.shape[-2]
    raise ValueError("no attention layer in cache")


def replicate(cache, B, rec_from=None):
    """Deep-copy `cache` into batch size B. If rec_from is a list of B caches (or None entries),
    the linear-layer states of row b are taken from rec_from[b] (State-swap)."""
    new = copy.copy(cache)
    new.layers = []
    for li, l in enumerate(cache.layers):
        nl = copy.copy(l)
        if is_linear_layer(l):
            cs = l.conv_states.expand(B, *l.conv_states.shape[1:]).clone()
            rs = l.recurrent_states.expand(B, *l.recurrent_states.shape[1:]).clone()
            if rec_from is not None:
                for b, src in enumerate(rec_from):
                    if src is not None:
                        cs[b] = src.layers[li].conv_states[0]
                        rs[b] = src.layers[li].recurrent_states[0]
            nl.conv_states, nl.recurrent_states = cs, rs
        else:
            nl.keys = l.keys.expand(B, *l.keys.shape[1:]).clone()
            nl.values = l.values.expand(B, *l.values.shape[1:]).clone()
        new.layers.append(nl)
    return new


SINK = 4  # attention-sink tokens are never hidden (StreamingLLM convention; Qwen3 relies on them)


def decision_mask(N, L, hide_spans, device):
    """hide_spans: list (len B) of lists of (start, end) history column ranges to hide.
    Returns bool mask (B,1,L,N+L), True = attend. Columns [0, SINK) always stay visible."""
    B = len(hide_spans)
    m = torch.ones(B, 1, L, N + L, dtype=torch.bool, device=device)
    tri = torch.tril(torch.ones(L, L, dtype=torch.bool, device=device))
    m[:, :, :, N:] = tri
    for b, spans in enumerate(hide_spans):
        for s, e in spans:
            m[b, :, :, max(s, SINK):e] = False
    return m


@torch.no_grad()
def decide(model, cache, N, dec_ids, hide_spans, rec_from=None):
    """Run decision tokens dec_ids (1D, len L) for B = len(hide_spans) variants.
    Returns float32 log-probs (B, L, V) at every decision position (predicting dec_ids[1:] and beyond)."""
    B, L = len(hide_spans), dec_ids.shape[0]
    c = replicate(cache, B, rec_from)
    mask = decision_mask(N, L, hide_spans, dec_ids.device)
    pos = torch.arange(N, N + L, device=dec_ids.device)[None].expand(B, L)
    out = model(input_ids=dec_ids[None].expand(B, L), attention_mask=mask, position_ids=pos,
                past_key_values=c, use_cache=True)
    return torch.log_softmax(out.logits.float(), -1)
