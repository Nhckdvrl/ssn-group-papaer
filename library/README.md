# Research Library — Curated Front Door

**Last verified:** 2026-09-28

This folder is the reusable knowledge layer so future research does not restart from a blank browser tab.

It contains:
- `TERRITORY_BANK.md` — durable scientific territories; **not candidate ideas**.
- `KEY_PAPERS.md` — anchor papers worth rereading.
- `BLOGS_REPORTS.md` — high-value blogs, project reports, research feeds.
- `deep/academic/` — detailed paper genealogies / literature maps.
- `deep/industry/` — deployment / company reports.
- `deep/open-artifacts/` — open-model / Hugging Face / artifact archaeology.

## How to use

When a new direction appears:

1. Check `TERRITORY_BANK.md`.
2. Read relevant anchors in `KEY_PAPERS.md` / `BLOGS_REPORTS.md`.
3. Reconstruct the nearest lineage in `deep/academic/`.
4. Check public artifacts in `deep/open-artifacts/`.
5. Search the web only for missing recent work / nearest prior.

## Do not read papers as finished ideas

For important papers, record not only:
- problem;
- method;
- result.

Also reconstruct:

- **parent baseline / belief** — what did the field do immediately before?
- **pressure** — what concrete difficulty made the parent insufficient?
- **changed premise** — what assumption did the paper reject?
- **revealing experiment** — what analysis could have exposed the issue before the final solution?
- **exploration space** — what plausible alternatives existed?
- **crystallization** — why did this final RQ/method become natural?
- **related-work boundary** — what makes it a new scientific object rather than a combination/cell?
- **reusable research move** — what part of the process should we imitate?

This is the most important use of the library for topic search.

### Documented vs reconstructed genesis

Do not invent author history.

Tag notes conceptually as:
- **DOCUMENTED** — supported by author retrospective/blog/talk/repo/appendix;
- **RECONSTRUCTED** — a plausible scientific path inferred from paper + related work.

Reconstruction is for training our research taste, not for making biographical claims.

## Genesis patterns already worth studying

### [RECONSTRUCTED] Strong baseline changes the question — ResNet Strikes Back
A mature architecture was still widely used as a baseline, but training practice had advanced. Rebuilding the recipe materially changed what counted as a competitive ResNet baseline. The reusable move is:

> **before proposing a new architecture-level fix, ask whether the baseline is still being trained like the era in which it was introduced.**

### [RECONSTRUCTED] Entangled method zoo → explicit design space — EDM
Instead of adding one more diffusion trick, the paper separated previously entangled choices and recombined them systematically.

Reusable move:

> **when a field has many interacting tricks, decomposition itself can expose which assumptions are actually load-bearing.**

### [RECONSTRUCTED] Complex pipeline → changed mathematical object — DPO
RLHF's reward-model + RL pipeline was treated as the pressure. A different parameterization let the standard objective collapse into a much simpler optimization problem.

Reusable move:

> **sometimes the bottleneck is not missing capacity but the representation of the optimization problem.**

### [RECONSTRUCTED] Scaling exposes a representation bottleneck — FAST
Autoregressive VLA scaling ran into poor action tokenization for high-frequency dexterous control. The solution follows from localizing the bottleneck to the action representation, not from adding a generic larger policy.

Reusable move:

> **a successful system abstraction can become the next bottleneck once scale/task frequency changes.**

### [RECONSTRUCTED] Successful training recipe → decompose where learning signal actually lives
Recent RLVR work first treats RL as a phenomenon to understand, then decomposes token entropy or positive/negative sample contributions. The method comes after the asymmetry is measured.

Reusable move:

> **when a training recipe works, ask which subset of the nominal learning signal is actually doing the work.**

## What belongs here

Add an item only if it has repeat value:
- foundational primitive;
- changed premise;
- strong negative/re-attribution;
- baseline/training recipe;
- reusable research-craft lesson;
- public artifact useful for future work.

Do **not** add every new arXiv paper or candidate-specific nearest-prior dump.

## Entry labels

- **ANCHOR** — durable foundation.
- **BRIDGE** — changes how a lineage is understood.
- **FRONTIER** — recent; re-check before current claims.
- **ARTIFACT** — code/weights/data useful experimentally.
- **CRAFT** — research/experimental practice.
- **NEGATIVE** — valuable limitation/re-attribution.

Keep this layer short enough to reread.
