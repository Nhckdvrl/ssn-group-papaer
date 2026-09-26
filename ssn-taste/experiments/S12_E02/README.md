# S12 E02 — held-out readout diagnosis, frozen before inference

E01 produced a directional-looking anomaly, but its questions may cue the answers. This experiment uses **new 60 base items, seed `220926`**, never exposed in E01, and the same cached Qwen2.5-14B-Instruct. E01 is discovery data; E02 is the first independent test of explanations raised by it.

## Competing explanations

1. **Readout wording:** “Nothing states whether” promotes an undetermined answer even under a definition, while “conflict with earlier information” asks about textual incompatibility rather than whether two worlds can coexist. Cleaning these two questions should increase definition positive transfer and reduce fact exception-conflict judgments.
2. **Direction-dependent use of the biconditional:** the model uses the same relation differently for positive inference and counterexample detection despite the role framing. The E01 pattern should persist with scope-clean questions.
3. **Mixed:** only one of the two wording changes matters, making one apparent directionality effect an artifact and the other a possible phenomenon.

The revised mother question *if the directional pattern survives* is: **Does an LM apply a newly introduced relation with different world scope depending on whether it is asked to infer membership or judge an apparent exception?** A positive result here would still need a second model or construction before a broad claim.

## Frozen design

- 60 new bases, 20 per prespecified role framing; 2 roles × 2 readouts × 2 wordings = 480 prompts.
- `original` uses the E01 prompt on the held-out bases. `scope_clean` changes only the downstream question/readout text, identically across roles: positive removes “Nothing states whether ...”; exception asks whether the World B observation can coexist with the World A inventory **given the earlier sentence's stated scope**. Core relation, World A extension, World B event, and role sentence are unchanged.
- Question polarity is balanced 10/10 within each role × readout × wording × framing. Expected A/B labels use the same generator logic as E01. Exact parser and no-exclusion rule are inherited unchanged from frozen E01 revision `8153af3`.
- Primary comparison, separately for each readout: matched-base definition-minus-fact transfer-assertion rate for `original` and `scope_clean`; also report role-specific assertion rates, accuracy, polarity, and invalid counts. The wording effect is the clean-minus-original assertion-rate difference within each role and readout. No LLM judge.
- Controls from E01 apply to the unchanged role and world materials; those controls were 144/144 before this experiment. E02 is diagnostic and does not retroactively repair E01.

Run `python3 e02.py generate`, `python3 e02.py check`, manually inspect bases `000`, `001`, `030`, and `059` in both roles/readouts/wordings, then commit code and items **before** `run`. After output, no prompt, label, parser, or analytic definition changes are allowed for E02.
