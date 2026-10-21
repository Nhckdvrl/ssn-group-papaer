# Scope-aware Character Editing: executable protocol smoke test

**Current status: E01 real baselines and E02 controls completed; see the results section below. Historical V1 protocol:** Four hand-authored independent story units, 16 nested cases (8 change / 8 preserve), each in before/after conditions. This is not a new benchmark, evidence of a model's failure, or a sample of real author preferences.

This fixture probes an original author's targeted revision of a fictional character. The relevant behavior should change in unseen scenes and unrelated choices should remain stable. It is deliberately explicit and therefore at risk of reducing to NLI/instruction following; a real scientific test needs independent authors, original character materials, semantically difficult revisions, strong updated-prompt and CDT baselines, human-permitted multiple outcomes and genuine style/role-play assessment.

Use Python 3.10+ and standard library only:

    python3 -m unittest -v test_scope_probe.py
    python3 scope_probe.py validate --fixtures fixtures.json
    python3 scope_probe.py render --fixtures fixtures.json --out /tmp/role_edit_tasks.jsonl

Only this next command makes OpenAI-compatible API calls (requires permitted endpoint/model):

    python3 scope_probe.py run --tasks /tmp/role_edit_tasks.jsonl --out /tmp/role_edit_responses.jsonl --endpoint http://127.0.0.1:8000/v1 --model YOUR_LOADED_MODEL
    python3 scope_probe.py score --tasks /tmp/role_edit_tasks.jsonl --responses /tmp/role_edit_responses.jsonl

`run` sends **only the messages field**, never the expected labels, and reads optional `OPENAI_API_KEY` from the environment. Check authorization before remote/paid calls; never commit credentials or large raw assets. The user-authorized first runs are stored as small lossless archives with raw hashes. Paired scores are conditioned on whether the pre-edit action was correct; report by story (n=4), not treat 32 requests as independent. Action-choice metrics do NOT measure style, emotional credibility, overall roleplay quality or player experience. No model or player study has been run.

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

## V1.2 strict-scoring guard (2026-10-21)

The input dataset and all **60 tasks are unchanged**. A developer-authored `situated_scope=supported` tag is only a hypothesis about reasonable transfer, **not an independent author label**. For situated cases, the scorer now counts a case toward `strictly_scored` only when **both** `author_verified=true` and `decision_identifiable=true` are attached to the case's task metadata. Neither is available for this toy fixture: consequently the correct **strict situated denominator is zero**. `author_intent_agreement_total` remains a descriptive comparison with the developer's full-rule oracle.

An informative character background can bias plausible edit scopes but cannot automatically identify the intended rule uniquely; an author's correction may itself override the old biography. `explicit` vs `situated` differs in information provided, so it is not an equal-information algorithm comparison. The pilot measures action choices but does not evaluate the generated `utterance` tone/style; inference errors and output formatting errors must be reported separately. No LLM model has been run as part of this update.

## V1.3 dual synthetic / identifiability scoring (2026-10-21)

The V1.1 **60 input requests are unchanged**. Evaluating them yields two different kinds of statements, deliberately not conflated:

- **`synthetic_oracle_by_mode`**: `n_requested`, `n_received`, `n_valid_action`, `n_action_oracle_match`, `oracle_match_per_received`, and `oracle_match_given_valid_action` for `original / situated / explicit`. These numerators are valid against the **developer's known, fully specified generating rule** even if the model input was underdetermined. They DO NOT imply that the situated evidence uniquely entails that rule. Disaggregate change/preserve via `synthetic_oracle_by_bucket`.
- **`n_certified_situated` and `metrics[].n_scored`**: available only with a stated hypothesis space and decision-consensus argument or independently validated author labels. Current developer labels lack this evidence, so the Situated strict denominator remains zero; **the synthetic-oracle score is NOT zero or discarded**.

The report additionally exposes `complete`, responses received, valid action counts, model errors, utterance presence, and separately the 12 *dependent* pressure/base comparisons (`pressure_pairs`; four scene pairs times three input modes). Missing requests are not silently counted as poor semantic decisions: oracle match per received response is reported with its denominator. The script still **does not grade style**, and a `thought` field is not needed.

A real likelihood of a hypothesis cannot be inferred from the fact that the developer picked it; a generative benchmark can score recovery of its own `S*` yet cannot alone prove unique author-intent inference. See [E01](../E01-scope-aware-character-edit-baseline-gate.md).

## 2026-10-21 实际运行与离线复算

[E01报告](../../results/e01/REPORT.md)、[E02报告](../../results/e02/REPORT.md)是当前状态；上面的V1–V1.3说明保留运行前设计。三模型各60条、Step截断恢复1条、Qwen普通控制64条，共245次调用。原renderer、fixtures和双轨scorer未修改。

- `run_baseline.py`：现有HF环境本地推理；或固定Step Plan endpoint，不支持现金回退、不跟随重定向、不会把gold发给模型。保存完整响应/模型hash/usage/finish reason；拒绝覆盖旧运行。Step密钥使用`STEPFUN_API_KEY`或隐藏终端输入。
- `analyze_baseline.py`：保留严格JSON轨，另报告只去完整外层围栏的动作轨；支持仅对原length请求的预算恢复。可直接读取压缩raw，无需模型或联网。
- `followup_controls.py`：E02输入构造、实际模型人物卡应用和同信息比较。原卡/explicit的模型输出是复用参照，不新增调用。
- `make_casebook.py`：全量台词排版供案例审阅，不打主观分数。`metadata.json`固定各运行版本、配置与具体命令；`results/e01/source/`保存启动时源码hash快照。

在仓库根执行（仅CPU复算，无API/GPU调用）：

```bash
python3 -m unittest discover -s workbench/game-npc-agents/experiments/scope_edit_pilot -v
for model in qwen3_8b llama31_8b step5; do
  python3 workbench/game-npc-agents/experiments/scope_edit_pilot/analyze_baseline.py \
    --tasks workbench/game-npc-agents/results/e01/tasks.jsonl \
    --run workbench/game-npc-agents/results/e01/$model
done
python3 workbench/game-npc-agents/experiments/scope_edit_pilot/analyze_baseline.py \
  --tasks workbench/game-npc-agents/results/e01/tasks.jsonl \
  --run workbench/game-npc-agents/results/e01/step5 \
  --recovery workbench/game-npc-agents/results/e01/step5_recovery
python3 workbench/game-npc-agents/experiments/scope_edit_pilot/followup_controls.py summarize \
  --e01 workbench/game-npc-agents/results/e01 --out workbench/game-npc-agents/results/e02
```

原始245条响应的`.jsonl.gz`合计109,839 bytes；全部可从Git取回，解压内容sha256见`results/raw_manifest.json`。展开副本在同目录被git-ignore；权重不进Git，按metadata的模型ID/revision重新取得，或使用本机`/home/xiang/.cache/huggingface/hub/`。无真人参与，台词审查是执行agent描述性阅读。
