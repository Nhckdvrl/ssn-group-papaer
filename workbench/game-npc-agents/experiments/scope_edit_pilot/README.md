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
