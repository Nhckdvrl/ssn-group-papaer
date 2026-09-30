# Key Papers — 推理与测试时计算（Reasoning / test-time compute）

从 `library/KEY_PAPERS.md` 按题材拆出（2026-09-30），ID 与内容保持不变。标签含义见 `../../KEY_PAPERS.md`。


## Reasoning / test-time compute

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| RS01 | **Self-Consistency Improves Chain of Thought Reasoning** (2022) | ANCHOR | Moves inference from one greedy reasoning path to marginalizing multiple paths. | https://arxiv.org/abs/2203.11171 |
| RS02 | **Tree of Thoughts** (2023) | ANCHOR | Makes explicit search state / branching part of inference rather than only sampling. | https://arxiv.org/abs/2305.10601 |
| RS03 | **Let's Verify Step by Step** (2023/ICLR 2024) | ANCHOR | Final-answer supervision can be too late; step-level supervision becomes the object. | https://arxiv.org/abs/2305.20050 |
| RS04 | **Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters** (2024) | BRIDGE | Key move from “more test-time compute” to **compute allocation conditioned on problem difficulty**. | https://arxiv.org/abs/2408.03314 |

## Reasoning / planning utilization

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| RS05 | **Extracting Search Trees from LLM Reasoning Traces Reveals Myopic Planning** (2026) | FRONTIER / DIAGNOSTIC | Reconstructs search structure from reasoning traces and asks whether deeper explored nodes actually control the final decision; useful pressure on “more visible reasoning = more used reasoning”. | https://arxiv.org/abs/2605.06840 |
| RS06 | **Reasoning Traces Shape Outputs but Models Won’t Say So** (ACL 2026) | PARENT / CAUSAL | Uses causal thought intervention to distinguish trace influence from models’ self-reports of that influence; important parent for reasoning-use/faithfulness claims. | https://aclanthology.org/2026.acl-long.1986/ |
| RS07 | **FaithCoT-Bench: Benchmarking Instance-Level Faithfulness of Chain-of-Thought Reasoning** (ICLR 2026) | PARENT / EVALUATION | Strong current faithfulness parent; prevents reframing generic CoT faithfulness as a new territory. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/6c7154e394e24c69409256ccf8bf0804-Abstract-Conference.html |
