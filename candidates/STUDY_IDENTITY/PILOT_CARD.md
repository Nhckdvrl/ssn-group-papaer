# Study Identity — Minimum Decisive Pilot

## Pilot goal

Answer one question with the smallest credible experiment:

> Holding the paper texts fixed, does access to correct study membership change evidence inference, and if so through information integration or evidence counting?

## 1. Pilot data

Use CochraneForest examples with:
- at least 2 papers for at least one study;
- at least 2 studies in the same review question/forest plot when reconstructable;
- accessible paper text for all included reports.

Target roughly 40–80 review/question units if the released data support it. If the natural qualifying pool is smaller, use all qualifying units and report exact coverage.

## 2. Conditions

Run at least:
1. **ORACLE** — correct study grouping shown;
2. **FLAT** — same papers, no study IDs;
3. **WRONG-SPLIT** — multi-report study presented as separate studies;
4. **WRONG-MERGE** — two studies falsely merged.

Optional fifth:
5. **PREDICTED** — automatic publication linkage.

The wording, paper contents, and question must otherwise be identical.

## 3. Models

Minimum two reasonably strong, architecturally distinct open models so we do not overfit one family, e.g. a Qwen-family model and a Mistral/Llama-family model available locally.

Do not start with a large model zoo. The pilot asks whether the intervention has scientific leverage.

## 4. Outputs

Require a structured output separating:
- study-wise evidence summary;
- study conclusion;
- number of independent studies/evidence units considered;
- final review-level conclusion only when direct gold is available.

Do not let a free-form prose answer make evidence-counting errors impossible to measure.

## 5. Primary metrics

- study-level conclusion accuracy/F1;
- effective evidence-unit count error;
- duplicate-vote rate under wrong split;
- missing-integration rate under flat/wrong split;
- merge-confusion under wrong merge;
- final synthesis preservation where direct gold permits.

## 6. Decisive comparisons

### Test 1 — Necessity
`ORACLE vs FLAT`

### Test 2 — Causal identity corruption
`ORACLE vs WRONG-SPLIT` and `ORACLE vs WRONG-MERGE`

### Test 3 — Where the error enters
Compare document-level extraction correctness with study/synthesis correctness.

The most interesting pattern is:

> paper facts remain correct, but identity corruption changes the evidence conclusion.

That directly establishes a load-bearing representation consequence.

## 7. Outcome branches

### Branch A — ORACLE clearly beats FLAT
Promote if errors are attributable to study-boundary loss and affect scientific inference, not just formatting.

Next phase: predicted linkage, boundaries, second corpus.

### Branch B — FLAT ≈ ORACLE
Still potentially promote if the model reliably reconstructs grouping across genuinely hard multi-report cases.

Then the claim becomes:

> explicit study identity can be removed under specified conditions because modern generators infer the latent evidence unit.

Must include unseen/hard linkage cases to avoid a trivial result.

### Branch C — Wrong split and wrong merge differ
Potentially strongest mechanistic result. Build a decision map of which identity errors are harmful and why.

### Branch D — Near-null everywhere
KILL if flat/oracle/split/merge are effectively equivalent because the selected data do not make study identity load-bearing or the downstream target is insensitive.

## 8. Pre-pilot kill checks

Before GPU:
- verify the exact number of multi-paper studies in the release;
- verify review-level reconstruction is possible;
- inspect 20 cases manually for real report complementarity/redundancy;
- confirm study-level conclusions are external gold and not model-derived;
- re-search publication-linkage-to-synthesis work.

## 9. Pilot promotion threshold

Do not require a specific numeric F1 delta in advance.

Promote only if the experiment supports one of these paper-level conclusions:
- explicit study identity is necessary;
- explicit identity is safely dispensable under nontrivial conditions;
- split/merge errors reveal a principled boundary in evidence-unit representation.

A small benchmark gain without a scientific consequence is a kill.