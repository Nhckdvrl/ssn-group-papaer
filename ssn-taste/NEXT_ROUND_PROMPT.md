# Next-Round Research-Question Search Prompt

Date of handoff: 2026-09-16

You are taking over the next round of research-question search for `Nhckdvrl/ssn-group-papaer/ssn-taste`.

## 0. Mission

Find genuinely worthwhile, feasible research questions for **ACL / EMNLP / NAACL Main**.

Use **TACL / ICLR / ICML / NeurIPS** only as secondary calibration for scientific taste and idea-generation quality. **EACL / AACL / Findings / workshops / arXiv may be searched aggressively for novelty checking and collision detection, but must NOT be used as positive taste calibration.**

The highest-priority constraint is **Sasano fit**. The search should feel like work Sasano would regard as a clear, interesting, well-motivated research question, while also matching the scope and quality of ordinary strong ACL/EMNLP/NAACL Main papers. Best/Outstanding papers are taste references, not the acceptance threshold.

Do not ask the user to choose abstract territories. Search directly, present concrete questions, and update your search strategy from the user's reactions.

---

# 1. The most important correction from the previous round

The previous round repeatedly drifted into a bad idea-generation loop:

> recent Main paper reports phenomenon -> authors did not fully explain why/mechanism/boundary -> propose that missing explanation as a new topic.

**Do not use this as the default search method.**

We have repeatedly found that once a mother phenomenon is important enough to appear in Main, its obvious mechanism, boundary conditions, representations, training source, and follow-up controls are already occupied by the original paper, parallel work, or immediate successors. Even if the exact experiment is absent, reviewers can compress the proposal into a follow-up.

Apply the **remove-the-trigger-paper test**:

> If the particular recent paper that inspired the idea disappeared, would the scientific question still naturally exist because of an independent theory, changed premise, real-world change, workflow defect, measurement flaw, resource trade-off, or practical need?

If not, deprioritize it as a likely follow-up.

This does **not** mean all successor work is forbidden. Sasano explicitly said that fundamental novelty is preferable, but a topic can still be valid when an existing method/formulation has a **clear point that genuinely should be improved**. The distinction is:

- weak successor: `they found X; we explain more of X / add one boundary / use a newer model / run a cleaner ablation`;
- potentially valid successor: `their formulation makes a load-bearing assumption or has a structural deficiency; fixing it changes the scientific inference, scientific object, or practical capability`.

---

# 2. Reconstructed Sasano taste — keep this visible while searching

Do not reduce Sasano taste to one template.

### Sato — strongest positive anchor

The attractive structure is:

> everyone can understand the puzzle -> identify a real scientific object -> use controlled experiments to distinguish plausible sources/explanations.

Sato's character-level knowledge work is valuable as a **way of finding and structuring questions**, not as a rule that every topic must be a source-tracing paper. A Sato-shaped question is not novel merely because it asks “where does X come from?”

### Guo — strongest novelty warning

Sasano explicitly judged a topic weak because **`先行研究との差が小さい`**. Re-running an old question on modern models is insufficient unless the model/data/setting changed in a way that changes a load-bearing premise and makes the result genuinely unknown in advance.

### Hamdi — reviewer curiosity and claim discipline

For top conferences, the Introduction must convince an average reviewer that the question is both reasonable and interesting. Research questions and findings should line up clearly. Unexpected results can still be interesting; do not require pilots to confirm the original hypothesis. Internal/behavioral distinctions are useful when they deepen understanding, but mechanism is not automatically the paper's main contribution.

### Utami — exogenous real-world change

A technology/social change can create a new question about language behavior. The question itself should be visible and intuitive. Do not broaden this into generic “LLMs changed language.” Find one changed population/process and one interpretable consequence.

### Kisako / Tsukagoshi — systematic trade-off / shared practical objective

A valid topic can start from a simple practical scientific question, e.g. two mature operations both target the same resource objective, yet their difference/interaction under a common budget is not understood. It does not need a deep linguistic mechanism. However, do not manufacture this by attaching an arbitrary downstream property to compression.

### Oshika — missing independent workflow decision

A mature workflow can contain a Main-sized question when two sides are developed but a necessary intermediate decision is still treated as human/gold/oracle. The missing step must be independently necessary, not merely an implementation detail already varied in recent work.

### Yano / Youchi — improvement can be legitimate

Similar work does not automatically kill a topic. A concrete weakness in prior formulation/method can motivate new work if the deficiency is important and the prior literature is thoroughly understood.

---

# 3. Topic preference — do NOT chase hype

Do not default to **RL-for-reasoning, generic agents/tool use, multi-agent systems, or whatever is currently fashionable**. The previous round repeatedly drifted there because those literatures are salient and easy to search, not because they best match Sasano.

Prefer durable NLP/LLM objects whose scientific interest would remain if the current hype cycle disappeared:

- language understanding and model knowledge;
- simple, interpretable semantics/pragmatics (not highly technical linguistics);
- representation / readout / generation behavior;
- evaluation and measurement validity;
- embeddings, representation compression and systematic trade-offs;
- multilingual/language variation only when there is a genuinely new question, not another competence benchmark;
- real-world language change with natural historical data;
- text generation and communication;
- missing decisions in established NLP workflows;
- older scientific questions made newly identifiable by a genuinely changed model premise.

User preferences: **avoid benchmark-centric work, avoid difficult/expensive data construction, avoid highly technical linguistics, prefer cheap clean pilots.** Simple semantics is fine.

---

# 4. What a good topic should look like

A strong candidate usually has most of the following properties:

1. **One-sentence curiosity.** An average NLP reviewer can understand what is unknown and why they might care without a page of framing.
2. **Independent reason to ask.** The question does not exist only because one recent paper left a future-work sentence.
3. **Real novelty at the reviewer-compression level.** Do not rely on “nobody tested this exact condition.” Ask what parent literature a reviewer will put it in.
4. **Correct scientific width.** Calibrate the Introduction-level RQ, claim scope, and Related Work neighborhood against actual ACL/EMNLP/NAACL Main papers and Sasano projects. Do not make a corner case sound like a broad parent; do not make the parent so broad that the experiment cannot answer it.
5. **Clean identifying experiment.** Prefer changing one scientifically meaningful variable at a time. Complexity of method is not a virtue.
6. **Feasible data/compute.** Natural or already available data is strongly preferred. A Master's project should not require massive pretraining or months of annotation before knowing whether the RQ has leverage.
7. **Claims do not exceed evidence.** A clean descriptive/systematic paper is allowed; mechanism is optional unless the question requires it.
8. **Not purely phenomenon-gambling.** Exploratory questions are fine, and the answer can be unknown. But avoid topics whose paper value exists only if one quirky anomaly happens.

Important: **simple question != weak question**. EMNLP 2025 `Flaw or Artifact?` asks whether a widely reported model weakness is partly an evaluation artifact; NAACL 2025 MORCELA challenges the assumption that the same correction should apply to all LMs. These are small-sounding questions whose assumptions are load-bearing and therefore change scientific conclusions.

---

# 5. High-value idea provenance to prioritize

Do not follow this list mechanically; use it as a search prior and revise it when actual Main papers show a better pattern.

### A. Load-bearing assumption / measurement validity

Find an assumption used across a scientific literature where changing it could alter rankings, effect sizes, or the interpretation of prior results. Strong examples of the *style* are EMNLP 2025 `Flaw or Artifact?` and NAACL 2025 MORCELA.

Do not create a trivial metric nitpick. The assumption must matter to a scientific conclusion.

### B. Changed premise / changed population

An old question becomes genuinely new when a premise changes enough that previous explanations no longer decide the answer. This can come from model architecture/training changes or real-world behavioral change. `newer model` alone is not enough.

### C. Hidden oracle / missing decision in an established NLP workflow

Draw the pipeline and locate a necessary intermediate operation that is still given by humans/gold data. Verify that Main work has not already treated that step as a variable. Oshika is the anchor.

### D. Same objective/resource, different mature operations

Start from a natural objective (storage, information budget, representation capacity, annotation effort, etc.). If two established operations achieve that objective differently, ask whether they are equivalent or how the budget should be allocated. Kisako is the anchor. The common resource unit must be scientifically coherent.

### E. Independent defect in a prior method/formulation

A successor is allowed when the prior method has a concrete structural flaw—not merely because we can run a cleaner experiment. The fix should change inference, validity, or usefulness.

### F. New identifying operation for an older scientific debate

Modern models sometimes make a classical distinction newly observable or intervenable. This can be excellent, but only when the new operation genuinely changes what evidence can decide—not when it is simply “test the old psycholinguistic effect on LLMs.”

### G. Cross-lineage collision

Two mature literatures may implicitly treat the same quantity differently. This is useful only if the intersection creates a **new measurable quantity or conflicting prediction**. `Paper A + Paper B` by itself is not an idea.

---

# 6. Search process — lightweight but disciplined

## Step 1: Re-anchor before generating

At the start of each substantial search batch:

- reread a few Sasano Slack examples/comments (especially Sato, Guo, Hamdi, Utami, Kisako/Tsukagoshi, Oshika, Youchi/Yano);
- sample several recent **ACL/EMNLP/NAACL Main** papers across non-hype areas;
- inspect not only abstracts/results but **Introduction + Related Work** to understand how the paper's question was generated, what parent it claims, and how wide that parent is.

Do not use only Best/Outstanding papers. Ordinary strong Main papers are the main calibration distribution.

## Step 2: Generate raw questions from provenance, not from paper edges

Search broadly across scientific objects. Produce raw RQs before building full paper stories. Do not spend time designing mechanisms/methods for a seed that has not survived novelty.

## Step 3: Parent-level novelty check

For every promising seed, search aggressively across ACL Anthology, arXiv and the broader web.

Read the nearest direct papers, especially their Intro/Related Work. Ask:

- What scientific parent do they already own?
- What would a reviewer call our paper in one sentence?
- Is our difference a new question / structural defect, or only a condition, dataset, model family, mechanism analysis, or cleaner ablation?

**EACL/AACL/Findings/arXiv can kill a topic. They cannot make a topic attractive just by resembling their accepted work.**

## Step 4: Width + Sasano audit

Before promotion, compare the candidate to several nearby ACL/EMNLP/NAACL Main papers:

- Is our Introduction-level RQ at roughly the same abstraction level?
- Is Related Work neither artificially narrow nor absurdly broad?
- Does it resemble a Sasano-approved way of asking questions?
- Is the topic scientifically durable rather than hype-driven?

If exact novelty survives but reviewer compression makes it one cell inside an owned parent, kill it. F06 `optional/default tool semantics` is the canonical warning.

## Step 5: Only then design the minimum experiment

Specify the cheapest experiment that actually distinguishes the relevant hypotheses or measures the target quantity. Do not turn the pilot into a benchmark construction project.

A pilot is not always a “life/death anomaly check.” For genuine inquiry questions, different outcomes can all answer the RQ. For phenomenon-dependent proposals, verify the phenomenon cheaply before investing.

## Step 6: Keep the ledger current

- rejected serious ideas -> `ssn-taste/FAILED_TOPICS.md`, including nearest prior and the actual parent-level failure;
- only genuinely surviving questions -> `ssn-taste/SELECTED_TOPICS.md`;
- do not resurrect killed parents by changing model, language, prompt, dataset, or mechanism name.

Current state: **0 selected topics**. That is acceptable.

---

# 7. Mandatory drift audit

The biggest failure of the previous round was not lack of effort; it was **attention drift**. Therefore periodically audit the search itself.

After roughly 8–12 seriously checked seeds, or whenever several consecutive ideas come from the same fashionable area, stop generating for a moment and ask:

1. Where did the last batch of ideas come from?
2. How many were `Main mother phenomenon -> why/mechanism/boundary` follow-ups? If several, the generator has drifted.
3. How many came from RL/agents/tool use merely because those fields are active? If several, leave that domain.
4. Have EACL/AACL/Findings/arXiv started influencing positive taste rather than only novelty? Correct immediately.
5. Are we searching exact keyword gaps instead of reviewer-level parents?
6. Are ideas becoming benchmark/data-construction projects despite user preference?
7. Is the RQ width similar to actual Main Introductions?
8. Re-read at least one Sasano comment and one strong Main Introduction/Related Work before continuing.

If many seeds die for the **same reason**, do **not lower the bar** and do not keep shrinking them. Change the **idea generator / scientific object**.

The process itself is provisional. If careful reading of strong ACL/EMNLP/NAACL Main papers reveals that these rules are steering search away from how good papers actually originate, revise the process and explicitly explain the correction. Do not obey this prompt mechanically when evidence says the process is wrong.

---

# 8. Anti-patterns to avoid

Do not spend serious search time on:

- recent Main phenomenon -> unexplained mechanism / why / boundary;
- old task + latest LLM;
- another benchmark for a known capability;
- `they did behavior, we do mechanistic probing` as the novelty claim;
- one more language/domain/model inside an occupied parent;
- arbitrary `X != Y` slogans created before identifying a real scientific object;
- giant gate systems (`why-space`, `belief update`, anomaly gates, MDE, etc.) applied to every exploratory question;
- chasing RL/agent/post-training hype by default;
- forcing every paper to have deep mechanism;
- forcing every idea to Best-Paper magnitude;
- using EACL/AACL acceptance style as positive taste calibration;
- saving an exact-cell novelty by rhetorically broadening the parent.

---

# 9. Previous-round anti-resurrection notes

Read `ssn-taste/FAILED_TOPICS.md` and the repository's older `failed/` ledgers before proposing topics.

Important directions already found to be occupied or poor fits include:

- post-training uncertainty: latent information vs confidence readout;
- message/turn serialization neutrality;
- API/tool schema evolution and optional/default semantics;
- timeout/idempotency/action-recovery semantics;
- token-vs-sample SFT length weighting;
- cross-lingual transfer/shared-representation origin as a broad parent;
- typo/noise robustness source tracing and typo internal repair;
- reasoning-control degradation as another mechanism follow-up;
- long-output training -> long-input transfer as a mother-paper why question;
- predictive fidelity vs interventional/causal fidelity of proxy models;
- unknown/absence vs false/closed-world semantics as a broad parent;
- PRM step-segmentation sensitivity;
- structured/grammar-constrained decoding as semantically neutral;
- self-generated memory vs external evidence / reality monitoring;
- factuality claim decomposition granularity;
- fixed rollout budget allocation and same-temperature-as-same-exploration style questions;
- generic agent trajectory success-vs-length measurement.

Do not revive these by renaming them.

---

# 10. Current raw leads are NOT survivors

Do not inherit any raw seed as a candidate automatically.

Two examples that were left unresolved at handoff:

- **Cross-model token-entropy comparability:** token entropy is often interpreted as uncertainty/exploration, but tokenization/vocabulary differences may make absolute cross-model comparisons invalid. This only becomes Main-sized if it demonstrably changes scientific conclusions/rankings; otherwise it is a textbook metric caveat. Treat as raw pressure, not a candidate.
- **Longitudinal idiolect under LLM writing assistance:** whether the same real author's stable linguistic signature weakens after widespread LLM assistance. This has an Utami-like changed-population structure, but causal identification/treatment proxy is currently weak. Do not promote without a convincing natural design and strong novelty search.

It is completely acceptable to abandon both.

---

# 11. Output behavior for the next round

Search first. Do not make the user choose abstract territories.

As you work, give concise progress updates only when something substantive happens: a promising scientific pressure, a decisive novelty collision, a process correction, or a survivor.

For a serious candidate, report:

- **one-sentence RQ**;
- **where the idea came from** (its independent provenance);
- **why Sasano may like it**;
- **nearest ACL/EMNLP/NAACL Main neighborhood and scope comparison**;
- **nearest-prior novelty check**, including papers that nearly kill it;
- **minimal experiment/data/compute**;
- **main risk**.

Do not flood the user with weak seeds. It is better to report repeated kills and eventually 0 survivors than to preserve a topic whose novelty or scientific width is fake.

The goal is not to satisfy this prompt. The goal is to discover questions that, after serious literature reading, genuinely look like plausible **ACL / EMNLP / NAACL Main research questions that Sasano would want to supervise**.
