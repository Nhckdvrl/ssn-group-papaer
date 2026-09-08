# Literature and claim alignment — 2026-09-08

PDFs are locally in `papers/`, extracted text in `text/`. `sources_20260908.json`
and `manifest_20260908.json` retain source URLs, retrieval times and hashes.
PDFs are research reference copies excluded from Git; scripts can re-acquire them.
The entries below identify inspected sections, not a claim to exhaustive coverage.
No award labels are inferred from the inherited repository's descriptions.

| Paper | Sections inspected / already owned | Consequence for L02 |
|---|---|---|
| [Ruppenhofer et al., SemEval 2010](https://aclanthology.org/S10-1008/) | §§2–4, Table 1: interpretation, licensing, resolution, coreference equivalence and head/overlap scoring. | Owns the distinction and decomposition. E000 must reproduce these, not claim novelty. Train: 438 sentences, 303 DNI (245 resolved), 277 INI; test: 525, 349 (259), 361 are **published**, not yet reproduced counts. |
| [Petruck, DMR 2019](https://aclanthology.org/W19-3313/) | §§2–3: representation and semantic nature of implicit roles. | “Food” as an indefinite participant type is not automatically unsupported specific reference. FrameNet's CNI convention must not be mapped blindly to SemEval interpretation flags. |
| [Roit et al., ACL 2024](https://aclanthology.org/2024.acl-long.863/) | §§1–4: slot insertion plus textual entailment; excludes misplaced and unsupported candidate arguments. | Owns document-level evidence filtering, beyond-sentence inference and an explicit verification method. Our claim cannot be “checking grounding helps.” Need interpretation-conditioned error decomposition, and an entailment-style control if the later method claim warrants it. |
| [Sharif et al., EMNLP 2024: DiscourseEE](https://aclanthology.org/2024.emnlp-main.673/) | §§2,4–5, Fig.2, prompt appendix: natural health discourse, implicit/scattered generation; **null is already allowed**. | Corrects the inherited assertion that all its slots require recoverable fillers. Its null merges absence without a DNI/INI licensing distinction; evidence for finer independence must come from our separate expert gold. It uses serious open/closed models; a tiny-model failure is below this bar. |
| [Sharif et al., Findings EMNLP 2025: REGen](https://aclanthology.org/2025.findings-emnlp.649/) | Framework, limitations, Appendices A–B: context-grounded matching and specificity examples; precision/recall denominator discussion. | Owns context-grounded generative EAE evaluation including semantic matching errors. We cannot claim that grounded evaluation or rejecting over-specific answers is new. A novel consequence would concern selection decisions when licensing is measured independently, with no LLM judge defining our primary gold. |
| [Srikanth & Rudinger, NAACL 2025](https://aclanthology.org/2025.naacl-long.130/) | §§3–4, Table 1, limitations: atomic inferences, validation, full-vs-atomic consistency. | Similar scientific shape: aggregate success can mask a distinct inferential decision. Our decomposition is source-native instead of generated atoms, but merely observing disagreement is insufficient; H01–H03 need a modeling or selection consequence. |
| [Kasa et al., EMNLP 2025](https://aclanthology.org/2025.emnlp-main.486/) | Introduction, related work, comparison table, experiment setup: classical modeling choice revisited under transformers, data/size/calibration trade-offs. | Similar paper identity: establish where a classical intermediate choice matters. Their from-scratch setup controls pretraining; ours does not. A small prompt comparison cannot inherit their breadth or causal isolation. |

## Comparison against the external bar

| Dimension | External reference bar | L02 now | Assessment |
|---|---|---|---|
| Question scope | Roit/DiscourseEE: meaningful information beyond sentence/span boundaries. | Whether gains in implicit completion preserve what discourse licenses. | Worth investigating; do not reduce to label accuracy. |
| Data quality | Natural discourse; independent, documented annotation. | Expert pre-LLM SemEval flags and links; small domain. | Strong provenance in principle, acquisition and parser validation pending. |
| Pre-result tension | Kasa: competing paradigms can win in different regimes. | Internal licensing suffices vs explicit decision improves frontier beyond caution. | Both plausible; null is informative only with adequate precision. |
| Claim novelty | New relation or consequence, not just another error category. | H01 paired frontier; H02 evidence × licensing boundary; H03 changed selection. | Provisional; no result and no “first” assertion. |
| Identification | Controls isolate the scientific quantity. | Matched schema, equal evidence, compute control, prior baseline, visible-link coverage. | Designed, not yet executed. |
| Narrative | Independent, memorable scientific point. | More recovered content may differ from more licensed content. | Distinct candidate narrative; needs empirical support. |
| Breadth | Diverse documents/tasks where warranted. | One author, two works. | Major limitation; no general necessity or preservation claim from pilot. |

## Per-experiment alignment

- **E000 (data/gold audit)** → D01–D03; S10-1008 §§2–4 and Petruck §3.
  It tests feasibility, linkage integrity, and whether lexical priors exhaust the axis.
  Counts or passing software tests establish no model claim.
- **E001 (development pilot)** → H01 feasibility; DiscourseEE prompts,
  Roit's evidence check, Kasa's controlled model comparison. Primary quantity is
  licensed recovery jointly with INI commitment, not DNI/INI macro-F1 alone.
- **E002 (held-out comparison, planned)** → H01/H02; distinguish extra computation,
  order, explicit semantic decision, and generic caution. Natural context restrictions
  are diagnostic interventions on available evidence, not newly invented linguistic gold.
- **E003 (selection consequence, planned)** → H03; REGen and NAACL atomic NLI.
  Use the same outputs and fully specified selection rules. A numerical score change
  is not automatically a new scientific conclusion or a model ranking reversal.

## Search boundaries and unresolved collisions

Queries on 2026-09-08 included `generative implicit argument extraction referential
indefinite null instantiation 2025 2026`, `implicit argument abstain`, `event argument
unanswerable`, and `2026 null instantiation`, alongside targeted retrieval of the
papers above. Search was noisy (argument mining often means premises/claims rather
than semantic roles). No exact full-story collision was located; this is **not proof
of novelty**. Preserve uncertainty rather than marking the gate unconditionally YES.

Further collision leads before full experiments: QA-based EAE answerability;
selective prediction/risk-coverage in IE; referential ambiguity; entailment-based
verification; modern FrameNet parsing. A finding that prior work already measures
the same licensing-conditioned frontier would require revising the narrative, not
simply substituting another dataset. Source accessibility problems alone do not
scientifically refute the research question.
