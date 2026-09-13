"""Shared pieces for L32 E01.

The scientific object is *where* a fixed, already-learned sparse embedding
update is causally accessible in a decoder-only LM. Everything here exists to
make that gating exact:

  * the 18 en->ca winning-ticket rows are the only trainable parameters;
  * they are held as a separate fp32 delta, never written into the frozen
    embedding matrix, so "base row" and "tuned row" both remain available at
    every position at inference time;
  * inputs_embeds is assembled by hand, so a per-position gate decides which of
    the two rows is read.
"""
import json
import pathlib

import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Yuan et al., NAACL 2025 (KS-Lottery), Table 5: the en->ca winning ticket.
# LLaMA-1 32k vocab ids. Do not reorder -- delta row k is SEL_IDS[k].
SEL_IDS = [13, 263, 278, 297, 304, 310, 322, 338, 376,
           393, 411, 29871, 29889, 29892, 29896, 29900, 29901, 29949]

# The parent does not publish a prompt template. This one is frozen here and
# used identically by every arm and every seed, so the channel contrast is
# unaffected by the choice.
INSTR_HEAD = "Translate the following sentence from English to Catalan.\nEnglish:"
INSTR_TAIL = "\nCatalan:"

# Segment codes stored per position.
# INSTR is split so that "does the effect come from the cue adjacent to
# generation?" can be separated from "does it come from the task sentence?".
# ARMS["INSTRUCTION"] still covers both, so arms run before the split remain
# directly comparable.
SEG_INSTR, SEG_SOURCE, SEG_TARGET, SEG_INSTR_TAIL = 0, 1, 2, 3

# Which segments see the tuned rows in each arm.
ARMS = {
    "BASE": (),
    "ALL": (SEG_INSTR, SEG_INSTR_TAIL, SEG_SOURCE, SEG_TARGET),
    "INSTRUCTION": (SEG_INSTR, SEG_INSTR_TAIL),
    "INSTR_HEAD": (SEG_INSTR,),
    "INSTR_TAIL": (SEG_INSTR_TAIL,),
    "SOURCE": (SEG_SOURCE,),
    "PREFILL": (SEG_INSTR, SEG_INSTR_TAIL, SEG_SOURCE),
    "TARGET": (SEG_TARGET,),
}


def build_prompt(tok, src):
    """Tokenize the prompt and return (ids, segments).

    Segments are derived from prefix tokenizations and checked for prefix
    consistency, so an instruction/source boundary is never guessed.
    """
    a = tok.encode(INSTR_HEAD, add_special_tokens=False)
    ab = tok.encode(INSTR_HEAD + " " + src, add_special_tokens=False)
    abc = tok.encode(INSTR_HEAD + " " + src + INSTR_TAIL, add_special_tokens=False)
    if ab[: len(a)] != a or abc[: len(ab)] != ab:
        return None, None  # non-prefix-consistent tokenization; caller drops it
    seg = ([SEG_INSTR] * len(a) + [SEG_SOURCE] * (len(ab) - len(a))
           + [SEG_INSTR_TAIL] * (len(abc) - len(ab)))
    ids = [tok.bos_token_id] + abc
    seg = [SEG_INSTR] + seg
    return ids, seg


def build_target(tok, tgt, eos_id):
    return tok.encode(" " + tgt, add_special_tokens=False) + [eos_id]


class SparseDelta(torch.nn.Module):
    """The only trainable object: an (18, d) fp32 delta over selected rows."""

    def __init__(self, hidden, n=len(SEL_IDS), device="cuda"):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.zeros(n, hidden, dtype=torch.float32, device=device))
        sel = torch.full((32000,), -1, dtype=torch.long, device=device)
        for k, t in enumerate(SEL_IDS):
            sel[t] = k
        self.register_buffer("row_of_token", sel, persistent=False)

    def forward(self, embed_base, input_ids, gate):
        """embed_base: (B,L,d) frozen rows. gate: (B,L) bool -- tuned row here?"""
        k = self.row_of_token[input_ids]            # (B,L), -1 where not selected
        hit = (k >= 0) & gate
        d = self.weight[k.clamp(min=0)]             # (B,L,d)
        return embed_base + torch.where(hit.unsqueeze(-1), d.to(embed_base.dtype), 0)


def gate_for(segments, arm):
    """segments: (B,L) long. Returns (B,L) bool."""
    allowed = ARMS[arm]
    if not allowed:
        return torch.zeros_like(segments, dtype=torch.bool)
    g = torch.zeros_like(segments, dtype=torch.bool)
    for s in allowed:
        g |= segments == s
    return g


def load_backbone(path, device="cuda", dtype=torch.bfloat16):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(path, dtype=dtype, device_map=device)
    model.config.use_cache = True
    assert model.config.vocab_size == 32000, model.config.vocab_size
    assert not model.config.tie_word_embeddings, "untied head is load-bearing for the design"
    for p in model.parameters():
        p.requires_grad_(False)
    return model, tok


def read_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]
