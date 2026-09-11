# L19 — Data and gold contract (FROZEN before any training run)

## Why Natural Questions

The manipulation we need is: **hold the question, the answer, the answer-supporting
evidence, the source document and the example set fixed; vary only how much natural
context surrounds the evidence.** NQ is the one large corpus where all four are human
gold and come from the same artifact:

- a real Google user question;
- the full Wikipedia page it was asked against;
- a human-annotated **long answer** bounding box, defined by the NQ guidelines to contain
  all information needed to answer;
- a human-annotated **short answer** span inside it.

No LLM generates gold. No one has to decide "which sentences are relevant" — the NQ
annotator already did, and the relevance judgement is identical in both arms.

Source: `google-research-datasets/natural_questions`, config `default`, split `train`
(original HTML-token form, 307,373 examples, 287 parquet shards, 55.5 GB).
Extraction code: `src/nq_extract.py`. Audit: `scripts/audit_nq.py`.

## Pair construction

For one NQ training example we emit at most one pair:

| condition | context |
|---|---|
| `SHORT-SUPPORT` | the human-annotated long-answer paragraph, verbatim |
| `LONG-FULL` | the entire Wikipedia page that paragraph came from, verbatim |

Shared and identical across the two conditions: `id`, question text, gold short answer,
source document, and the supervised target string. The only difference is the natural
text surrounding the support.

## Inclusion filters (frozen)

1. annotation has a non-null long answer (`start_token >= 0`);
2. `yes_no_answer == -1` (extractive only);
3. exactly one short-answer span, non-empty;
4. the long-answer candidate begins with `<P>` — prose paragraphs only, no tables/lists/
   infoboxes, because those change the *kind* of supervision, not just its length;
5. the gold answer string occurs in the support paragraph (case-insensitive);
6. **length window**, in Llama-3 tokens: `len(support) <= 512` and
   `8000 <= len(page) <= 24000`.

HTML tokens are dropped (`is_html`); text is the whitespace join of the remaining tokens,
applied identically to both conditions.

## Length audit (3 shards, 3,213 raw examples, Llama-3 tokenizer)

Filters 1-5 keep **18.4%** (590/3213).

| | median | mean | p10 | p25 | p75 | p90 | max |
|---|---|---|---|---|---|---|---|
| support | 106 | 123 | 49 | 74 | 156 | 207 | 602 |
| page | 6,019 | 9,186 | 1,727 | 2,885 | 11,880 | 20,045 | 72,516 |

Adding filter 6 keeps **6.5%** of raw examples (210/3213), i.e. an expected ~20k pairs
from the full train split; we take the first 10,000 by shard order.

## Why this window, and why it is frozen now

Chosen to bracket the mother paper's own regime (their Appendix A Table 2: short arm
avg 568 / 1759 tokens; long arm avg 9358 / 9548 / 78716) while being cleanly separated:

```
SHORT-SUPPORT  median   106 tok   (p90 207, hard cap 512)
LONG-FULL      median ~11000 tok  (hard floor 8000, cap 24000)
```

That is a ~100x contrast, sharper than the mother's ~17x, with no synthetic padding.
The 24k cap is a memory decision, taken before seeing any outcome. The cutoffs are
recorded here and in `data/pairs_manifest.json`; they are not adjustable after results.

## Known selection effects (stated, not hidden)

- Requiring `page >= 8000` over-samples long Wikipedia pages, i.e. popular/high-traffic
  entities. Both arms inherit the same sample, so this cannot produce a between-arm
  difference; it bounds the population the claim generalises to.
- Requiring a prose `<P>` long answer removes the table/list questions that are a large
  part of NQ. Again identical in both arms.
- Requiring a single short-answer span removes multi-span and null-answer questions.
  This makes the supervised target unambiguous and identical across arms.
