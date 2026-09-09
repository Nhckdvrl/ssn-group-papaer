# L12 — Data and Identification

**Core principle:** the parent phenomenon is already established. The next evidence must distinguish **selective semantic abstraction** from **broad context disengagement**.

# 1. Behavioral substrate

Use the three published risky-choice prospects already audited from **Mind the (DH) Gap!**.

Keep:
- gain/loss framing;
- option order;
- the exact audited Instruct-SFT / Think-SFT sibling checkpoints.

Do not build a new large benchmark for this pilot.

# 2. E07 unit

The unit is one:

> **prospect × frame × order**

with three contextual versions of the same displayed options.

### none
No additional note.

### redundant
A short contextual note rechecks one probability and leaves it unchanged.

### correction
The same note structure updates that probability to a frozen value that flips the EV-optimal underlying action.

Example:

> Additional context: the probability associated with Option B was rechecked and remains 0.34.

versus

> Additional context: the probability associated with Option B has been updated from 0.34 to 0.36.

The displayed option lines remain identical across the three context conditions.

# 3. Gold

Gold is the EV-optimal choice under the currently valid facts:

- **none / redundant:** original probabilities/payoffs;
- **correction:** the explicit contextual update supersedes the corresponding original probability.

The three frozen updates in `configs/boundary.json` each flip the EV-optimal underlying action in both gain and loss framings.

No LLM judge is needed for the primary outcome.

# 4. Two load-bearing quantities

### Irrelevant-context invariance

Compare **none → redundant**.

> Does behavior remain stable when the extra context changes no decision fact?

### Relevant-context uptake

Compare **redundant → correction**.

> How much does the correction move choice probability toward the newly EV-optimal action?

Correction EV accuracy is kept only as an easy-to-read secondary number.

Together these distinguish:

- **selective abstraction:** irrelevant context is ignored, relevant context is used;
- **context flattening:** irrelevant context is ignored, but relevant context is also underused.

# 5. Model comparison

Primary comparison:

- `allenai/Olmo-3-7B-Instruct-SFT`
- `allenai/Olmo-3-7B-Think-SFT`

They are sibling branches from a common base.

The current scientific claim concerns the transformation visible across these released branches. Stronger training-causal attribution is not required for E07.

# 6. E08

Only if E07 yields a stable semantic-relevance distinction:

> use matched redundant/correction contexts to intervene on the pre-answer decision state.

The target is whether that state carries **decision-relevant context** while becoming invariant to **irrelevant context**.
