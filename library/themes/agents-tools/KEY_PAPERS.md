# Key Papers — 智能体、工具与交互（Agents / tools / interaction）

从 `library/KEY_PAPERS.md` 按题材拆出（2026-09-30），ID 与内容保持不变。标签含义见 `../../KEY_PAPERS.md`。


## Interactive agents / evolving task state

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AG19 | **LLMs Get Lost In Multi-Turn Conversation** (ICLR 2026) | PARENT / BEHAVIOR | Strong parent showing that competence under a fully specified task can collapse when the same information arrives interactively; useful baseline for separating static capability from state maintenance/recovery across turns. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/59f6421e64707225fdf5b28840679a07-Abstract-Conference.html |
| AG20 | **LLMs Get Lost in Evolving User Intent** (2026) | FRONTIER / ARTIFACT | Extends multi-turn pressure from incremental disclosure to revisions and goal/function changes; useful ownership boundary for any work on persistent task-state revision. | https://arxiv.org/abs/2607.20734 |
| AG21 | **U-Fold: Dynamic Intent-Aware Context Folding for User-Centric Agents** (Findings ACL 2026) | SUCCESSOR / METHOD | Treats changing user intent as a context-management problem rather than ordinary summarization; important evidence that state revision is already becoming an explicit systems object. | https://aclanthology.org/2026.findings-acl.897/ |
| AG22 | **Uncertainty-Aware Clarification in LLM Agents with Information Gain** (ICML 2026) | PARENT / METHOD | Strong clarification parent: turns underspecification into a decision problem over whether asking is worth the interaction cost; useful boundary against rediscovering generic clarification. | https://proceedings.mlr.press/v306/deng26l.html |
| AG23 | **When and What to Ask: AskBench and Rubric-Guided RLVR for LLM Clarification** (Findings ACL 2026) | PARENT / BENCHMARK / ARTIFACT | Separates intent-deficiency and false-premise clarification and supplies a current strong baseline; important evidence that “agents should ask clarifying questions” is already crowded. | https://aclanthology.org/2026.findings-acl.845/ |
| AG24 | **Ask Early, Ask Late, Ask Right: When Does Clarification Timing Matter for Long-Horizon Agents?** (2026 preprint) | FRONTIER / DIAGNOSTIC | Controlled timing intervention suggests clarification value depends on where the agent is in a trajectory; useful research-move example even if the exact claim remains preprint-level. | https://arxiv.org/abs/2605.07937 |
| AG25 | **When2Tool: Tool Necessity Is Linearly Decodable Before Generation** (2026) | FRONTIER / REPRESENTATION→ACTION | Shows that tool-need information can be strongly decodable before generation while natural action selection still fails to use it reliably; useful ownership boundary for generic “the model knows but does not act” stories. | https://arxiv.org/abs/2605.09252 |
| AG26 | **Done, But Not Sure: Disentangling World Completion from Self-Termination in Embodied Agents** (2026) | FRONTIER / CONTROL | Separates completing the external task from committing to termination; useful example of decomposing a single benchmark success into distinct control decisions. | https://arxiv.org/abs/2605.08747 |
| AG27 | **Calibration Is Not Control: Intervention Advantage for LLM-Agent Oversight** (2026) | FRONTIER / CONTROL OBJECT | Changed-object lesson: predicting failure risk is not the same as estimating whether an intervention improves the continuation. Useful beyond the specific oversight setting. | https://arxiv.org/abs/2606.21399 |
| AG28 | **AgentLens: Revealing the Lucky Pass Problem in SWE-Agent Evaluation** (2026) | FRONTIER / MEASUREMENT | Process-level audit showing that terminal success can hide poor recovery/verification trajectories; useful measurement warning for long-horizon agents. | https://arxiv.org/abs/2605.12925 |

## Second-pass additions from the same 2026-09-30 scan

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AG29 | **Beyond Single-shot Writing: Deep Research Agents are Unreliable at Multi-turn Report Revision** (ACL 2026) | PARENT / REVISION | User feedback is usually incorporated, yet 16–27% of previously covered content/citation quality regresses; strong evidence that revision locality/non-regression is distinct from “understands feedback”. | https://aclanthology.org/2026.acl-long.609/ |
| AG30 | **Action Boundary Blindness: When LLM Agents Cannot Tell Where One Action Ends and Another Begins** (ACL 2026) | PARENT / ACTION STRUCTURE | Natural cross-benchmark agent failure with an important diagnostic twist: explicit boundary cues recover part of the gap, suggesting elicitation rather than a simple capability absence. Excellent Sasano-style genealogy example; the exact object is already owned. | https://aclanthology.org/2026.acl-long.1711/ |
| AG31 | **Large Language Models Develop Belief State Geometry In-Context** (2026) | FRONTIER / MODEL SCIENCE | Controlled HMM setting shows linearly decodable and intervention-relevant posterior belief geometry in ordinary pretrained LLMs; a useful controlled parent for asking what “agent state” could mean mechanistically. | https://arxiv.org/abs/2609.17376 |
| AG32 | **AgentAbstain: Do LLM Agents Know When Not to Act?** (2026) | FRONTIER / ARTIFACT | Paired executable tasks separate task-solving from calibrated action commitment and expose post-hoc abstention after irreversible actions; important ownership boundary for generic “ask/stop/abstain” topics. | https://arxiv.org/abs/2607.10059 |

## Ownership-pressure additions — 2026-09-30 late scan

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AG33 | **When Users Change Their Minds: Measuring and Repairing Intent Drift in LLM Agents** (2026 preprint) | FRONTIER / OWNERSHIP | Released 2026-09-26. IntentFlux makes superseded/withdrawn intent executable and StateForge explicitly maintains active requirements; this sharply narrows any generic “evolving intent” novelty claim. | https://arxiv.org/abs/2609.32520 |
| AG34 | **From Memory to Belief: A Survey of State Maintenance and Belief Revision in LLM Decision Agents** (2026 survey/preprint) | SURVEY / FIELD MAP | Released 2026-09-23. Frames agent failures as state, transition, likelihood, revision, credit and belief-action consistency rather than generic memory; mandatory ownership map before entering this territory. | https://ssrn.com/abstract=7493158 |
