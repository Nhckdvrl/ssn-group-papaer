# L13 E08 — natural `before`-clause audit (2026-09-11)

Source: `NeelNanda/pile-10k`, 446,819 sentences scanned offline. Selection is by
surface form only (`scripts/extract_natural_before.py`); no model selects, rewrites or
labels anything. Sentences are verbatim; only the target proposition is authored.

## 1. What the corpus actually contains

| | count |
|---|---|
| sentences scanned | 446,819 |
| containing " before " | 4,615 |
| `before <NP> could/would <VP>` (modally marked) | 101 |

Non-veridical `before`-clauses in natural text are **usually lexically marked** with a
modal — *"He stopped talking to me before I could figure it out."* The unmarked case our
controlled set isolates is a minority construction.

## 2. External-validity result (E08) — mostly negative, reported as such

35 hand-adjudicated items (22 prevented, 13 veridical), plain-timeline task:

| model | prevented event listed as realized | veridical event listed |
|---|---|---|
| Llama-3.1-8B | **0.318** [0.14, 0.50] | 0.846 |
| Qwen3-8B | **0.182** [0.04, 0.36] | 0.769 |
| Gemma-3-12B | **0.136** [0.00, 0.27] | 0.692 |
| Qwen3-32B | **0.136** [0.00, 0.27] | 0.769 |

**On modally marked natural sentences the collapse largely does not occur** (0.14–0.32),
against 0.45–1.00 on the controlled unmarked items. Direct P(YES) on prevented items is
0.00–0.20, i.e. the models read these correctly.

The honest conclusion is a **boundary, not a replication**: the failure is specific to
the *unmarked, genuinely unresolved* `before`-clause. Where English supplies a lexical
cue (`could`), models use it. Llama-3.1-8B remains the exception at 0.32.

## 3. Prevalence of the affected construction

A random sample of 45 natural plain-past `before`-clauses was adjudicated by hand
(realized / unresolved / not-realized / not an event clause). Nine were not event
clauses (PP uses such as *"before the specified date"*, *"before the undersigned"*, or
corrupt text); six near-identical boilerplate sentences from one source were collapsed
to one.

| adjudication | n | share of adjudicable |
|---|---|---|
| realized | 26 | 84% |
| **unresolved** | 4 | **13%** |
| not realized | 1 | 3% |

So roughly **one natural `before`-clause in six** is not guaranteed by its sentence, and
about one in eight is genuinely open. The construction is a minority case, not a corner
case, and it is precisely the case without a lexical cue.

Two findings worth carrying into the paper:

1. The surface cue is **not** diagnostic in either direction. Plain past tense can still
   be prevented — *"He stopped me before I reached the third sentence."*,
   *"He caught me before I reached the trees."* — and these are included in the
   prevented set as `clause_cue: plain_past`.
2. The effect size ordering across models is preserved between the controlled and the
   natural set (Llama worst, Gemma/Qwen3-32B lowest), which is weak convergent evidence
   that the same mechanism is being measured.

## 4. Limitation

35 items, one corpus, author adjudication. This is a boundary probe, not a corpus study.
