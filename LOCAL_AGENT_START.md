# Local Agent Start — Current Execution Handoff

**Date:** 2026-09-09  
**Target:** NAACL Main  
**Mode:** RESEARCH EXECUTION  
**Approved paper mainline:** NONE  
**Default portfolio priority:** L08 unless the user explicitly selects another candidate.

> Give this file to the local research agent when starting work.

The current portfolio contains eight active candidates. Do **not** generate new topics during ordinary execution unless the user explicitly reopens topic search.

---

# 1. Candidate selection rule

The user’s explicit task selection overrides the default priority.

Examples:
- if the user says “do L11,” work on good/L11_TASK_GRADIENT_PRESSURE/;
- if the user says “do L12,” work on good/L12_REASONING_DECISION_INVARIANCE/;
- if the user says “do L11/L12,” treat them as two separate subprojects and keep their artifacts separated;
- otherwise the current default priority remains L08.

Do not silently redirect explicit L11/L12 work back to L08.

---

# 2. Mandatory reading

Before experiments:

1. RESEARCH_EXECUTION.md
2. the selected candidate’s canonical package:
   - README.md
   - DATA_AND_GOLD.md
   - RELATED_WORK_AND_NOVELTY.md
   - RESEARCH_PLAN.md
   - PILOT_CARD.md

Then inspect current code/data/results already present in that candidate directory before creating anything new.

The canonical package defines:
- the scientific question;
- evidence standard;
- current novelty boundary;
- Main-level identity;
- current cheapest decisive starting point.

It does **not** freeze the final method or answer.

---

# 3. Repository safety

During execution:

> **Only modify the concrete candidate directory being worked on.**

For L11: good/L11_TASK_GRADIENT_PRESSURE/

For L12: good/L12_REASONING_DECISION_INVARIANCE/

If executing both, keep code/data/results/claims separate inside their own directories.

Do not edit root workflow/status documents during ordinary experiment work.

Inside the selected directory, create or maintain only useful execution artifacts such as:
- CLAIMS.md;
- EXPERIMENTS.md;
- RELATED_WORK.md or updates to the canonical novelty file;
- DATA.md or updates to the canonical data file;
- src/;
- scripts/;
- configs/;
- results/;
- reproducibility/environment notes.

Do not create files mechanically if existing files can carry the information clearly.

---

# 4. Scientific flexibility rule

The candidate package should **constrain the science, not pre-write the answer**.

Hard constraints:
- preserve the natural research question;
- evidence must really identify the claim;
- novelty is judged at the paper level;
- outcome must remain scientifically meaningful under multiple plausible results;
- the developing work must continuously align to strong ACL/EMNLP/NAACL Main papers.

Flexible:
- exact model/checkpoint after feasibility audit;
- exact probe/patching/gradient metric;
- exact mechanistic account;
- exact experiment ordering;
- exact paper section structure;
- whether the final story becomes mechanism-first, measurement-first, boundary-first, or a stronger reconstruction.

If evidence points to a better explanation, reconstruct around it. Do not force the original account.

---

# 5. Continuous top-conference alignment

Before every new load-bearing claim or major experiment:

1. refresh the closest current literature;
2. inspect the strongest structurally relevant ACL / EMNLP / NAACL Main papers;
3. use Best / Outstanding / Best Theme work as high-end calibration where useful;
4. inspect ICLR / ICML / NeurIPS when the paper identity is mechanistic, optimization, representation, or measurement-heavy.

Do not ask whether every ingredient is unprecedented.

Ask whether the **full developing paper** still owns:
> framing/narrative + decisive operation + central conclusion + consequence.

Run the reviewer-compression test:
> **“This is just ______.”**

A shared parent/method/component is allowed. A prior paper that accurately compresses the whole final paper is not.

---

# 6. Execution discipline

Before every substantive experiment, record:
- experiment ID;
- linked claim/question;
- why the experiment is necessary;
- dataset/subset;
- model/revision;
- intervention/conditions;
- metrics/statistical tests;
- expected informative outcome branches;
- kill/reconstruct implications.

After every run, record:
- exact command/config;
- environment/model version;
- raw result path;
- summarized result;
- uncertainty where relevant;
- interpretation;
- what claim changed.

Maintain the chain:
> **claim → experiment → config/code → data → raw result → conclusion**

---

# 7. L11-specific guardrails

Canonical directory: good/L11_TASK_GRADIENT_PRESSURE/

Established parent:
> multi-task RL can produce very different task gradient magnitudes that do not simply track learning gain.

Do not rediscover that phenomenon.

Scientific center:
> **What makes one task optimization-loud, what does raw task-gradient magnitude actually measure, and when is it a misleading cross-task learning-pressure signal?**

Current mechanism families are hypotheses, not requirements:
- per-example/token score sensitivity;
- within-response cancellation;
- across-example update coherence;
- parameter-space vs function-space miscalibration;
- another stronger mechanism.

Main failure mode:
> gradient imbalance → normalize/surgery/sample differently → +X%.

That is below the intended paper identity unless it follows from a new scientific diagnosis.

The first pilot should recover one clean parent contrast and resolve the cheapest meaningful source-of-loudness uncertainty before scaling.

---

# 8. L12-specific guardrails

Canonical directory: good/L12_REASONING_DECISION_INVARIANCE/

Established parent:
> ACL 2026 Outstanding work reports that reasoning-oriented models are substantially less sensitive to several equivalent risky-choice presentations.

Do not rediscover that behavioral result.

Scientific center:
> **Does reasoning-oriented post-training create a shared/canonical task representation, or does framing/context survive internally while losing influence over the final decision policy?**

Important checkpoint-identification rule:

For OLMo 3, do **not** describe Instruct-SFT → Think-SFT as a sequential training transition.

The verified design is:
- common base: allenai/Olmo-3-7B;
- sibling branch: allenai/Olmo-3-7B-Instruct-SFT;
- sibling branch: allenai/Olmo-3-7B-Think-SFT;
- optional later DPO/final checkpoints within each branch.

Therefore reason from:
> **base→Instruct change vs base→Think change**

and use later within-branch stages only if they sharpen identification.

Current mechanism families are hypotheses, not requirements:
- representational canonicalization;
- policy/readout override;
- inference-time deliberation;
- arithmetic/specialization boundary;
- another stronger mechanism.

Probe-only work is not enough for the intended final mechanism claim.

---

# 9. Current portfolio

- L03 — PILOT-AUTHORIZED
- L06 — SERIOUS / PILOT-READY
- L07 — SERIOUS / DATA AUDIT FIRST
- L08 — SERIOUS / default current priority
- L09 — SERIOUS
- L10 — SERIOUS
- L11 — PILOT-AUTHORIZED
- L12 — PILOT-AUTHORIZED

The user may change priority at any time.

---

# 10. Required pilot verdict

A pilot phase should end with:

- **GO**
- **CONDITIONAL**
- **NO-GO**

Return:
1. data/intervention validity;
2. exact result with uncertainty;
3. which scientific accounts were strengthened/weakened;
4. strongest current reviewer compression;
5. fresh novelty status;
6. Main-level paper shape that still remains;
7. exact reproducibility pointers;
8. next smallest decisive experiment.

Kill/reconstruct when:
- data/intervention cannot identify the claim;
- current literature owns the resulting paper identity;
- surviving result is trivial;
- no meaningful Main-level paper shape remains.

A preferred hypothesis losing is **not** itself a kill condition.
