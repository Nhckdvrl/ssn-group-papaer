# L32 — Claim Novelty Delta (post-E01)

Written per `RESEARCH_EXECUTION.md` §8. E01 passed its gate and answered its
question, but the answer moved the paper identity, so the previous authorization
has expired. This is a **selection request, not an execution plan**.

---

## 1. Old statement

> When only a handful of frequent token embeddings learn a translation task,
> where does their causal effect enter a decoder-only LM: the task/source
> prefill, generated-target feedback, or both?

## 2. New statement

> A "certified multilingual winning ticket" is not a capability locus. The 18
> rows recover full-fine-tuning translation scores because they occur in the
> **fixed prompt template** and install a **prefill-time stopping policy**. The
> ticket is a function of the prompt, not of the language.

## 3. Evidence (E01, `notes/E01_REPORT.md`, 3 seeds, 1012 Flores sentences)

| | |
|---|---|
| `Δ_ALL` raw (gate ≥ +15) | **+29.50** [+28.59, +30.46] — replicates the parent |
| `Δ_ALL` first-line scoring | **+1.72** [+1.03, +2.42] — 94% of the headline is termination |
| recovery, INSTRUCTION only | **1.00** [0.98, 1.02] |
| recovery, SOURCE only | **−0.00** [−0.01, 0.01] — despite *more* tuned-token occurrences than the instruction (7.73 vs 7.00 per sentence) |
| recovery, TARGET feedback only | 0.05 [−0.01, 0.09] |
| norm-matched random delta, same rows/positions | spBLEU **0.05** |
| `Δ_raw` under a paraphrased instruction | **+3.19** (seeds +7.40 / +2.60 / −0.42) vs +29.18 trained template |

Selection's accounts A (source interface), B (autoregressive feedback) and D
(joint access) are rejected. Account C (task-prefix) holds at recovery 1.00.

## 4. Closest owners — honest accounting

| work | what it owns | why it does not own this |
|---|---|---|
| **Yuan et al., NAACL 2025 (KS-Lottery)** | the phenomenon, the KS certification, the frequency observation | the target of the reinterpretation. No termination-controlled baseline, no channel localization, no template manipulation. No public code (`github.com/CONE-MT/KS-Lottery` is 404), no published prompt. |
| **Hewitt et al. 2024** | "much of instruction tuning is a simple output-distribution change", incl. an EOS rule | about instruction tuning broadly, not sparse tickets, and not about *where along the sequence* an update acts |
| **Min et al. 2022; Kung & Peng ACL 2023** | the genre: a celebrated result's mechanism is not what it seems | different phenomena (ICL demonstrations; instruction quality) |
| **Li & Liang 2021 (Prefix-Tuning)** | a few learned vectors can condition a frozen LM | the parent used a weaker Prefix-Tuning baseline to *reject* the prompt reading; our result explains that gap rather than repeating it |
| **TS-PEFT (2511.16147)** | token-level gating of PEFT updates | training-time sparsity for efficiency; not an inference-time causal localization by semantic segment. **This does weaken the methodological-novelty leg — the technique is not new, the use is.** |

No existing critique or replication of KS-Lottery was found.

## 5. Strongest reviewer compression

> "The baseline wasn't truncated, and a delta trained under one fixed prompt
> overfits that prompt. Both are known failure modes. This is a replication
> note, not a paper."

## 6. What survives that compression — and what does not

**Does not survive.** "Base LLMs over-generate, so truncate MT output" is
practitioner common knowledge. "Prompt-tuned things are prompt-dependent" is
common knowledge. Position-gated updates already exist as a technique.

**Survives.** The SOURCE/INSTRUCTION dissociation is an intervention result that
no amount of "it overfits the prompt" predicts quantitatively: 25% of all source
tokens carry the tuned rows, with *more* occurrences than the instruction span,
and they recover **exactly zero** (CI width 0.02). The same rows, in the same
sequence, at different positions, do opposite things. That says a sparse
embedding update is a **constant-context state setter** — it buys nothing when
it lands on variable content — which is a mechanism statement, not a caveat.

## 7. Honest verdict on level

**E01 as it stands is Findings-level, not Main-level.** It is a well-controlled
correction plus localization of one result in one language pair on one model. The
genre (Min et al., Kung & Peng) reaches Main only when the correction generalizes
into a law about the method class rather than one paper's number.

The missing piece is one testable law, and it is cheap:

> **The certified ticket is a function of the prompt template, not of the
> language.**

The parent's own Table 11 reports that winning tickets overlap across languages
and reads this as a shared multilingual subspace. Every one of their languages
shares the same English prompt, so template-commonality and language-commonality
are perfectly confounded. The dissociation:

`overlap(same template, different language)` **vs** `overlap(same language, different template)`

- our account predicts the first ≫ the second;
- the parent's account predicts the reverse, or at least no template effect.

If tickets track the template, "certified winning ticket" is certified with
respect to an unreported prompt, and the parent's central interpretation — and
its cross-language evidence — collapses. That is a Main-level claim about a
method class, not a complaint about a number.

## 8. Status

Running now as the decisive test (4 selection runs: ca/explicit, ca/paraphrase,
es/explicit, de/explicit — full embedding tuning at the parent's 2e-5 / 3 epochs,
then per-row KS). **Disclosed as started without fresh Selection authorization**,
on the grounds that it is bounded (~1 GPU-hour on otherwise idle cards), uses no
new infrastructure, and its outcome determines whether this candidate is worth
any further compute at all. It can be stopped at any point.

Pre-declared kill condition: if `overlap(ca/explicit, ca/paraphrase)` is
comparable to `overlap(ca/explicit, es/explicit)`, the template account of ticket
*selection* is wrong, the Main-level path closes, and L32 is written up as a
Findings-level correction or archived.

## 9. Requested verdict

`PASS` to a bounded C2 built on §7, or `NO-GO` if the whole line is judged too
close to a replication note to survive review even with the localization result.

**Recommendation: conditional PASS** — PASS if the §7 dissociation holds, and
Findings-or-archive if it does not. Stated plainly so it is not the L30 mistake
again: **without §7 this is not a Main paper, and I would not argue for one.**
