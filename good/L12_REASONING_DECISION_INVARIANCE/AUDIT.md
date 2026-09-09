# L12 Parent, Stimulus, and Checkpoint Audit

**Date:** 2026-09-10

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

## Independent-Decision Expansion

E10 adds 36 base decisions generated before model scoring from a frozen factorial over payoff scale, relative EV gap, and probability gap. The audit verifies:

- 12 near, 12 medium, and 12 far EV-gap units;
- 12 units at each payoff scale;
- 18 narrow- and 18 wide-probability-gap units;
- 18 gain-optimal A and 18 gain-optimal B units;
- no ties, dominance, exact duplicates, or affine-equivalent units.

The base decision is the inferential unit. E11 selected 18 decisions before state substitution, one from every factorial cell, with alternating gold direction.

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
- E10 generated 576 continuations per sibling branch. Instruct-SFT validity was 1.000; Think-SFT validity was 0.875 at the 1,024-token cap. Exactly one of 144 Think cells had no valid completion, leaving 35/36 decisions analyzable for behavioral frame consistency and all 36 represented in matched trajectory control.
- E10 valid stripped traces all had a terminal conclusion removed, retained no decision marker, and retained 45.0% of original characters on average.

## DPO Checkpoint Axis

Official Hugging Face metadata identifies exact continuations and revisions:

- `Instruct-SFT -> Instruct-DPO`: `b33130b7de49f0c2553b5c2b3bc8409ff3e627d1`
- `Think-SFT -> Think-DPO`: `7b18bf927b430ff06376fdfa5610eb3b1b6a5c38`

Both exact safetensors snapshots were subsequently cached outside the repository and E12 completed. Each branch produced 888 factorial score rows over the same 36 base decisions and frozen E10 trajectory pairs. The Think-minus-Instruct DPO control difference is +0.472 [0.401, 0.555], positive for every decision. Model weights remain external cache artifacts.

## Qwen3 Same-Weight Route Audit

- Model: `Qwen/Qwen3-8B`, revision `b968826d9c46dd6066d109eabc6255188de91218`.
- The official chat template implements `enable_thinking=True` by opening the reasoning channel and `False` by pre-filling an empty closed reasoning block.
- Behavior uses identical checkpoint weights, prompts, sampling counts, and decoding distributions across modes. Thinking produced 483/576 valid closed trajectories; non-thinking produced 576/576 valid choices. One thinking-mode decision lacked all cells needed for frame consistency, and worst/best missing-unit bounds are reported.
- All 483 valid thinking trajectories had terminal conclusions removed; none retained a decision marker. There are 203 matched gain/loss trace pairs covering all 36 decisions.
- In the control factorial, the identical stripped donor text occupies the native reasoning channel under the thinking route and the answer channel after an empty reasoning block under the non-thinking route. This channel/position difference is intrinsic to the public hard switch and is an explicit identification boundary.

## Llama-Ecosystem External Audit

- DeepSeek uses official `deepseek-ai/DeepSeek-R1-Distill-Llama-8B` revision `6a6f4aa4197940add57724a7707d069478df56b1` and its native template, which opens `<think>` at the assistant transition.
- The official Meta Llama repository revision is `0e9e39f249a16976918f6564b8830bc894c89659`, but this host receives HTTP 403 from the manually gated repository.
- The locally available `NousResearch/Meta-Llama-3.1-8B-Instruct` mirror revision is `d10aef7999a2b5ba950ab3974312feeedbfe0b77`. Its core config, generation config, model index, tokenizer vocabulary, four shard sizes, and four shard-pointer Git object IDs match Meta's public repository tree exactly. Its `tokenizer_config.json` object differs, so the native chat-template provenance is explicitly the mirror rather than silently labeled official.
- E14 is external replication only. It cannot attribute differences to a single training operation, dataset, tokenizer, template, or configuration choice.
- The original generic DeepSeek answer parser selected the first A/B mention after `</think>` and is invalid for verbose post-think answers. An audited terminal-answer parser recovers 540/576 valid choices and 252 matched gain/loss trajectory pairs across all 36 decisions. The corrected order-conditional frame consistency is 0.947 [0.916, 0.975], versus 0.000 for Llama-Instruct's displayed-A policy.
- The stripping heuristic removed a terminal segment from 533 of the 542 traces previously admitted by the loose parser. After corrected answer filtering, a strict sensitivity excludes nine affected matched pairs; the external control difference remains +0.058 [0.027, 0.089].
- E15's preregistered 18-decision subset contains none of those nine stripping exceptions.

## CPC18 Calibration Execution Audit

- All six frozen regimes produced exactly 3,624 rows: 151 base decisions x
  (one explicit plus three real-history presentations) x two orders x three
  samples. Raw continuations remain ignored outside Git; compact summaries and
  model/source manifests are committed.
- The first CPC18 stripping audit exposed two false commitment patterns:
  "choose between A and B" and a broad "so ... A" window. No heldout data had
  been accessed. The corrected `cpc18_terminal_commitment_v3` rule passes explicit
  positive and noncommitment controls and was applied uniformly to all reasoning
  regimes before causal scoring.
- Strict matched trajectory coverage after correction is 917 units over 147
  problems for OLMo, 1,931 over 145 for Qwen, and 1,920 over all 151 for
  DeepSeek. A strict unit requires a valid terminal answer, a nonempty precommitment
  trajectory, and at least one removed terminal commitment segment in both
  presentations.
- Calibration behavior confirms positive reasoning-associated consistency changes
  for OLMo (+0.225) and same-weight Qwen (+0.276), including invalid-assignment
  sensitivity. It reverses for the unmatched Llama/DeepSeek axis (-0.225): the
  standard Llama comparator is invariant but approximately chance-level with
  respect to exact EV. This is a substantive boundary between invariance and
  EV-guided choice, not an exclusion target.
- E17 factorial scoring uses 917 strict OLMo trajectory units over 147 base
  decisions, 1,931 Qwen units over 145, and 1,920 DeepSeek units over all 151.
  Each unit supplies all four crossed prompt/trajectory cells under both members
  of its comparison axis.
- OLMo and Qwen show positive reasoning-minus-standard trajectory-relative
  control contrasts with clustered intervals excluding zero. The Llama/DeepSeek
  interval includes zero. All three preregistered random-slope MixedLM fits report
  nonconvergence, so no mixed-model coefficient or p-value supports a claim.
- Raw calibration behavior and factorial artifacts total hundreds of megabytes
  and remain ignored. `results/cpc18_calibration_seed121/raw_manifest.json`
  pins every artifact by row count, byte size, and SHA-256.

## CPC18 Competition Audit

- The E18 scientific contract was committed as `9e4a532` before opening the 60
  competition problems. Subsequent config changes populate provenance only.
- The two historical website CSV links return HTTP 404. The official Zenodo
  record supplies the 65,363,460-byte all-problem raw file with matching MD5
  `db1bdcff2e07290714553f29cde81948`.
- Competition distributions are deterministically expanded from the official
  compact parameters. The expansion was independently validated against all 420
  option distributions in the official 210-problem calibration workbook; maximum
  absolute payoff/probability cell error is `3.75e-8` after coalescing duplicate
  payoff rows.
- Exactly 44/60 competition problems pass the unchanged known-probability,
  independence, non-tied-EV, complexity, and three-history criteria, exceeding
  the frozen gate of 40. No selected history contains a payoff outside the
  reconstructed support, and no participant identifier is exported.

## Broad State-Mediation Audit

- E19 units were frozen before patch outcomes: 48 of 65 eligible calibration
  problems, with 16 from each candidate-relative-EV-gap rank tertile. Eligibility
  requires strict nonempty precommitment traces that naturally produce opposite
  choices; no hidden state or patch magnitude enters selection.
- Each base decision contributes both explicit-to-history and history-to-explicit
  directions, making target A/B intervention direction exactly balanced despite
  a 28/20 imbalance in the selected source pair orientations.
- The early-to-late profile is coherent rather than layer-local: layer-0 shift is
  -0.004 [-0.025, 0.016], layer 16 is +1.232 [0.983, 1.469], layer 18 is
  +5.461 [4.603, 6.289] with mean margin reversal, and layer 31 is +7.094
  [5.914, 8.276].
- The 3,072-row patch output remains ignored. Its checksum, byte size, and row
  count are recorded in the committed summary.
