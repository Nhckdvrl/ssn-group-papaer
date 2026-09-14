"""Frozen metric implementations for L36.

`sacrebleu` is not present in the frozen `verl-clean` environment and the repo compute policy
forbids installing packages, so BLEU and chrF2 are implemented here to sacrebleu's specification:

- BLEU: `13a` tokenizer, case-sensitive, max order 4, `exp` smoothing, closest-reference brevity
  penalty, multi-reference via max n-gram counts.
- chrF2: char order 6, word order 0, beta 2, whitespace removed, micro-averaged over the corpus,
  multi-reference via best-per-segment F score.

Validated against the upstream sacrebleu source (run from a scratch checkout, not installed);
see `results/e00/metric_validation.json`.
"""

import math
import re
from collections import Counter

# --- 13a tokenizer (mteval-v13a) ------------------------------------------------------------

_13A_SUBS = [
    (re.compile(r"<skipped>"), ""),
    (re.compile(r"-\n"), ""),
    (re.compile(r"\n"), " "),
]
_PUNCT = re.compile(r"([\{-\~\[-\` -\&\(-\+\:-\@\/])")
_PERIOD_COMMA_PRECEDING = re.compile(r"([^0-9])([\.,])")
_PERIOD_COMMA_FOLLOWING = re.compile(r"([\.,])([^0-9])")
_DASH_PRECEDED_BY_DIGIT = re.compile(r"([0-9])(-)")
_WS = re.compile(r"\s+")


def tokenize_13a(line: str) -> str:
    line = line.rstrip()
    for pattern, repl in _13A_SUBS:
        line = pattern.sub(repl, line)
    line = line.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    line = " " + line + " "
    line = _PUNCT.sub(r" \1 ", line)
    line = _PERIOD_COMMA_PRECEDING.sub(r"\1 \2 ", line)
    line = _PERIOD_COMMA_FOLLOWING.sub(r" \1 \2", line)
    line = _DASH_PRECEDED_BY_DIGIT.sub(r"\1 \2 ", line)
    return _WS.sub(" ", line).strip()


# --- BLEU -----------------------------------------------------------------------------------

MAX_ORDER = 4


def _ngrams(tokens, order):
    return Counter(tuple(tokens[i:i + order]) for i in range(len(tokens) - order + 1))


def bleu_segment_stats(hyp: str, refs):
    """Return [hyp_len, ref_len, correct_1..4, total_1..4] for one segment (multi-reference)."""
    h = tokenize_13a(hyp).split()
    rs = [tokenize_13a(r).split() for r in refs]
    hyp_len = len(h)
    # closest reference length, ties broken towards the shorter reference (sacrebleu behaviour)
    ref_len = min((len(r) for r in rs), key=lambda x: (abs(x - hyp_len), x))
    correct = [0] * MAX_ORDER
    total = [0] * MAX_ORDER
    for n in range(1, MAX_ORDER + 1):
        hyp_ng = _ngrams(h, n)
        if not hyp_ng:
            continue
        max_ref = Counter()
        for r in rs:
            for ng, c in _ngrams(r, n).items():
                if c > max_ref[ng]:
                    max_ref[ng] = c
        total[n - 1] = sum(hyp_ng.values())
        correct[n - 1] = sum(min(c, max_ref[ng]) for ng, c in hyp_ng.items())
    return [hyp_len, ref_len] + correct + total


def bleu_from_stats(stats):
    """Corpus BLEU (0-100) from summed segment statistics."""
    hyp_len, ref_len = stats[0], stats[1]
    correct, total = stats[2:2 + MAX_ORDER], stats[2 + MAX_ORDER:2 + 2 * MAX_ORDER]
    if hyp_len == 0:
        return 0.0
    smooth_mteval = 1.0
    precisions = []
    for n in range(MAX_ORDER):
        if total[n] == 0:
            precisions.append(0.0)
            continue
        if correct[n] == 0:
            smooth_mteval *= 2
            precisions.append(100.0 / (smooth_mteval * total[n]))
        else:
            precisions.append(100.0 * correct[n] / total[n])
    if min(precisions) <= 0:
        return 0.0
    if hyp_len < ref_len:
        bp = math.exp(1 - ref_len / hyp_len) if hyp_len > 0 else 0.0
    else:
        bp = 1.0
    return bp * math.exp(sum(math.log(p) for p in precisions) / MAX_ORDER)


def corpus_bleu(hyps, refs_list):
    """hyps: list[str]; refs_list: list[list[str]] (references per segment)."""
    agg = [0] * (2 + 2 * MAX_ORDER)
    for hyp, refs in zip(hyps, refs_list):
        st = bleu_segment_stats(hyp, refs)
        agg = [a + b for a, b in zip(agg, st)]
    return bleu_from_stats(agg)


# --- chrF2 ----------------------------------------------------------------------------------

CHAR_ORDER = 6
BETA = 2.0
_WS_STRIP = re.compile(r"\s+")


def _char_ngrams(text, order):
    return Counter(text[i:i + order] for i in range(len(text) - order + 1))


def chrf_segment_stats(hyp: str, refs):
    """Return the per-order [n_hyp, n_ref, n_match] triples for the best-scoring reference."""
    h = _WS_STRIP.sub("", hyp)
    best, best_score = None, -1.0
    for ref in refs:
        r = _WS_STRIP.sub("", ref)
        stats = []
        for n in range(1, CHAR_ORDER + 1):
            hn, rn = _char_ngrams(h, n), _char_ngrams(r, n)
            match = sum(min(c, rn[ng]) for ng, c in hn.items())
            stats.extend([sum(hn.values()), sum(rn.values()), match])
        score = chrf_from_stats(stats)
        if score > best_score:
            best, best_score = stats, score
    return best


def chrf_from_stats(stats):
    """chrF2 (0-100) from summed statistics; orders with no n-grams on either side are skipped."""
    eps = 1e-16
    factor = BETA ** 2
    avg_prec, avg_rec, effective_order = 0.0, 0.0, 0
    for i in range(CHAR_ORDER):
        n_hyp, n_ref, n_match = stats[3 * i:3 * i + 3]
        if n_hyp == 0 and n_ref == 0:
            continue
        prec = n_match / n_hyp if n_hyp > 0 else eps
        rec = n_match / n_ref if n_ref > 0 else eps
        avg_prec += prec
        avg_rec += rec
        effective_order += 1
    if effective_order == 0:
        return 0.0
    avg_prec /= effective_order
    avg_rec /= effective_order
    if avg_prec + avg_rec < eps:
        return 0.0
    return 100 * (1 + factor) * avg_prec * avg_rec / (factor * avg_prec + avg_rec)


def corpus_chrf(hyps, refs_list):
    agg = [0] * (3 * CHAR_ORDER)
    for hyp, refs in zip(hyps, refs_list):
        st = chrf_segment_stats(hyp, refs)
        agg = [a + b for a, b in zip(agg, st)]
    return chrf_from_stats(agg)


def sentence_chrf(hyp, refs):
    return chrf_from_stats(chrf_segment_stats(hyp, refs))
