# 2026-09-13 — Related-Work Provenance Search

## Why this round changed the search procedure

The previous search had accumulated too many front-loaded gates and was becoming poor at high-volume idea generation. This round intentionally separates **discovery** from **selection** more sharply.

Discovery rule for this round:

> **Read a strong paper → identify the strangest / most load-bearing sentence in its result or motivation → trace the 3–5 closest predecessors → ask what single important sentence is still missing → kill immediately if the answer is already implied.**

Do not start by inventing a mechanism taxonomy, benchmark, or full C1/C2/C3 plan. Full selection still applies **after** a genuinely natural question survives.

### What public research-advice sources reinforced

Useful common advice from NLP/research reading guides and research-taste notes:

- broad reading should prioritize **motivation and problem**, not method details;
- Related Work is a compact history of why the new paper had to exist;
- extract the paper's question, prior limitation, key insight, and basic solution before reading implementation detail;
- build a field coordinate system rather than hoarding keyword-matched papers;
- generate many candidate ideas cheaply and get fast criticism instead of emotionally committing to each one.

Sources sampled in this round include:

- Alyssa Hwang, *How to Read a Research Paper*: https://alyssahwang.com/research-tips/how-to-read-a-research-paper
- PRADA Lab Research Handbook, *Tips on how to find research ideas*: https://kaustpradalab.github.io/research-handboook/tips-about-how-to-find-ideas.html
- Bojie Li, *如何培养 Research Taste？*: https://01.me/2024/04/research-taste/
- colah, *Research Taste Exercises*: https://colah.github.io/notes/taste/
- Zhihu, *科研论文如何想到不错的 idea？*: https://zhuanlan.zhihu.com/p/7365588776

The useful part of the Zhihu-style “挑刺” advice is active criticism and fast extraction of the unresolved sentence. The dangerous part is mechanically combining two weaknesses; that produces the bridge/synthesis style that is easy to generate and easy to reviewer-compress.

## Strong-paper provenance patterns sampled

This round re-read award / high-signal ACL-family papers not primarily for their methods, but for the **small move from related work to the paper question**. Reusable moves included:

1. **Known restriction unexpectedly helps → ask why the restriction improves computation.**
   - Example shape: local attention was introduced as an efficiency restriction, yet can improve quality; the strong paper asks what this means for expressivity rather than proposing another attention variant.

2. **Mature debate + weak evidence → replace observational evidence with a decisive causal test.**
   - Example shape: CoT faithfulness was already heavily studied; novelty came from changing what evidence could support the causal claim.

3. **Classic empirical trade-off → ask whether the same law survives a new model regime.**
   - Example shape: generative-vs-discriminative learning is old; the paper is about whether the old sample-efficiency story still holds for pretrained Transformers.

4. **A paper reports a striking side fact while solving another problem → follow only the side fact's missing sentence.**
   - This is the main generator used below.

5. **Formal or mechanistic explanation follows a simple behavioral anomaly.**
   - Strong papers often have a simple title-level question and complicated analysis, not a complicated question produced by the analysis method.

## Rapid kills from this provenance-first pass

These were investigated enough to avoid rediscovery, but are **not** promoted candidates.

### Hook P1 — Retokenization robustness

**Question attempted:** why can models tolerate strongly non-canonical tokenization / resegmentation?

**DROP.** 2026 successor work already identifies an early detokenization computation in which attention transports subword information and MLPs compose word-level representations, across multiple models. A new project would mostly connect an established robustness phenotype to an already-localized circuit.

### Hook P2 — Token cramming / parallel token reconstruction

**Question attempted:** why can an LM reconstruct or carry several tokens through one hidden slot, and is this semantic compression?

**DROP.** 2026 mechanistic follow-up shows the phenomenon is brittle steering rather than generic semantic compression and performs early-layer causal localization. Parent plus successor already own the natural explanation.

### Hook P3 — Fine-tuning vs ICL sensitivity to arbitrary token labels

**Question attempted:** why does fine-tuning tolerate / exploit arbitrary label-token mappings differently from in-context learning?

**DROP.** Symbol Tuning and the random-label / mapping-vs-format ICL literature already own the key inference. Exact modern-model comparisons would be another cell rather than a new scientific object.

### Hook P4 — Partially incorrect demonstrations can still help ICL

**Question attempted:** why do demonstrations with wrong answers sometimes preserve substantial ICL benefit?

**DROP.** The missing inference compresses to the established decomposition between label semantics, input-label mapping, format, and task recognition. Without a new same-quantity contradiction this is too crowded.

### Hook P5 — Off-policy SFT produces self/other entropy separation

**Question attempted:** why can a model distinguish its own continuations after post-training even when the adaptation data are off-policy?

**DROP FOR NOW.** The current strongest formulation is too close to own-policy likelihood / surprisal plus entropy-coupling explanations, and no selective discriminator yet yields a stronger inference than those components.

### Hook P6 — Super-additive cross-lingual transfer

**Question attempted:** why can fine-tuning on another language outperform fine-tuning on the target language itself?

**DROP FOR CURRENT ROUND.** The phenotype is interesting but language data, tokenizer support, pretraining exposure, optimization, and representation geometry are entangled; no affordable selective E01 was found. Do not convert it into a broad multilingual-data survey.

## Surviving lead handed to full Selection

### L32 seed — Where do ultra-sparse tuned token embeddings act?

Mother paper:

- Yuan et al., NAACL 2025, *KS-Lottery: Finding Certified Lottery Tickets for Multilingual Transfer in Large Language Models*: https://aclanthology.org/2025.naacl-long.458/

Stable mother:

- LLaMA-7B baseline translation average is ~4.6 spBLEU in the reported four-language table;
- tuning only a tiny selected set of token embeddings reaches ~27.9 average, comparable to embedding/full tuning;
- in en→ca, the strict set contains only **18 token embeddings** and reaches 37.7 spBLEU;
- winners are predominantly high-frequency tokens; directly tuning high-frequency tokens nearly matches embedding tuning;
- ordinary Prefix Tuning is substantially weaker (17.4 average vs 27.9 for Partial Tuning), so the phenomenon is not already explained by “a few trainable prompt vectors are enough.”

Plain-language missing sentence:

> **When only a handful of frequent input-token embeddings learn the translation task, where does their causal effect enter the decoder-only computation: while reading the instruction/source, or when generated target tokens are fed back autoregressively?**

Why this is a natural next question rather than a synthesized new object:

- KS-Lottery establishes the sparse phenomenon and names frequency, but does not distinguish the positions/segments at which the tuned rows matter.
- LLaMA's input embedding and LM head are untied (`tie_word_embeddings=False`), so the selected rows cannot directly change output logits; they matter only when those token IDs are read as inputs.
- In decoder-only translation the same embedding row can be read in qualitatively different roles: instruction/source prefill vs generated-target history.
- Existing decoder-only MT work establishes that source/target interaction matters, but does not identify the causal channel of ultra-sparse embedding adaptation.

This lead is sent to a separate full Selection record. Do not call it actionable unless that record ends in an explicit bounded `PILOT-AUTHORIZED — E01 ONLY`.