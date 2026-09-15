# 2026-09-15 — SEARCHER HANDOFF V: RECALIBRATED

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS  
**Current open-search state:** no new Mainline survivor from Rounds V–VI. L42 remains `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`.

This document is intentionally compact. It is a control file for the next searcher, not another 50-item constitution.

---

# 1. Main diagnosis: the process has improved, but it still has a structural failure mode

The recent `0 survivor` rounds are **not mainly evidence that the quality bar is too high**. The generated mother questions are now often genuinely important and easy to state; many died because 2025–2026 strong groups had already asked almost exactly the same question. That is real landscape difficulty.

But the searcher still has a structural bias:

> **good mother question → exact-owner search → owner exists → kill → switch wall**

This is much better than `paper → limitation → gap`, but it can still turn us into a **high-quality question reviewer rather than a problem creator**.

The next correction is not to lower novelty. It is to change what we search for.

We should maintain two things separately:

1. **Standing important problems** — questions that would matter even if we had no method yet.
2. **New leverage** — a 2025–2026 model family, intervention, theorem, training regime, causal instrument, or empirical capability that changes what is identifiable now.

The highest-value search object is their intersection:

> **important old/standing question + genuinely new leverage that makes it answerable now, where the leverage paper itself did not already answer the old question.**

This is closer to how strong researchers operate: keep important problems alive, then recognize when a new clue suddenly bears on one of them.

---

# 2. Specific process problems to fix

## A. Do not treat “owner exists” as a binary kill

Distinguish:

- **Exact owner:** same scientific claim + same regime + essentially same identifying contrast. → KILL.
- **Mother-problem owner:** same broad question, but current answer rests on a weak assumption, different regime, or non-identifying evidence. → NOT automatically dead.
- **Adjacent lineage:** related concept/method, but not the same estimand. → definitely not a kill by itself.

Do not keep shrinking a formulation merely to escape an exact owner. But also do not reject a strong question just because somebody has worked on its broad parent problem.

## B. Stop learning “paper shapes” as generators

We have repeatedly overfit to the newest admired move:

`anomaly→mechanism`, `wrong quantity`, `hidden assumption`, `old law→new regime`, `A+B`, etc.

Strong papers show that many moves can work. Their value is to calibrate **taste and contribution magnitude**, not to provide templates.

When 2–3 consecutive ideas have the same provenance shape, stop generation and recalibrate.

## C. Current search is too reactive to the newest literature

Recent work should often be treated as a **leverage bank**, not only an owner bank.

To discover standing problems, read more longitudinally:

- classic/durable papers repeatedly cited by modern work;
- strong authors across several years;
- introductions + Related Work, not only abstracts;
- talks, research statements, interviews, lab blogs;
- old disagreements that modern papers keep invoking without resolving.

Do not spend all search budget on 2026 papers whose obvious big questions are naturally already occupied.

## D. Breadth is necessary, but intimacy is also necessary

Recent rounds moved across many scientific objects. That successfully prevents local tunnel vision, but too-rapid wall switching can prevent the searcher from understanding what the field itself considers the real unresolved “big bones.”

Keep a broad bank of ~10–20 important problems, but at any moment choose only a few promising pressure pools for deeper lineage reconstruction. Do not candidateize every pressure immediately.

## E. Our negative criteria became slightly too constitutional

`low description length`, `both-way belief change`, `non-obviousness`, `natural data`, etc. are excellent preferences, but not every one is a mandatory gate.

Strong work can be asymmetric: one outcome may be much more surprising than the other. A question may need two sentences of setup. A new method can be central if it finally identifies an old important question.

The primary test is not checklist perfection. It is:

> **If the paper succeeds, what important scientific belief changes?**

## F. Preserve a small “fragile idea” budget

Original projects can initially look odd or receive negative expert feedback. Do not optimize the search so hard that every idea must look obviously publishable before any cheap information is gathered.

Keep 1–2 high-upside, uncertain ideas alive long enough for a cheap falsification / literature / toy check when the mother question is genuinely important.

---

# 3. Revised definition of a strong topic

The core criteria are only five.

### 1. Independent importance

The question matters **before** introducing our probe, SAE, metric, dataset, benchmark, or special intervention.

### 2. Scientific consequence

A successful answer changes a meaningful belief about foundation models: what computation they use, what training changes, what architecture buys, what law governs them, or what existing evidence actually implies.

Ask:

> If another top group published the cleanest version of this paper tomorrow, would we genuinely be excited to read it?

### 3. Genuine uncertainty

A knowledgeable reader should not be able to derive the answer immediately from standard theory or from the two parent papers.

“Not previously tested” is not enough.

### 4. Why now / new leverage

There must be a credible reason this question is answerable **now** when it was not before:

- new model regime;
- new causal intervention;
- new theoretical characterization;
- new training setup;
- new controllable family;
- new natural phenomenon;
- or a modern assumption change that makes an old law genuinely nontrivial again.

### 5. Reasonable decisive attack

We need a plausible experiment/theorem/intervention that distinguishes the important explanations at useful resolution.

The attack need not already be fully engineered, but it cannot be “run many models and hope a pattern emerges.”

---

# 4. Strong preferences — NOT rigid gates

Prefer:

- a question compressible to one or two sentences;
- natural data/tasks over bespoke benchmark construction;
- results that are interesting in more than one plausible direction;
- a clean minimal pilot before months of compute;
- a growth path from decisive E01 → law/mechanism/theory → limited external validation;
- contribution that survives removing model-zoo breadth.

Deprioritize:

- benchmark/dataset/RAG/evaluator/data-centric papers;
- “method X on domain Y” without a new scientific statement;
- generic probe/SAE/steering papers where the instrument creates the importance;
- tiny distinctions extracted from a mature owner program;
- questions whose best-case conclusion is merely `X affects Y`;
- projects that are Main-level only if one lucky reversal occurs.

---

# 5. How strong-paper calibration should work

Do not only read award papers and extract their rhetorical move.

For each fresh strong paper / lineage, do **predict-before-reading**:

1. Before reading the full result, what question would I have asked from the prior literature?
2. What result would I have predicted?
3. What experiment/theory would I have considered sufficient?
4. Why did the real authors choose a different scientific object, comparison, or level of explanation?
5. What existed **before** this paper that made the idea possible?

The prediction error is the useful signal.

Calibrate against diverse strong identities, e.g. papers that:

- challenge a dominant assumption;
- redefine the comparison quantity;
- expose a training/deployment mismatch;
- turn a classical law into a modern conditional law;
- lower the explanatory level with a simple model;
- use a new causal instrument to answer a standing question;
- connect theory and a real empirical design surprise.

Never convert this list into a generator menu.

---

# 6. Next-session search loop — short and flexible

### Phase A — refresh the problem bank

Read a diverse sample of ACL/EMNLP/NAACL strong Main + TACL + ICLR/ICML/NeurIPS strong/award work, plus at least one strong-author lineage / research-advice source.

Extract **standing questions/frictions**, not paper gaps.

### Phase B — refresh the leverage bank

Separately collect recent things that changed what can be identified: new causal tools, model families, formal results, training regimes, controllable checkpoints, matched architectures, etc.

### Phase C — match, do not autocomplete

Ask which leverage actually changes the answerability of which standing problem.

Do not require the connection to look like a familiar template.

### Phase D — owner map only after the question is strong

For a promising intersection, map:

- exact scientific claim;
- exact regime;
- exact quantity/estimand;
- exact identification strategy.

Kill only if a strong owner substantially matches all of these, or if the remaining difference is merely cosmetic/instrumental.

### Phase E — once SERIOUS, finish it

Judge importance, owners, prediction entropy, why-now leverage, identification, feasibility, and best-case paper identity before switching walls.

### Heartbeat

After roughly 1–2 serious audits, 3–5 dead walls, or obvious generator repetition, recalibrate on fresh strong work from a **different research school**.

The searcher is explicitly allowed to change this process when real strong-paper evidence shows it is drifting.

---

# 7. Current state / anti-resurrection

- **L42 — Does Scale Reward Syntax?** remains `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`. Do not generate L42 sequels during open search.
- Search Rounds V and VI produced **0 new survivor**, after broad/deep searches. Their dead walls should not be cosmetically revived.
- Two long-term WATCH ideas remain non-candidates: policy-equivalent reward signals selecting different learned computation; and a possible shared value-of-computation currency across `think / tool / answer`. Both currently lack sufficiently clean identification / independent paper identity.
- Latest unarchived search checked **variable / role–filler binding** and found a mature mechanism lineage (Binding ID → variable binding → dynamic rebinding). Do not reopen as “larger/natural model binding.”
- The next tentative surface had been mathematical/equivalence invariances, but **this is not an assigned direction**. It should be pursued only if it emerges from a real standing problem + leverage match.

---

# 8. The one meta-question to keep repeating

> **Am I finding a question that strong researchers would have wanted answered before seeing my method — and whose answer became newly possible now — or am I merely generating the next experiment after a recent paper?**

And one second question, equally important:

> **If an exact parent exists, is the problem truly owned — or does the new regime/leverage make a scientifically different answer possible?**

The next session is not a process-editing session. Use this document as a compact prior, then **go search for problems**. If fresh evidence from excellent papers or researchers contradicts this process, update the process rather than obeying it mechanically.