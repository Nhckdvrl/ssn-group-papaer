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

Find a natural, important uncertainty and a plausible route to an independently valuable answer. The problem should make sense without our method. The answer need not be known before starting.

For a rough lead write:

1. One-sentence RQ and a plain example.
2. The best existing explanation or practice.
3. What it leaves unresolved, and why that matters.
4. A candidate idea or scientific operation that could change the answer.
5. The observation that would distinguish it from the existing account.
6. Plausible data and independent scientific units.
7. Closest ownership risk and the consequence of resolving the question.

Keep this short. Do not build a full candidate package for every thought. If there is only an attractive RQ but no contribution path, label it as such rather than promoting it through rhetoric.

## 2. Read Strong Papers for Their Intellectual Progression

Before a normal search round, inspect relevant recent ACL/EMNLP/NAACL papers, prioritizing strong paper identities and pertinent award work. Use top-ML work where it owns the technical question.

Ask what readers believed before, what the paper changed, which operation enabled that change, and how the study developed beyond its first observation. Read results and appendices when assessing actual depth and workload.

A large unexplained table entry is a lead, not a claim to open explanation space. A paper's "future work" is not a novelty certificate. Awards do not confer importance on every follow-up.

Do not imitate titles, three-claim structures, or a hypothesis/probe/patch template. Read for the inferential advance.

## 3. Search Broadly, Not Mechanically

For open-ended search, inspect several genuinely distinct domains or generators. Do not repeatedly instantiate "X is not Y," representation-versus-readout, a favorite intervention, or one fashionable area.

A user-requested bounded recheck of an existing route is not an invitation to start broad topic search.

No survivor quota. Zero strong leads is an acceptable outcome. Search priorities are priors, not universal exclusions: a concrete, important question in a crowded area can survive; obscurity in a quiet area is not novelty.

Retain advisor guidance with its scope: a hard user requirement is binding;
a concern about one project is not automatically a universal gate. Existing
negative search priors include generic Agent/RAG/RL, prompt engineering,
judge/annotation-only studies, generic bias/calibration/hallucination reports,
and benchmark creation without a substantive question. Topics requiring a long
specialist linguistic setup have a naturalness burden. These are priorities,
not categorical exclusions of an independently compelling contribution.

Recurring positive tracks include concrete model computation, classic NLP
problems reopened by new leverage, scientific documents, structured evidence,
and consequential measurement problems. Rotate tracks rather than declaring
one template the only route to a good paper.

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
3. **Calibrate:** read relevant strong work for intellectual advance, decisive evidence, development, and scope.
4. **Generate:** produce compact leads across distinct tracks when the task is open-ended.
5. **Challenge:** test ownership, successful-result inference, naturalness, and contribution size.
6. **Promote selectively:** use the selection document for bounded authorization, not a premature paper endorsement.
7. **Record:** update only the relevant existing documents; new dead parents go to the killed ledger, duplicate hits keep the old KXXX and are noted in the dated search-round record.

A killed route may be reconsidered with qualitatively new leverage, evidence, or literature understanding. A new title or more available GPUs is not such a reason.

## 8. Stop and Handoff Rules

Stop a lead when the remaining answer is trivial, a true collision owns the paper, data cannot plausibly identify it, or a credible contribution path is absent after bounded investigation.

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
