# 2026-09-14 Broad-Search Kill Batch — K234–K236

**Purpose:** anti-resurrection registry for training-convention pressure pools.  
**Prior round registry:** `failed/2026-09-14_SEARCH_KILL_BATCH_K232_K233.md`.  
**Rule:** changing the downstream behavior, model family, language, or training scale does not reopen a killed convention-level parent.

---

| ID | killed parent | primary failure | shortest kill / anti-resurrection boundary |
|---|---|---|---|
| **K234** | Assistant-response-only loss / chat-role loss masking as an unexamined cause of post-training behavior | NOVELTY_PARENT_COLLISION | Shi et al. 2024, *Instruction Tuning With Loss Over Instructions*, already reverses the standard convention by training on instruction/prompt tokens and analyzes when it helps. Chatterjee et al., TACL 2025, *On the Effect of Instruction Tuning Loss on Generalization*, systematically varies prompt-vs-response loss weights across model families/datasets and shows conventional response-only loss can hurt prompt robustness and even lower prompt-token likelihood. Thus the convention itself and its generalization consequences are already direct research objects. Do not reopen by attaching a new behavioral dependent variable (syntax, production preference, style, etc.) unless an independent scientific law first predicts a qualitatively different effect. |
| **K235** | Document packing / cross-document attention / boundary masking as an unexamined cause of LLM capabilities | NOVELTY_PARENT_COLLISION / CROWDED_PARENT | Prato et al. 2025, *Effect of Document Packing on the Latent Multi-Hop Reasoning Capabilities of Large Language Models*, directly asks whether packing has capability effects beyond compute efficiency and ablates packing amount, repacking, document order, batch size, and cross-document attention. EXACT (Zhu et al. 2026) further shows that document masking changes the distribution of effective-context supervision in long-context adaptation. ICLR-2026 work such as ULTRALLADA also compares intra-document masking, EOD concatenation, and direct concatenation. Generic “packing is not scientifically neutral” is therefore occupied. Reopen only if a separately motivated scientific law is shown to have been specifically confounded by packing, not by studying another packing outcome. |
| **K236** | Tokenization as a supposedly harmless preprocessing convention whose general capability effects remain unstudied | CROWDED_PARENT / NOVELTY_PARENT_COLLISION | 2025–2026 work already treats tokenization as a causal scientific variable: morphology-aware tokenization, phonological representation limits, semantic corruption from token boundaries, language-variation sensitivity, tokenization gauge-symmetry breaking, and compute-optimal tokenization scaling laws. “Tokenization changes what LMs learn” is no longer a parent question. Do not reopen with another language/phenomenon. Only a separately established scientific law whose inference is demonstrably reversed by the token unit could create a new parent. |

---

## Round-level lesson

Training conventions can indeed become scientific variables, but by 2026 several obvious conventions are already explicit research programs. A viable changed-convention paper must begin from an independently important law or theory and show that the convention changes the law's load-bearing causal interpretation; merely measuring another downstream consequence of the convention is residual.

**Next kill ID:** K237.
