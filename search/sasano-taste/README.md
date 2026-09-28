# Sasano Taste Search

**Role:** identify a problem territory worth exploring **according to Sasano's own research taste**.

This lane is intentionally narrower than `../our-taste/`. Do not dilute it with our preferences for trendy methods, benchmark gains, agents, RL, or whatever we personally want to build.

Primary calibration sources:
1. Sasano's actual meeting comments and Slack judgments;
2. concrete papers / projects he explicitly finds interesting or uninteresting;
3. strong ACL / EMNLP / NAACL / TACL work only as secondary calibration.

Historical Sasano-search material is under `../../archive/search/sasano-taste/`.

## 1. The central shape

The strongest recurring Sasano pattern is:

> **a simple, real, natural question → an answer that is not merely obvious → a clear finding an average reviewer can understand**

He repeatedly distinguishes between:
- a topic that sounds potentially interesting;
- and a result that collapses to “そうだよね / of course”.

“there is an effect”, “language A differs a little from language B”, or “the model is somewhat worse here” is usually not enough.

The desired question should be understandable before the mechanism/method exists.

## 2. Avoid races where the research object expires faster than we can study it

Sasano is not categorically anti-hot-topic. The concern is **research half-life and opponent strength**.

Be especially cautious when:
- the field changes month by month;
- new frontier models can erase the phenomenon;
- the natural contribution is “improve current AI capability / benchmark score”;
- the decisive experiments require company-scale models, data, or repeated frontier retraining;
- Meta/Google/OpenAI/etc. and very experienced groups are attacking essentially the same engineering target.

For a Master's project that may take months, this is a structural risk, not a moral objection to trendy work.

Prefer objects whose scientific question would still be meaningful if a stronger model appears six months later.

## 3. “A little unusual, but obviously worth asking once you hear it”

A good Sasano-style topic is often somewhat specific or unusual, yet has an immediate human hook:

> “I would not have thought of that first, but now that you say it, that is genuinely interesting.”

Examples from his own discussions include language-specific / cross-lingual phenomena, special task structures, and naturally occurring semantic or behavioral contrasts.

This does **not** mean “pick an obscure niche”. The unusual setting needs to expose a broader or intrinsically interesting question.

## 4. Natural contrast beats expected confirmation

When two conditions differ, ask whether the answer is already obvious.

Bad endpoint:
> same-form / same-meaning items share behavior more than unrelated items.

That may simply be expected.

Potentially more interesting:
> the same surface form carries conflicting meanings across languages and this shared form systematically causes interference under otherwise controlled conditions.

The point is not that this exact example must be studied. The lesson is:

> **prefer a contrast where either outcome teaches us something nontrivial, and where the interesting possibility is not just the default expectation.**

## 5. Verify the object before theorizing about it

Before building an RQ around a linguistic/model distinction, check that the distinction exists operationally.

Examples:
- are supposedly shared characters actually the same code/token representation?
- does the model have the prerequisite capability?
- does the dataset contain the needed contrasts?
- is the baseline behavior real under a strong model?

Sasano repeatedly asks these basic object-validity questions before discussing mechanism.

## 6. Data / feasibility matter early

A fascinating question with no usable data or credible construction path is often not a practical Master's topic.

Existing natural data is especially valuable. Automatic expansion may help later, but “we can generate a dataset” is not itself the contribution.

Search should identify a plausible data/object path before sending the territory to workbench.

## 7. Generality without forcing artificial breadth

A Japanese/Chinese phenomenon can be valid, but if the scientific question naturally extends to more languages / settings, that is preferable.

Do not force multilingual breadth for appearance. Ask instead:

> is this really about Japanese/Chinese, or about a more general structural relation that happens to be especially visible there?

## 8. RQ and finding must stay crisp

Sasano's later paper feedback repeatedly emphasizes:
- one clear RQ ↔ one clear finding;
- average reviewers should immediately see what is interesting;
- an Introduction must make both **納得できる** and **面白い**;
- a finding that is not surprising enough should not be forced into the headline;
- merely changing model / dataset / evaluation setting does not automatically create novelty.

## 9. Search output for this lane

A Sasano-taste search result should contain:

- **Natural question area:** one sentence, understandable outside the narrow subfield.
- **Why it matters:** no benchmark-only justification.
- **Why it should survive time:** why a stronger model / next release does not instantly obsolete the question.
- **Why the answer is genuinely unknown:** not a disguised expected result.
- **Existing natural data/object:** what we can actually study.
- **Strong parent/baseline:** where workbench should start.
- **Several plausible outcomes:** without choosing the desired one.
- **Nearest-prior risk:** what could compress it into “already known”.
- **Why Sasano might care:** tied to actual taste evidence, not our imitation of his vocabulary.

Then hand the territory to `../../workbench/`.

Do **not** create an Sxx ID here.

## 10. Immediate warning signs

- “We can raise a small model's reasoning benchmark by X points.”
- “This agent/RAG/RL trick is hot right now.”
- “The latest model has not been tested on this dataset.”
- “A and B are theoretically different, so let's see whether the LLM distinguishes them.”
- “There is probably an effect; let's design a synthetic setup that makes it measurable.”
- “The result may be ordinary, but the experiment is very clean.”
- “If it fails, we can add more controls / models / prompts until a story appears.”

These are not automatically bad research in general. They are poor defaults for **this lane**.
