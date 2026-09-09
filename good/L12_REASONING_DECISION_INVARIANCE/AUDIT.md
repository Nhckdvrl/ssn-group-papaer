# L12 Parent, Stimulus, and Checkpoint Audit

**Date:** 2026-09-09

## Parent Artifacts

- Paper: ACL 2026 Outstanding, Appendix B.3-B.4 supplies prompt blocks and three base prospects.
- Author repository: `Yongyan-Zhang/mind-the-dh-gap`, commit `986bc17` at audit.
- Public data contain aggregate choice rates/counts, not raw prompts, individual generations, seeds, or API request records.
- The local provenance manifest records commit and SHA-256 hashes.

Therefore “exact reproduction” means exact published stimulus template/factorial reconstruction plus count-level audit; byte-identical original requests cannot be established from released artifacts.

## Checkpoint Relationship

Official OLMo 3 model cards identify the common base as `allenai/Olmo-3-1025-7B` and list `Olmo-3-7B-Instruct-SFT` and `Olmo-3-7B-Think-SFT` as sibling SFT branches. Exact audited revisions are in `configs/pilot.json`.

The ACL paper Appendix C.1 contains a contradictory sentence saying Instruct-SFT is initialized from Think-SFT. This is inconsistent with the official cards and cannot support a sequential claim. All project inference uses `(base -> Instruct-SFT)` versus `(base -> Think-SFT)`.

## Stimulus and Statistical Contract

- Unit: matched base prospect crossed with sign frame and displayed order.
- Three prospects are transcribed from Appendix B.4.
- Primary prompt: explicit prospect + no explanation + choice block, transcribed from Appendix B.3.
- Twenty samples per cell match the parent's approximate trial count.
- Invalid outputs are retained and reported; they are missing only from conditional choice metrics.
- Only three base prospects exist, so prospect-level confidence intervals are intrinsically wide. Trial-level precision must not be misrepresented as stimulus generalization.

## Public-Data Audit Result

Across all three prompt styles and three prospects (nine matched cells), published aggregate frame consistency is:

- Instruct-SFT: 0.843, matched-cell bootstrap 95% CI [0.751, 0.913].
- Think-SFT: 0.965, matched-cell bootstrap 95% CI [0.938, 0.991].

Raw summary: `results/parent_audit/summary.json`. This confirms the parent branch contrast but is not new mechanism evidence.

## Generated-Behavior Validity

- The common base generated unrelated pretraining-style multiple-choice continuations. Apparent A/B string matches are not task responses, so base generated behavior is marked non-identifiable.
- Normal Think-SFT answers are accepted only after a generated closing `</think>`. Raising the cap from 512 to 1,024 tokens yields 219/240 valid final answers.
- The 512-token loose-parser run and 32-token injected-end run are archived as invalid and never enter formal summaries.
- Injecting `</think>` did not produce a no-reasoning mode. This operation is not used as causal evidence.
