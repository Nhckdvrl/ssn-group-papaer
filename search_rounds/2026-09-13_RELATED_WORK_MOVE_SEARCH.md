# 2026-09-13 — Related-Work-Move Search

## Search mode

This round deliberately simplifies topic generation. Instead of starting from a large checklist or from a method, read strong ACL / EMNLP / NAACL papers backward:

> prior work already establishes A -> paper notices one strange/important B -> paper asks only the next missing sentence.

The target is a **minimal consequential increment**, not a synthetic combination of multiple literatures.

Operationally:

1. read Main / Best / Outstanding papers for the source of the question;
2. identify one stable odd result, inherited assumption, or unresolved sentence;
3. trace only the closest 3–5 predecessors/successors;
4. ask whether the missing sentence is already naturally entailed;
5. if yes, kill immediately; if no, only then do full Selection.

This keeps the search high-throughput. The old Selection gates still apply before compute, but they are not used to manufacture rough hooks.

---

## Surviving result from this mode

### L32 — Where Do 18 Embeddings Work?

Status: **PILOT-AUTHORIZED — E01 ONLY**.

Mother: NAACL 2025 KS-Lottery shows that tuning only 18 LLaMA token-embedding rows can recover near-full multilingual translation tuning performance.

Minimal missing sentence:

> When those few frequent token embeddings carry the adaptation, does their useful effect enter through instruction/source prefill, through generated-target feedback, or through cross-phase reuse?

The decisive E01 uses one trained sparse-embedding model and gates the same learned embedding deltas by segment at inference, avoiding cross-training confounds. The full Selection record is stored separately in this repository.

---

## Dead hook A — Corrective rationales hurt ICL: why?

Origin: EMNLP 2025 **No Need for Explanations: LLMs can implicitly learn from mistakes in-context**.

Stable result: adding explicit corrective rationales to wrong+correct demonstration pairs often hurts math reasoning relative to showing wrong+correct answers without rationales. The paper interprets this as rationales over-constraining the model, supported by greater output similarity to exemplar rationales.

Tempting next question:

> Is the harm caused by trajectory imitation, semantic over-specification, or generic context interference?

Why not promoted:

- the parent already makes the explanatory object central and performs length/diversity/overfitting analyses;
- ACL 2024 and EMNLP 2024 learning-from-mistakes work already studies negative examples, prompting and tuning, and explicit error information;
- the natural follow-up quickly becomes another fine-grained prompt/rationale ablation inside a crowded self-correction / contrastive-ICL parent;
- strongest reviewer compression: `contrastive negative demonstrations are known to help + rationale-augmented ICL is known to be sensitive + EMNLP 2025 already shows rationale imitation/over-constraint`.

Verdict: **DROP for current portfolio.** Do not reopen merely as paraphrased-vs-original rationale, concise-vs-long rationale, or another prompt-format study.

---

## Dead hook B — Why do unfamiliar fine-tuning examples determine hallucination defaults?

Origin: NAACL 2025 **Unfamiliar Finetuning Examples Control How Language Models Hallucinate**.

Stable result: as test inputs become unfamiliar, predictions move toward the response distribution attached to unfamiliar fine-tuning examples; changing supervision on those examples changes the model's default behavior on unfamiliar queries.

Tempting mechanism:

> unfamiliar examples dominate because they induce larger / more diffuse gradients and therefore receive disproportionate effective update weight.

Why not promoted:

- familiarity-vs-gradient magnitude is already a natural optimization consequence and 2026 work directly reports gradient/update magnitude decaying as data becomes familiar;
- equalizing gradient magnitude would be a clean experiment but the strongest positive result reviewer-compresses to `high-loss unfamiliar examples make larger updates, so they dominate the learned fallback`;
- this is too close to component composition rather than a new Main-level inference unless an independent residual contradiction appears after matching update magnitude.

Verdict: **DROP in current form.**

---

## Dead hook C — Why can smaller models be diversity teachers for larger models?

Origin: EMNLP 2025 **Diverse, not Short**.

Stable side result: OLMo-2-7B can provide preference data that improves diversity of larger variants.

Why not promoted:

The phenomenon is currently one secondary result inside a diversity-alignment/data-selection paper. The obvious account—smaller models have a broader / less aligned output distribution, providing more diverse candidate responses—is already close to the paper's setup and is not yet an independent stable mother across sources. Making it a paper would first require rediscovering/establishing the mother, violating the current preference against betting on a side cell.

Verdict: **DROP.**

---

## Dead hook D — Corrective rationales help tuning but hurt in-context learning

Potential tension:

- EMNLP 2024 reports that mistake-correction data and explicit explanations/reasons contribute under fine-tuning.
- EMNLP 2025 reports that explicit corrective rationales hurt relative to implicit wrong+correct demonstrations in ICL.

Why not promoted yet:

ACL 2024 already studies learning from mistakes from both prompting and model-tuning perspectives, and the two results are not yet a SAME-QUANTITY contradiction under matched data/model/evaluation. A matched `adaptation channel × explicit-rationale` 2×2 would first need to establish that the sign reversal survives exact controls; otherwise the paper is betting on a reconstructed reversal.

Verdict: **NO CURRENT AUTHORIZATION.** Do not report as a found topic unless a strong matched mother or independent replication appears.

---

## Calibration lessons from strong papers

Two useful exemplars from award papers:

- ACL 2026 Best Paper on local attention: prior work already observed that a restriction introduced for efficiency can improve quality; the paper asks the one missing `why` and supplies a formal expressivity account.
- EMNLP 2025 Outstanding on generative vs discriminative classification: it takes a classical 1975 empirical/theoretical law and asks whether the same two-regime trade-off survives modern Transformer architectures.

Both support the current search doctrine:

> **A strong idea often comes from one inherited statement whose next sentence has never been properly answered.**

Do not confuse sophistication of the experiment with sophistication of the question.
