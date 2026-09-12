# Research Topic Search: Find Questions with a Contribution Path

Updated: 2026-09-12. Target: ACL / EMNLP / NAACL Main; strong Main and award work provide calibration.

This governs search, not experiment execution. [The playbook](TOPIC_SEARCH_PLAYBOOK.md) supplies optional generators. [Selection](RESEARCH_TOPIC_SELECTION.md) evaluates concrete candidates. [Execution](RESEARCH_EXECUTION.md) governs development after bounded authorization.

## 0. Mandatory Anti-Resurrection Check

Before generating, naming, or externally searching a new lead, first inspect the anti-resurrection record:

- `failed/KILLED_LEDGER.md` for the scientific parent, estimand, failure mode, and reopen fence;
- archived/no-go packages under `candidates/` when the lead resembles a previous candidate;
- `Nhckdvrl/Interpretability-try` when the proposed question, mechanism, intervention, or dataset may inherit earlier mechanistic work.

Search by the **scientific object, estimand, decisive operation, and nearest synonyms**, not only by a proposed title. If a lead matches a killed route, it must state **`Not KXXX because ...`** and identify qualitatively new leverage that changes the inference or contribution. A new dataset, model, prompt, paper title, narrower mechanism, historical version, or cleaner implementation is not enough by itself. If that case cannot be made, discard the lead before deep literature search or compute.

Do not assign a new kill ID to a rediscovered parent. Record it as a duplicate hit on the existing KXXX. At the end of a search round, every seriously investigated rejection must be recorded either in the killed ledger (new parent) or as an explicit duplicate hit in the dated search-round record. This check precedes, rather than replaces, fresh external novelty search.

## 1. Search for More Than an Interesting RQ

Find a **natural scientific uncertainty** and a plausible route to an independently valuable answer. Natural does **not** mean everyday, layperson-friendly, or explainable without domain knowledge. A question may be technical, mathematical, linguistic, statistical, scientific, or domain-specific.

Natural means the scientific object and uncertainty exist **before our proposed benchmark, prompt, intervention, toy construction, or method**. A domain expert should recognize why the question follows from the field's theory, evidence, practice, unresolved contradiction, measurement problem, or empirical regularity. The experiment may be highly controlled or artificial; the **question should not be reverse-engineered from the experiment**.

A plain example is only a communication aid when one is useful, not a selection gate. Do not penalize a strong research question merely because it lacks a lifestyle example or requires technical background.

For a rough lead write:

1. One-sentence RQ; optionally one compact scientific/domain example if it clarifies the object.
2. The best existing explanation or practice.
3. What it leaves unresolved, and why that matters.
4. A candidate idea or scientific operation that could change the answer.
5. The observation that would distinguish it from the existing account.
6. Plausible data and independent scientific units.
7. Closest ownership risk and the consequence of resolving the question.

Keep this short. Do not build a full candidate package for every thought. If there is only an attractive RQ but no contribution path, label it as such rather than promoting it through rhetoric.

## 2. Read Strong Papers for Their Intellectual Progression **and Their Origin**

Before a normal search round, inspect relevant recent ACL/EMNLP/NAACL papers, prioritizing strong paper identities and pertinent award work. Use top-ML work where it owns the technical question.

Ask what readers believed before, what the paper changed, which operation enabled that change, and how the study developed beyond its first observation. Read results and appendices when assessing actual depth and workload.

A large unexplained table entry is a lead, not a claim to open explanation space. A paper's "future work" is not a novelty certificate. Awards do not confer importance on every follow-up.

Do not imitate titles, three-claim structures, or a hypothesis/probe/patch template. Read for the inferential advance.

### 2.1 Topic Provenance Card

For each especially useful Best / Outstanding / strong Main paper, record **where the question came from**, not only what the final paper did:

- **Scientific ancestry:** the classical problem, older theory, empirical regularity, professional practice, or field assumption that predates the current LLM fashion cycle.
- **Immediate pressure:** the concrete contradiction, unexplained robust observation, measurement bottleneck, hidden assumption, weakly evidenced public claim, or real workflow failure that made the question live.
- **Why now:** what new model regime, representation, natural dataset, intervention, causal design, or measurement operation makes the old uncertainty answerable now.
- **First decisive operation:** the cheapest observation/intervention that could have changed the authors' view before the full paper existed.
- **Growth path:** how that first result became a larger explanation, boundary, law, consequence, or intervention.
- **Transferable origin mechanism:** the reusable way of *finding* the problem. Transfer this generator to quieter scientific objects; do not copy the paper topic.
- **Fashion density:** whether the paper's identity depends on a currently saturated label or instead on a scientific pressure that would remain interesting if the fashionable system name disappeared.

A strong provenance usually reaches further back than “Agents/RAG/RL became popular.” A fashionable technology can provide **new leverage**, but fashion itself is not scientific ancestry.

Useful recurring provenance patterns include:

- old problem/law + previously missing measurement;
- old theoretical debate + genuinely new model regime;
- important causal estimand + an identification bottleneck solved by a mature design from another field;
- stable engineering anomaly + no satisfactory explanation;
- mathematically convenient / conventional field assumption + a consequential counterexample;
- proxy metric + a more consequential target quantity;
- strong public/theoretical claim + surprisingly weak direct evidence;
- real professional workflow + natural process data;
- cheap destructive/control intervention + an unexpectedly stable effect worth explaining.

## 3. Search Broadly, Not Mechanically — and Penalize Fashion Density

For open-ended search, inspect several genuinely distinct domains or generators. Do not repeatedly instantiate "X is not Y," representation-versus-readout, a favorite intervention, or one fashionable area.

A user-requested bounded recheck of an existing route is not an invitation to start broad topic search.

No survivor quota. Zero strong leads is an acceptable outcome. Search priorities are priors, not universal exclusions: a concrete, important question in a crowded area can survive; obscurity in a quiet area is not novelty.

Current negative search priors are stronger for **very hot directions** such as generic Agent/long-term-memory/RAG/RL, prompt engineering, judge/annotation-only studies, generic bias/calibration/hallucination reports, and benchmark creation without a substantive question. The problem is not merely competition: in saturated areas, a natural RQ is more likely to be reviewer-compressed into an existing parent, and the paper identity is more likely to depend on a particular harness/framework rather than on a durable scientific object.

For an open-ended topic search, strongly deprioritize a lead when removing the words **Agent / memory framework / RAG / RL / judge / harness** makes its contribution disappear. Harness-dependent results carry an additional burden: the inference should survive reasonable framework choices, and natural data/gold should exist independently of the harness. Do not spend search budget building infrastructure merely to discover whether the scientific question exists.

These are strong priors, not absolute bans: a crowded area can still enter if the scientific question clearly predates and transcends the fashionable implementation and there is a decisive framework-independent operation.

Topics requiring a long specialist linguistic setup also have a naturalness burden. A classical linguistic or philosophical distinction is useful only when it exposes a broader modern computation, inference, measurement, or representation problem; “does the LLM know the distinction?” is normally too weak.

Recurring positive tracks include concrete model computation, classic NLP/scientific problems reopened by new leverage, scientific documents, structured evidence, consequential measurement problems, and quiet domains with mature natural gold. Rotate tracks rather than declaring one template the only route to a good paper.

Question first does not mean methods are irrelevant to discovery. A new operation can reveal an answerable old question. Reject method-first work when the problem exists only to showcase the tool.

## 4. Anomalies Lower One Risk, Not All Risks

Established anomaly -> unresolved explanation is a useful generator, not the privileged definition of research.

Audit separately:

- Is the parent phenomenon credible in the regime we can study?
- Is a consequential explanation actually unresolved?
- Would our operation separate explanations rather than reproduce a generic fact?
- Does the answer have an independent contribution after direct follow-ups?

New phenomenon discovery is allowed through principled exploration and validation. Do not demand that every outcome remain publishable. Require informative decisions, including stopping.

## 5. Data and Identification Enter Before Attachment

For each serious lead, ask what observation, gold, manipulation, or intervention identifies the proposed quantity.

Prefer natural existing data when it fits. Minimal controlled construction is legitimate when it gives cleaner leverage. Avoid elaborate synthetic worlds, circular LLM-generated gold, or variables defined to make the hypothesis win.

Distinguish the natural object, the measured proxy, and the inference. List what the manipulation changes. A plausible source does not automatically validate the construct.

Before investing in execution, apply selection's successful-result test: even with the desired effect, could the main interpretation still be unsupported?

## 6. Two-Sided Novelty Search

Search classical parents, direct recent neighbors, alternative terminology, and work that owns the proposed explanation rather than just the dataset. Refresh on material claim mutation.

Verify primary sources, versions, and publication status. A search miss is not evidence of priority. An abstract may establish a possible neighbor; inspect the relevant full-text operation before declaring full collision.

Write both the strongest compression and the strongest surviving contribution.

- Familiar ingredients do not prove that the relationship is known.
- An untested combination does not prove the relationship matters.
- A new model/domain can be important if it changes a substantive answer, not just coverage.
- A new name or broader abstraction does not enlarge an unchanged result.
- Distinguish direct ownership, insufficient significance, and unresolved evidence.

Use bounded literature review. Do not indefinitely refine wording to avoid every neighbor, or kill a natural contribution merely because its supporting concepts are familiar.

## 7. Round Workflow

1. **Refresh:** inspect current user scope, dated portfolio, candidate status, `failed/KILLED_LEDGER.md`, nearby archived routes, relevant `Interpretability-try` history, and remote changes.
2. **Anti-resurrection:** for each prospective lead, record the closest KXXX/archived route and why the lead is or is not a genuine reopen.
3. **Calibrate:** read relevant strong work for **topic provenance**, intellectual advance, decisive evidence, development, and scope.
4. **Generate:** transfer the *origin mechanisms* of strong papers into several quieter scientific tracks; do not copy their subject labels.
5. **Challenge:** test ownership, successful-result inference, scientific naturalness, fashion/harness dependence, and contribution size.
6. **Promote selectively:** use the selection document for bounded authorization, not a premature paper endorsement.
7. **Record:** update only the relevant existing documents; new dead parents go to the killed ledger, duplicate hits keep the old KXXX and are noted in the dated search-round record.

A killed route may be reconsidered with qualitatively new leverage, evidence, or literature understanding. A new title or more available GPUs is not such a reason.

## 8. Stop and Handoff Rules

Stop a lead when the remaining answer is trivial, a true collision owns the paper, data cannot plausibly identify it, a credible contribution path is absent after bounded investigation, or the scientific identity collapses into a saturated harness/framework choice.

Do not discard solely because the expected sign is uncertain: that may be the reason to investigate. Do not promote solely because the parent phenomenon is established.

Formal selection receives the RQ **and** candidate idea/operation **and** prospective contribution, with unresolved risks. It need not receive a finished answer.

Use existing locations:

- Portfolio and priorities: CURRENT_SEARCH.md, with dates and links rather than duplicated run instructions.
- Candidate decisions/evidence: concrete candidate package.
- Archived-route memory: existing failed ledger when an archive decision is authorized.
- Reusable generators: TOPIC_SEARCH_PLAYBOOK.md.
- Durable process changes: these root documents only during an authorized workflow revision.

## 9. Durable Lesson from L12

A strong question can survive while a sequence of proposed paper identities fails. Search should not merely find another attractive label for inherited experiments. Ask what new idea would explain or predict something the old account cannot, and what operation could establish it.

Equally, avoid the reverse shortcut: several nearby owners do not prove every possible synthesis is owned. A bounded review may conclude "no sufficiently valuable, identifiable contribution path found" without claiming that the entire RQ is dead.

**Search for a worthwhile answerable uncertainty, a credible way to resolve it, and a reason the answer would matter. None substitutes for the others.**
