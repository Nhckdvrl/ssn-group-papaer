# L12 Data and Identification

**Updated:** 2026-09-09

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
