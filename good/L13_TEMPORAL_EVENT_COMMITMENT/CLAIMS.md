# L13 — Claim Ledger

Status values: `hypothesis` / `supported` / `weakened` / `rejected`.

## C1 — Separability

> **C1.** Under a `before`-clause whose subordinate event is not yet resolved, LLMs do
> not hold the event at `unresolved`; they carry a systematic commitment toward
> realization beyond a matched non-temporal unresolved control.

- Matters because: it makes "mentioned in a temporal relation" behave like "happened".
- Evidence: E01 `neutral_gap`, with `nontemporal_neutral` controlling label avoidance.
- Nearest work: MAVEN-FACT (factuality labels, no construction manipulation).
- Status: **hypothesis**.

## C2 — Timeline-induced actualization

> **C2.** Forcing the model to construct an explicit chronological timeline before the
> realization probe increases its commitment that the unresolved event occurred, on the
> same text.

- Matters because: it turns a correlation into a task-level causal statement, and it is
  the claim no factuality benchmark can make.
- Evidence: E02 `timeline_effect`, target vs control conditions, paired by base.
- Status: **hypothesis**.

## C3 — Update asymmetry

> **C3.** Later confirmation and later cancellation do not move commitment
> symmetrically; cancellation must undo a commitment the temporal construction already
> created.

- Evidence: E01 `update_asymmetry`.
- Status: **hypothesis**.

## C4 — Mechanism (not authorized yet)

> **C4.** The effect is causally carried by the temporal connective's representation:
> patching the connective's hidden state moves realization commitment without changing
> the surrounding proposition.

- Authorized only if C1 and C2 are supported on ≥2 families. Open-weight models only.
- Status: **hypothesis, unauthorized**.

## Anti-claims (must not be promoted)

- "LLMs are bad at `before`." — trivial, and false as stated.
- "`before` means the event did not happen." — wrong semantics.
- Any claim resting on accuracy alone at ceiling.
