# Stage lineage: when, and in what, the termination regime changes

**Status:** exploratory (E00-EXT). E00's verdict (HOLD) is unchanged; this line was opened to test
whether the candidate's ceiling is higher than "finding-level".
**Substrate:** the frozen `newstest2019` En→De substrate; 400 segments for the step-0 measurements,
200 for the beam cells.
**Instrument:** `src/termination.py` — "the translation ends here" is the full set of vocabulary
items whose surface form contains a line break (few-shot interface) or the end-of-turn/EOS ids
(chat interface), so the same quantity is measured across model families and interfaces.

---

## 0. How these results should and should not be stated (correction, 2026-09-14)

Two framings in the earlier version of this file were too strong and are corrected here.

**(a) The `rank_stop ≤ 2b` bound is not a finding.** HuggingFace beam search keeps the top `2b`
candidates at the first step, so an immediate-stop hypothesis *cannot* enter the beam unless its
token is in that set. The 393/393 result is a correctness check on the instrument, not a discovery.
What is actually worth reporting is the other half:

> training stage and generation format move the **stop-rank distribution by orders of magnitude**
> (rank 3 → 60030 across conditions of the same 7B lineage), and that distribution, measured before
> any search is run, **predicts out of sample the beam interval in which a previously unrun system
> opens its termination-collapse channel** (Olmo-3 base: `rank ≈ 532 ⇒ b* ≈ 266`; observed 0 % empty
> through beam 128, 8 % at beam 512).

**(b) The chat/few-shot rank gap is partly a stop-event cardinality artefact.** The few-shot stop
set is ~2179 tokens whose surface contains a line break; the chat stop set is a single end-of-turn
id. Some of the rank 3 vs rank 1222 gap therefore reflects "how many ways there are to end", not
learned geometry alone. This does not undermine the behavioural results — a real decoder does face
those different stopping contracts — but it does mean that a *weights × format* interaction claim
cannot be made from this table. Removing that confound requires training with a **single shared
boundary symbol in both formats**, which is what `E02_PREREGISTRATION.md` does.

## 1. The exposure check (instrument correctness, 393/393 events)

HuggingFace beam search keeps the top `2b` candidates at the first generated position. So the empty
hypothesis can only **enter** the beam when `rank_stop ≤ 2b`; whether it then **wins** is a separate
question decided by the margin.

Per-segment test on `facebook/wmt19-en-de`, RAW scoring, first 400 segments:

| beam | empty outputs | of which had `rank_stop ≤ 2b` | exposed segments | `P(empty | exposed)` |
|---|---|---|---|---|
| 4 | 0 | — | 2.8 % | 0 % |
| 16 | 14 | **100 %** | 7.2 % | 48.3 % |
| 32 | 15 | **100 %** | 18.5 % | 20.3 % |
| 64 | 35 | **100 %** | 67.0 % | 13.1 % |
| 128 | 135 | **100 %** | 90.5 % | 37.3 % |
| 512 | 194 | **100 %** | 98.2 % | 49.4 % |

**Not one collapse event in 393 violated the rank bound**, across beam widths spanning two orders of
magnitude — as it must be, since the bound is what the search algorithm enforces (see §0a). The
informative part is that exposure is necessary but not sufficient (the margin among exposed segments barely
differs between collapsing and surviving ones: 8.33 vs 8.91 nats), which is why the empty rate
tracks but never reaches the exposure rate.

This turns "modern models put less probability on stopping" into a quantity that **predicts the beam
width at which a given system breaks**.

## 2. Where the regime sits for each system

Step-0 measurements, 400 segments:

| system | interface | margin | `log p(stop)` | median `rank_stop` | greedy BLEU | empty @ b16 | empty @ b64 |
|---|---|---|---|---|---|---|---|
| `facebook/wmt19-en-de` (2019 NMT) | sentence | +9.09 | −9.57 | **106** | — | 5.4 % | 13.1 % |
| `Olmo-3-1025-7B` **base** | few-shot | +7.70 | −8.67 | **532** | 35.29 | 0 % | 0 % |
| `Olmo-3-7B-Instruct-SFT` | few-shot | +1.01 | −2.46 | **3** | 18.92 | 90.5 % | 92.5 % |
| `Olmo-3-7B-Instruct-DPO` | few-shot | +2.17 | −3.24 | **4** | 20.23 | 79.5 % | 82.0 % |
| `Olmo-3-7B-Instruct-SFT` | chat | +11.19 | −11.91 | **1222** | 30.39 | 0 % | (running) |
| `gemma-3-12b-it` | chat | — | −35.33 | (large) | 45.14 | 0 % | 0 % |

### 2b. The completed Olmo-3 lineage

| tag | stage | interface | margin | `log p(stop)` | median `rank_stop` | `b*` | BLEU@1 | BLEU@16 | BLEU@64 | empty@64 |
|---|---|---|---|---|---|---|---|---|---|---|
| `olmo3-rlvr` | RLVR | chat | +17.79 | −18.10 | **41025** | 20513 | 28.64 | 31.54 | **31.08** | **0.00 %** |
| `olmo3-sft` | SFT | chat | +11.19 | −11.91 | **1222** | 611 | 30.39 | 27.11 | 17.64 | 0.00 % |
| `olmo3-base` | base | few-shot | +7.70 | −8.67 | **532** | 267 | 35.29 | 36.74 | 22.20 | 0.00 % |
| `olmo3-dpo` | DPO | few-shot | +2.17 | −3.24 | **4** | 2 | 20.23 | 0.08 | 0.00 | 82.00 % |
| `olmo3-rlvr` | RLVR | few-shot | +1.76 | −2.91 | **3** | 2 | 18.16 | 0.02 | 0.00 | 84.50 % |
| `olmo3-sft` | SFT | few-shot | +1.01 | −2.46 | **3** | 2 | 18.92 | 0.00 | 0.00 | 92.50 % |
| `facebook/wmt19-en-de` | reference | NMT | +9.09 | −9.57 | **106** | 53 | — | — | — | 13.12 % |

In-format the boundary keeps moving outward along the lineage (SFT 1222 → RLVR **41025**), and
`olmo3-rlvr` in chat format is the one checkpoint here that is *fully* beam-robust: BLEU 28.64 →
31.08 from beam 1 to 64 with no empties and no degradation. Out of format every post-trained stage
sits at rank 3–4 and is destroyed by beam 16.

### 2c. Weights vs. format, decomposed — and why the decomposition is only half-clean

Measuring the **base** checkpoint through the **SFT sibling's chat template** (`--template-from`)
holds the prompt string fixed and varies only the weights:

| condition | weights | prompt string | median `rank_stop` |
|---|---|---|---|
| base, few-shot | base | few-shot | 532 |
| **base, chat template** | **base** | **chat** | **755** |
| SFT, chat | SFT | chat | 1222 |
| SFT, few-shot | SFT | few-shot | 3 |

Changing only the prompt string moves the boundary a little (532 → 755). Changing only the weights
at a fixed chat prompt moves it further (755 → 1222), and changing only the weights at a fixed
few-shot prompt moves it catastrophically in the *other* direction (532 → 3). So the weights carry
the change, and its **sign depends on whether the context matches the format the weights were
trained on**.

**Caveat, and it matters:** the base checkpoint cannot actually use the chat template — its
translation quality in that condition collapses (BLEU 1.05 at beam 16), so only the step-0
termination measurement is interpretable there, not its beam behaviour. Off-the-shelf checkpoints
cannot give a fully clean weights-vs-format factorisation, because format and weights are
co-adapted by construction. That is exactly the gap a controlled SFT with a
termination-supervision ablation would close.

## 3. What this says

**(a) ~~The jump is at SFT, and DPO barely moves it.~~ — CORRECTED 2026-09-15, did not replicate.**
A second lineage (Tülu-3, `results/stages/TULU3_REPLICATION.md`) shows **no jump at SFT**: in-format
base → SFT moves `rank_stop` 45 → 40. The Llama-3.1-8B base already sits at rank 45 and already
collapses (26.5 % empty at beam 64), whereas Olmo-3 base sits at rank 532 and does not. Which
training step moves a lineage into the dangerous regime is **lineage-specific**; what is stable
across both lineages is the format keying (claim b), the RLVR-outward effect, and the rank → onset
map. The original Olmo-3 observation is retained below as a description of *that* lineage only.

**(a-olmo3, descriptive only) Within Olmo-3, the jump is at SFT, and DPO barely moves it.** Under a fixed interface, `rank_stop` goes
532 → 3 from base to SFT, and 3 → 4 from SFT to DPO. Whatever reorganises termination is installed
in supervised fine-tuning.

**(b) The learned boundary is keyed to the format, not to the weights alone.** The *same* SFT
checkpoint has `rank_stop` 1222 inside its chat format and 3 outside it. So "modern LLM-MT has no
beam-search curse" is a statement about **weights × interface**, not about the LLM regime. Out of
format, a post-trained model is *far worse* than the 2019 system it supposedly superseded: it
collapses by beam 16, where the classic model needs beam 64.

**(c) It is dissociated from task competence.** Across the same step, greedy BLEU does not improve —
base few-shot 35.29, SFT chat 30.39. The boundary is learned without (here, slightly against) the
task capability that the same training is nominally about.

**(d) There is a second, separate damage channel.** `Olmo-3` base at beam 64 loses 14 BLEU with
**0 % empty outputs** and a normal length ratio (0.947): inspection shows generic high-probability
sentences ("Die Aussprache ist geschlossen.") and source copying — mode inadequacy in the sense of
Eikema & Aziz, not the termination pathology. The two channels must be reported separately; the
rank law governs only the termination one.

## 3b. Out-of-sample confirmation of the onset law (first half)

`RANK_ONSET_PREDICTION.md` predicted, before the runs, that `Olmo-3` base under the few-shot
interface (median `rank_stop` 532, so `b* = 266`) would stay **free of empty outputs at beam 128**,
at a width where the 2019 system is already at 40 % empty.

| system | beam 128 | empty % | length ratio |
|---|---|---|---|
| `facebook/wmt19-en-de` | BLEU 16.11 | **40.11 %** | 0.444 |
| `Olmo-3-1025-7B` base, few-shot | BLEU 16.17 | **0.00 %** | 0.948 |

Confirmed. Note both systems have lost most of their quality by beam 128 — but for entirely
different reasons: the classic model empties out and shortens to 0.44 of the reference length, while
the base LM keeps full-length outputs and degrades through the generic-hypothesis channel of §3(d).
Two systems, the same BLEU, two different pathologies — which is exactly why the termination channel
needs its own instrument rather than being read off a quality curve.

**Second half, also confirmed.** The same checkpoint at beam 512 (50-segment subset, `2b = 1024 ≥
532`) does start emptying out:

| beam | 1 | 16 | 64 | 128 | **512** |
|---|---|---|---|---|---|
| empty % | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| length ratio | 1.004 | 0.954 | 0.947 | 0.948 | **0.804** |
| BLEU | 35.29 | 36.74 | 22.20 | 16.17 | 8.39 |

The termination channel is silent for four beam widths spanning 1→128 and switches on between 128
and 512, bracketing the `b* = 266` predicted from a single step-0 measurement taken before any
search was run — on a model family and an interface different from the one the law was derived on.

## 4. What is still running / not yet done

- chat-interface beam-64 cells for SFT/DPO/RLVR, and the base model measured through its SFT
  sibling's chat template (`--template-from`), which is the clean way to hold the prompt string
  fixed while varying only the weights;
- the out-of-sample onset sweep on `Olmo-3` base few-shot (`rank_stop` 532 ⇒ `b* = 266`): predicted
  clean at 128 and collapsing by 512 (`RANK_ONSET_PREDICTION.md`);
- a second, independent lineage (Tülu-3 on Llama-3.1-8B: base → SFT → DPO → RLVR) as replication;
- the termination-supervision ablation, which is the step that would turn this from a
  learning-dynamics description into a mechanism claim.
