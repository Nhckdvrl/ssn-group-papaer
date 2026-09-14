# Stage lineage: when, and in what, the termination regime changes

**Status:** exploratory (E00-EXT). E00's verdict (HOLD) is unchanged; this line was opened to test
whether the candidate's ceiling is higher than "finding-level".
**Substrate:** the frozen `newstest2019` En→De substrate; 400 segments for the step-0 measurements,
200 for the beam cells.
**Instrument:** `src/termination.py` — "the translation ends here" is the full set of vocabulary
items whose surface form contains a line break (few-shot interface) or the end-of-turn/EOS ids
(chat interface), so the same quantity is measured across model families and interfaces.

---

## 1. The exposure law (confirmed, 393/393 events)

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
magnitude. Exposure is necessary; it is not sufficient (the margin among exposed segments barely
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

## 3. What this says

**(a) The jump is at SFT, and DPO barely moves it.** Under a fixed interface, `rank_stop` goes
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

## 4. What is still running / not yet done

- chat-interface beam-64 cells for SFT/DPO/RLVR, and the base model measured through its SFT
  sibling's chat template (`--template-from`), which is the clean way to hold the prompt string
  fixed while varying only the weights;
- the out-of-sample onset sweep on `Olmo-3` base few-shot (`rank_stop` 532 ⇒ `b* = 266`): predicted
  clean at 128 and collapsing by 512 (`RANK_ONSET_PREDICTION.md`);
- a second, independent lineage (Tülu-3 on Llama-3.1-8B: base → SFT → DPO → RLVR) as replication;
- the termination-supervision ablation, which is the step that would turn this from a
  learning-dynamics description into a mechanism claim.
