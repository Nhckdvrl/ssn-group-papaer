# 2026-09-14 Rough-Lead Selection Audit

Target: ACL / EMNLP / NAACL Main  
Scope: audit the three rough leads from the 2026-09-14 silent-structure / discourse / information-structure search. No new deep-search expansion in this pass.

---

## Executive verdict

The prior search ended with three `ROUGH LEAD — UNRESOLVED NOVELTY` items:

1. Bridging relation provenance
2. Ellipsis reconstruction substrate
3. Focus alternative-set computation

After selection-quality review:

| lead | verdict | reason |
|---|---|---|
| Bridging relation provenance | **KILL — K244** | the two provenance sources cannot currently be manipulated as the same quantity; knowledge editing damages semantics, nonce entities change the question, and context conflict collapses to generic context-vs-parametric evidence |
| Ellipsis reconstruction substrate | **PROMOTE — L38 SERIOUS CANDIDATE; NO PILOT** | natural silent-content object, live theory distinction, both directions informative; remaining blocker is a genuinely selective causal instrument separating semantic recovery from structural licensing |
| Focus alternative-set computation | **KILL CURRENT FORM — K245** | no clean natural operator-independent focus manipulation in text; positive result risks becoming constructed-feature steering / causal localization, negative result is confounded with instrument failure |

The prior broad-search kills are registered separately as K237–K243. After this audit, next kill ID is **K246**.

---

# 1. Bridging relation provenance — K244

Original attractive question:

> Is a successful bridge such as `house -> door` driven by a relation stored parametrically in world knowledge, or by a relation constructed online in the current discourse?

Why it looked strong:

- ordinary resolution accuracy cannot reveal provenance;
- both directions appeared scientifically meaningful;
- a conditional law / regime switch sounded stronger than a benchmark or feature-localization paper.

Why it fails Selection:

### The operation changes the scientific quantity

The project needs two independently manipulable quantities:

- stored relation prior;
- discourse-built relation evidence.

But the obvious operations do not isolate them.

**Knowledge editing:** removing or reversing `house -> door` can change the lexical/world representation needed to interpret the bridge itself. The edit is not guaranteed to target only relation provenance.

**Nonce entities:** this removes the parametric source and turns the task into in-context relation learning. It no longer compares two provenance routes for the same bridge.

**Context/world conflict:** this is interpretable, but the parent compresses to generic parametric-prior-vs-context competition with bridging as one task wrapper.

Therefore the proposed `provenance-sensitive law` is not identified before the result. A large or nonlinear effect would not repair the inference bridge.

**Final:** K244.

---

# 2. Ellipsis reconstruction substrate — L38

Original question:

> Does successful ellipsis reconstruct antecedent-like syntax, or recover event/propositional meaning while syntax acts as a separate identity/licensing filter?

This lead passes the natural-question test better than the other two.

### Why the scientific object is real

Ellipsis contains interpreted material with no overt realization. This makes `what object is actually reconstructed?` a natural question independent of any interpretability method.

The two candidate accounts can produce the same correct surface answer:

- **syntactic reconstruction**: a silent structural object is part of semantic recovery;
- **semantic recovery + licensing**: meaning is recovered independently and structural identity only controls whether the ellipsis is licensed.

### Why this is not just `syntax exists in the model`

A model can encode syntax and still resolve ellipsis without copying that syntax into the silent content. Existing covert-syntax evidence therefore does not own the same quantity.

The Main-level remainder is:

> **Is syntax constitutive of the recovered silent object, or a separate constraint on an independently recovered meaning?**

### Why it is not pilot-authorized yet

The candidate still needs an operation that changes structural identity while preserving intended meaning, or vice versa, and then reads out two independent consequences:

- semantic recovery;
- structural licensing/identity.

If the only available method is a donor hidden-state transplant or a learned direction whose interpretation already assumes the target object, the project becomes method-first and dies.

**Final:** register **L38 — SERIOUS CANDIDATE — IDENTIFICATION BLOCKER; NO PILOT AUTHORIZED**.

---

# 3. Focus alternative-set computation — K245

Original attractive question:

> Does a language model construct one reusable set of focus alternatives that multiple operators/consequences consume, or do construction-specific shortcuts directly produce the outputs?

The cross-consequence version is much better than `find a focus feature`, but the current textual substrate is not clean enough.

### Core identification problem

Prosodic focus is usually not overtly marked in ordinary text. Text experiments therefore tend to manipulate:

- capitalization / typography;
- clefts or word order;
- lexical focus particles;
- construction-specific cues.

Each changes salience, syntax, lexical content, or operator structure in addition to the alleged alternative set.

A second route — explicitly construct candidate alternatives and discover/patch a latent alternative direction — risks defining the object using the same target effect the experiment later claims to explain.

Thus:

- a positive result compresses to `constructed focus-related state can steer focus outputs`;
- a negative result cannot distinguish `no shared alternatives` from `bad focus instrument`.

Cross-operator breadth adds scale but not identification.

**Final:** K245. Reopen only if a natural, operator-independent focus manipulation plus independently defined causal operation appears.

---

# 4. What changed relative to the original report

The original report was correct to avoid promoting any of the three immediately. The stricter audit changes two things:

1. **Bridging should not remain a live rough lead.** Its construct problem is not a minor implementation blocker; it undermines the same-quantity estimand.
2. **Focus should not remain live merely because no direct owner was found.** Exact novelty is irrelevant if the scientific object cannot be independently manipulated in text.

Ellipsis is the only lead whose remaining blocker is plausibly an **instrument problem around an already-natural scientific distinction**, rather than a problem with the scientific object itself.

That is enough to justify development to L38, but not enough to spend compute.

---

# 5. Current state after audit

- **New L-series:** L38
- **L38 status:** SERIOUS CANDIDATE — IDENTIFICATION BLOCKER; NO PILOT AUTHORIZED
- **New kills physically registered:** K237–K245
- **Next kill ID:** K246
- **Approved paper mainline:** unchanged; NONE

No result in this audit authorizes a GPU run.
