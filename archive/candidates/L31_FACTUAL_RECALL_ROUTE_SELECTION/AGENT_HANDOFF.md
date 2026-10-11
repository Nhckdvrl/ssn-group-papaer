# L31 Agent Handoff — What Selects a Factual-Recall Route?

Current status:

> **PILOT-AUTHORIZED — E01 ONLY**

Before working, sync latest `main` and read:

- `candidates/L31_FACTUAL_RECALL_ROUTE_SELECTION/README.md`
- `search_rounds/2026-09-13_FACTUAL_RECALL_REGIME_SELECTION.md`
- `RESEARCH_EXECUTION.md`
- `RESEARCH_TOPIC_SELECTION.md`

The README and selection record define the authorized scope.

## Scientific identity

Do not treat this as another localization survey.

The question is:

> **What load-bearing condition determines whether a Transformer learns an Attention-centered or MLP-centered factual-recall computation?**

The mother phenomenon is already established by cross-architecture factual-recall work. E01 tests one pre-specified determinant: **embedding geometry / MLP usability**.

The working causal account is that when the MLP substrate becomes harder for the Transformer to use, a freely trained model should shift factual-memory burden toward Attention; when the MLP route becomes easier, burden should shift toward MLP.

## Why this axis

Do not search architecture knobs.

This axis is selected because existing work independently establishes:

1. both Attention and MLP parameters can implement factual associative memory;
2. embedding geometry and decoding margin can strongly alter MLP storage capacity/usability inside a Transformer;
3. natural pretrained models already show different Attention/MLP factual-recall organizations.

The missing experiment is whether manipulating substrate usability changes which route a model **chooses when both are available**.

## E01

Use a small synthetic factual-recall Transformer based on the public ICLR-2025 factual-recall setup or a faithful equivalent.

Keep the fact mapping, data distribution, architecture, training budget, optimizer and evaluation fixed. Manipulate only the predeclared embedding-geometry condition.

Preferred implementation family:

- low-whitening / baseline geometry;
- high-whitening / altered geometry;
- optionally one midpoint only if frozen before outcomes.

You may adapt the precise transform to match the published code/theory, but do not search transforms by outcome sign.

### Critical difference from Dugan/Garcia constructive-MLP studies

They constrain/freeze alternative pathways so the Transformer must query the provided MLP. L31 must **not** do that in the load-bearing experiment. Attention and MLP must both remain trainable/available so the experiment measures route selection.

## First-stage gate

Before analyzing learned routes, verify that the manipulation materially changes the intended MLP-usability quantity in the expected direction.

Choose the first-stage quantity from the source literature before outcome inspection, e.g. decodability / minimum decoding margin / directly measured MLP usability.

If first stage is weak or reversed, stop. Do not inspect a later route trend and narrate it anyway.

## Route measurement

Use at least two predeclared causal views with factual behavior as endpoint.

A sensible pair is:

1. Attention-output vs MLP-output severing/ablation and change in correct-answer logit/accuracy;
2. restoration or path-aware intervention designed to stress redundant-path compensation differently.

Do not use a linear probe or activation norm as the main route label.

Define a normalized route contrast before reading treatment signs, conceptually:

`R = causal contribution(Attention) - causal contribution(MLP)`.

Primary effect:

`Δ_route = R(high-usability geometry) - R(low-usability geometry)`.

The exact sign convention is arbitrary; freeze it in the config/report before seeing results.

## Stop rules

- geometry does not move MLP usability: **STOP / instrument failure**;
- geometry moves usability but route does not move: **KILL current determinant hypothesis**;
- route methods disagree materially: **construct unstable; HOLD/KILL**;
- one seed produces the desired sign but others do not: do not cherry-pick; report instability;
- do not launch Qwen/LLaMA model-zoo experiments after an ambiguous E01.

If E01 succeeds cleanly, stop and return to selection. C2/C3 are not authorized.

## Deliverables

Keep all scripts/configs/results under `candidates/L31_FACTUAL_RECALL_ROUTE_SELECTION/`.

The final E01 report should include:

- exact task/model/config;
- geometry manipulation and first-stage result;
- training curves and factual competence by arm;
- both causal route measurements by seed;
- uncertainty/seed variation;
- locked outcome interpretation;
- `PASS TO RE-SELECTION`, `HOLD`, or `KILL`.

The goal is not to make the hypothesis win. The goal is to decide whether substrate usability causally selects factual-memory computation.
