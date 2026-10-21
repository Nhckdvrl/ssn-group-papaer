# Scope-aware Character Editing: executable protocol smoke test

**Status: program validation only.** Four hand-authored independent story units, 16 nested cases (8 change / 8 preserve), each in before/after conditions. This is not a new benchmark, evidence of a model's failure, or a sample of real author preferences.

This fixture probes an original author's targeted revision of a fictional character. The relevant behavior should change in unseen scenes and unrelated choices should remain stable. It is deliberately explicit and therefore at risk of reducing to NLI/instruction following; a real scientific test needs independent authors, original character materials, semantically difficult revisions, strong updated-prompt and CDT baselines, human-permitted multiple outcomes and genuine style/role-play assessment.

Use Python 3.10+ and standard library only:

    python3 -m unittest -v test_scope_probe.py
    python3 scope_probe.py validate --fixtures fixtures.json
    python3 scope_probe.py render --fixtures fixtures.json --out /tmp/role_edit_tasks.jsonl

Only this next command makes OpenAI-compatible API calls (requires permitted endpoint/model):

    python3 scope_probe.py run --tasks /tmp/role_edit_tasks.jsonl --out /tmp/role_edit_responses.jsonl --endpoint http://127.0.0.1:8000/v1 --model YOUR_LOADED_MODEL
    python3 scope_probe.py score --tasks /tmp/role_edit_tasks.jsonl --responses /tmp/role_edit_responses.jsonl

`run` sends **only the messages field**, never the expected labels, and reads optional `OPENAI_API_KEY` from the environment. Check authorization before remote/paid calls; do not commit tokens or model raw outputs. Paired scores are conditioned on whether the pre-edit action was correct; report by story (n=4), not treat 32 requests as independent. Action-choice metrics do NOT measure style, emotional credibility, overall roleplay quality or player experience. No model or player study has been run.

See [E01](../E01-scope-aware-character-edit-baseline-gate.md) and [I01](../../ideas/I01-scope-aware-character-editing.md).

## V1.1 situated-critique adapter (researcher-authored smoke only)

V1 remains immutable. [v11_probe.py](v11_probe.py) reads the same V1 fixtures plus [v11_annotations.json](v11_annotations.json). It renders `original`, `explicit` and `situated` conditions; the last condition uses only a specific rehearsal failure, the author's comment, and a corrected example, **not** the complete abstract edit. A pressure twin is added for one out-of-scope case per story, explicitly sharing its base-case expected decision.

No new model is called by rendering or scoring:

```bash
python3 -m unittest -v test_v11_probe.py
python3 v11_probe.py validate --fixtures fixtures.json --overrides v11_annotations.json
python3 v11_probe.py render --fixtures fixtures.json --overrides v11_annotations.json --out /tmp/role_edit_v11_tasks.jsonl
# Only an explicitly invoked model runner makes API calls, for example:
python3 scope_probe.py run --tasks /tmp/role_edit_v11_tasks.jsonl --out /tmp/role_edit_v11_responses.jsonl --endpoint http://127.0.0.1:8000/v1 --model YOUR_LOADED_MODEL
python3 v11_probe.py score --tasks /tmp/role_edit_v11_tasks.jsonl --responses /tmp/role_edit_v11_responses.jsonl --out /tmp/role_edit_v11_score.json
```

In-situ corrections **do not uniquely imply** many of the oracle's hidden edit boundaries. The v1.1 scorer therefore separates `author_intent_agreement` from strictly interpretable `supported` cases, and returns paired before/after comparisons for each mode. No `thought` is requested; physical/narrative `action_id` and `utterance` remain separate. The tool does **not** measure tone or player experience. `pressure` is a dependent perturbation of the same scene, not an independent story/quadrant.

This only adds a *measurement design*; the honest research sample count is still **4 developer-authored stories**, not an 8–10 story research dataset. Genuine author materials, multi-solution adjudication, independent style evaluation, proper strong baselines and calibration remain necessary before any scientific conclusion.
