# L10 — Data, Gold, and Controlled Experience Design

**Core rule:** this is a mechanism paper. The decisive data must record actual environment outcomes and actual subsequent actions; labels should not be invented by an LLM judge.

---

## 1. Primary controlled substrate — ImplicitMemBench

ACL 2026 ImplicitMemBench:
- 300 high-quality items;
- Learning/Priming–Interfere–Test protocol;
- first-attempt behavioral scoring;
- 17 evaluated models;
- constructs include behavioral preference and inhibition.

Source:
- https://aclanthology.org/2026.acl-long.1301/

Use the released task structure as the first controlled substrate.

## 2. Natural replication — EscapeBench

ACL 2025 EscapeBench provides interactive trajectories with:
- action;
- environment state;
- textual feedback;
- subsequent action.

The error taxonomy includes:
> Useless Repetition — repeating the same action despite failure feedback.

Source:
- https://aclanthology.org/2025.acl-long.39/

Use this only after the controlled mechanism is identified.

## 3. Load-bearing experimental unit

Construct matched experience pairs with the same choice structure.

Example:

### Positive experience
- choose A;
- environment gives unambiguous success;
- interference;
- test A vs B.

### Negative experience
- choose B;
- environment gives unambiguous failure;
- interference;
- test A vs B.

The central factor is:
> outcome valence / behavioral implication,

not task difficulty or wording.

## 4. Four observable stages

For every experience independently query/evaluate:

### Stage 1 — Outcome memory
> What happened when option B was tried?

Gold:
- environment success/failure state.

### Stage 2 — Causal attribution
> Which action/choice caused the outcome?

Gold:
- controlled task causal structure.

Use only cases where the experiment deterministically makes one action responsible.

### Stage 3 — Policy knowledge
> What should be done next time?

Gold:
- repeat successful A / avoid failed B or choose viable alternative, defined by task.

### Stage 4 — Actual first action
Allow the model to act.

Gold:
- behavior implied by the known environment/task.

The key scientific pattern is where accuracy first diverges between positive and negative conditions.

## 5. Targeted interventions

### Attribution intervention
After failure explicitly state:
> B caused the failure.

If behavior recovers:
> attribution was limiting.

### Positive replacement
Compare:
- “do not use B”;
- “use A instead”;
- raw failure only.

If positive replacement wins sharply:
> suppression/negative-specification is limiting.

### Explicit policy reminder
Give:
> you concluded B should be avoided.

If model still chooses B:
> knowledge→action inhibition is limiting.

### Delay/interference
Vary intervening context length/content.

If negative lessons decay faster:
> retention/consolidation asymmetry.

## 6. Controls

### Wording symmetry
Use matched positive/negative wording length and salience.

### Outcome strength
Ensure success and failure feedback are equally explicit.

### Option priors
Counterbalance A/B identities.

### Semantic pressure
Avoid cases where one option is strongly preferred by pretraining unless explicitly measured.

### Difficulty
Use trivial deterministic tasks first; complex agents only for replication.

## 7. Metrics

Per stage:
- positive accuracy;
- negative accuracy;
- signed asymmetry Δ = positive − negative.

Behavior:
- repeat-success rate;
- avoid-failure rate;
- useless-repetition rate.

Intervention:
- recovery after attribution;
- recovery after positive replacement;
- recovery after policy reminder;
- decay vs interference.

Mechanistic sequence:
> Stage 1 → Stage 2 → Stage 3 → Stage 4 transition loss.

## 8. Model scope

Start with:
- 2–3 strong open model families;
- include at least one reasoning model and one standard instruct model.

No need for 17-model replication initially; the parent already establishes breadth.

## 9. Data-validity kill conditions

KILL or reconstruct if:
- positive/negative items differ in difficulty or salience;
- causal responsibility is ambiguous;
- “correct policy” requires author judgment;
- outcome feedback is not explicit;
- asymmetry disappears under matched design across models and only survives in the original benchmark;
- natural EscapeBench replication does not show the same stage bottleneck.

## 10. Data Gate verdict

**YES.**

The controlled environment gives direct outcome/causal/action truth, and the parent phenomenon is already externally established.
