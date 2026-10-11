# L12 Data and Identification

**Updated:** 2026-09-10

## 1. Current pilot substrate

The mechanism-discovery experiments use the three explicit risky-choice prospects published in *Mind the (DH) Gap!*, crossed with:

- gain/loss frame;
- both displayed option orders;
- four sampled Think-SFT trajectories per cell.

The independent scientific unit is the **base prospect**, not a generation, trace, frame, order, or patch layer. Current prospect-cluster intervals therefore have only three independent units and must not be presented as full-paper breadth.

## 2. Behavioral gold

Each option is a finite lottery. The underlying choice with the greater expected payoff is computed directly from the displayed probabilities and outcomes. Gain/loss transformations and order swaps preserve a known mapping between the underlying choice and displayed label A/B. No LLM judge is used.

## 3. E07 trajectory surgery

E07 removes the suffix beginning with the first directional comparison or explicit commitment while retaining the earlier reasoning. The audit records:

- the original and stripped text;
- every removed segment;
- whether an A/B decision marker remains;
- the retained character fraction;
- validity and matching status.

Final audit: 48 traces generated, 47 valid, 46 matched target rows; all valid traces had a conclusion removed, none retained a decision marker, none became empty, and the mean retained character fraction was 0.481.

## 4. E08 identification

Target and donor are matched on base prospect, displayed order, and sample index, and differ in frame and resulting decision. Donor reasoning text is never appended to the target. Only the donor final-token residual state at one decoder layer is substituted. Self/no-patch behavior is the baseline, and the signed outcome is movement toward the donor decision.

This identifies a causal role for the substituted pre-answer state under the constructed prefixes. It does not by itself identify the training operation that created the state.

## 5. E09 identification

E09 crosses prompt frame and stripped-trajectory frame independently in a 2 x 2 factorial. The exact same trajectory strings are scored by the sibling Instruct-SFT and Think-SFT checkpoints, using each checkpoint's native answer transition. The reference outcome is the displayed choice optimal in the gain frame.

The primary quantity is:

> `(trajectory control - prompt control)_Think - (trajectory control - prompt control)_Instruct`

This directly tests whether the behavioral branch transition is accompanied by stronger trajectory-relative causal control. Native template differences and non-identical branch training remain explicit attribution limits.

## 6. Full-paper stimulus expansion - completed

E10 contains 36 independent base decisions constructed under requirements frozen before model evaluation:

- simple two-option lotteries with exact, programmatically verified expected values;
- natural round payoffs and probabilities, with no complex fictional world;
- exact gain/loss and order-matched variants;
- stratification by EV gap and probability/payoff trade-off, avoiding accidental dominance;
- no duplicate or affine-equivalent base units within a stratum;
- a held-out audit table containing all values, gold mappings, and exclusion reasons;
- base-decision cluster bootstrap as the primary uncertainty analysis.

The audit passes every listed constraint. E10 validates the behavioral transition and causal-control index across the full set. E11 repeats state substitution on a preregistered 18-decision stratified subset.

Frame consistency is computed **within each displayed order first**, then averaged within a base decision. This prevents a fixed displayed-position policy from appearing invariant after order marginalization. The earlier order-marginalized E02/E10/E13/E14 summaries were superseded on 2026-09-10; raw generations did not change.

## 7. E12-E13 breadth identification

E12 reuses the frozen E10 decisions and stripped trajectories at exact OLMo DPO revisions. Its estimand is persistence of the branch contrast along documented continuations; it cannot identify DPO as the cause of the original divergence.

E13 uses the same 36 decisions and one Qwen3 checkpoint under its official hard thinking switch. The behavioral contrast fixes weights and surface prompts. The control contrast fixes weights and stripped donor text, but native route is a compound operation: reasoning-channel placement versus answer-channel placement after an empty reasoning block. Accordingly, E13 identifies reasoning-route-dependent integration and supplies complementary triangulation; it does not isolate a hidden mode bit, token count, or text position.

## 8. E14-E15 external-replication identification

E14 compares unmatched Llama-ecosystem post-training outcomes. The estimand is qualitative external replication of aligned behavioral invariance and stronger trajectory-relative causal control, not a causal effect of reasoning training.

After terminal-answer reparsing, DeepSeek supplies 252 valid matched trajectory pairs across all 36 decisions. The primary E14 control summary filters to those corrected-valid pairs. A construct-validity sensitivity additionally excludes nine pairs whose natural-language commitment was not detected by the frozen stripping heuristic; the cross-model control difference remains positive with a clustered interval excluding zero.

E15 substitutes residual state within DeepSeek only. Its target/donor pairs share base decision, displayed order, and sample-index rule, while frame and gold decision direction differ. No donor text is inserted. This establishes a causal role for the pre-answer state under constructed prefixes, not equivalence of internal layer coordinates across model families.

## 9. CPC18 description/history expansion

E16 uses the official CPC18 calibration split only. The source workbook contains
the exact finite distributions for 210 base decisions; the Zenodo raw file contains
510,750 trial rows. Source URLs, byte size, and cryptographic checksums are frozen
in `configs/cpc18.json`. Large public source files stay in an external cache.

The inclusion contract was fixed before any CPC18 model scoring: known probabilities,
independent option outcomes, valid probability mass, non-tied exact EV, no more than
10 outcomes per option, and at least three distinct full-feedback histories. This
yields 151 problems and passes the preregistered 150-problem gate. Support dominance
is retained and reported as a stratum because it is a meaningful difficulty
boundary, not an identification failure.

Each exported history contains both realized and forgone payoffs from trials 6-25.
Three distinct real histories are sampled uniformly without replacement using the
frozen seed. The selection does not inspect empirical direction, participant choice,
or model data. Normalized Wasserstein distance to the published marginals is retained
only as a representativeness audit, not as a filter. No participant identifier leaves
the external raw cache.

Exact expected payoff remains the independent gold. Human choices are provenance
and descriptive context, never answer labels. Description/history consistency is
computed within displayed order and history first, then averaged within base
decision. Histories, orders, and generations never inflate the independent sample
size.

The E18 contract was committed as `9e4a532` before the 60 CPC18 competition
problems were opened. Under the unchanged rules, 44/60 problems pass the frozen
gate of 40. They were scored once as external confirmation and were never used to
revise prompts, parsing, trajectory construction, exclusions, or estimands.

The calibration behavior run contains 3 samples in every frozen cell for all six
regimes. Terminal-answer parser version `cpc18_terminal_v2` leaves validity between
0.841 and 1.000 across regimes. During the pre-heldout audit, terminal stripping
incorrectly treated the noncommittal phrase "choose between A and B" and the broad
connector "so ... A" as commitments. Version
`cpc18_terminal_commitment_v3` requires the option label to be the direct object of
the decision verb or a tightly adjacent conclusion label. Positive commitment and
noncommitment controls are executable in `scripts/test_cpc18_parser.py`; all raw
reasoning generations were reparsed uniformly before E17 factorial scoring.
The same parser and stripping versions were then applied unchanged to E18.
