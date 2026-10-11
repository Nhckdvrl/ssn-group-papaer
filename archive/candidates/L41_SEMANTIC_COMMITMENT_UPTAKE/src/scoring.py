"""
L41 neutral-belief scoring.

B(p) = log P("Yes" | prompt) - log P("No" | prompt)

Scored as the log-prob of the *answer token* immediately after the answer cue,
restricted to the two answer tokens (i.e. a signed log-odds, not a full
distribution).  Several query paraphrases may be averaged WITHIN proposition;
they are never independent units.
"""
import torch

MODEL_ID = "Qwen/Qwen3-8B-Base"
REVISION = "49e3418fbbbca6ecbdf9608b4d22e5a407081db4"

# ---------------------------------------------------------------- few-shot prefix
# Balanced 2-Yes / 2-No, everyday content, no facility/agent vocabulary,
# no implicative verbs, no negation.  Purpose: fix the answer format for a
# base (non-instruct) LM.
FEWSHOT = (
    "Question: Is the Pacific Ocean larger than the Atlantic Ocean?\n"
    "Answer: Yes\n\n"
    "Question: Is Lisbon the capital of Spain?\n"
    "Answer: No\n\n"
    "Question: Does water boil at 100 degrees Celsius at sea level?\n"
    "Answer: Yes\n\n"
    "Question: Is a decade one hundred years?\n"
    "Answer: No\n\n"
)

# Neutral query paraphrase family (frozen before E01-B).
# Each takes the proposition dict and returns the question string.
def q0(p): return f"Did {p['agent']} {p['complement']}?"
def q1(p): return f"Is it true that {p['agent']} {p['complement_past']}?"
def q2(p): return f"Did {p['agent']} in fact {p['complement']}?"
def q3(p): return f"According to the records, did {p['agent']} {p['complement']}?"

QUERY_FAMILY = [q0, q1, q2, q3]


def build_prompt(question, context=None, fewshot=True):
    s = FEWSHOT if fewshot else ""
    if context:
        s += f"Context: {context}\n"
    s += f"Question: {question}\nAnswer:"
    return s


class BeliefScorer:
    def __init__(self, model, tokenizer, device="cuda"):
        self.model, self.tok, self.device = model, tokenizer, device
        # answer tokens: leading space variant, as produced after "Answer:"
        self.yes_id = self._single(" Yes")
        self.no_id = self._single(" No")

    def _single(self, s):
        ids = self.tok.encode(s, add_special_tokens=False)
        assert len(ids) == 1, f"{s!r} -> {ids} (expected single token)"
        return ids[0]

    @torch.no_grad()
    def score_prompts(self, prompts, batch_size=32):
        """Return list of B = logP(Yes)-logP(No) at the next-token position."""
        out = []
        self.tok.padding_side = "left"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        for i in range(0, len(prompts), batch_size):
            chunk = prompts[i:i + batch_size]
            enc = self.tok(chunk, return_tensors="pt", padding=True,
                           add_special_tokens=False).to(self.device)
            logits = self.model(**enc).logits[:, -1, :].float()
            lp = torch.log_softmax(logits, dim=-1)
            out.extend((lp[:, self.yes_id] - lp[:, self.no_id]).tolist())
        return out

    def belief(self, props, context_fn=None, queries=QUERY_FAMILY,
               fewshot=True, batch_size=32):
        """Mean B over the query family, per proposition.

        context_fn(p) -> optional in-context sentence (forward semantic gate).
        Returns (mean_B, per_query_B) with per_query_B shape [n_props][n_queries].
        """
        prompts, index = [], []
        for pi, p in enumerate(props):
            ctx = context_fn(p) if context_fn else None
            for qi, qf in enumerate(queries):
                prompts.append(build_prompt(qf(p), ctx, fewshot))
                index.append((pi, qi))
        vals = self.score_prompts(prompts, batch_size)
        per = [[0.0] * len(queries) for _ in props]
        for (pi, qi), v in zip(index, vals):
            per[pi][qi] = v
        mean = [sum(r) / len(r) for r in per]
        return mean, per


def load_base(device="cuda", dtype=torch.bfloat16, model_id=MODEL_ID, revision=REVISION):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, revision=revision, dtype=dtype,
        attn_implementation="sdpa").to(device).eval()
    return model, tok
