# Key Papers — MoE 与路由（MoE / routing）

从 `library/KEY_PAPERS.md` 按题材拆出（2026-09-30），ID 与内容保持不变。标签含义见 `../../KEY_PAPERS.md`。


## MoE / routing

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| MOE01 | **Switch Transformers** (2021) | ANCHOR | Simplified top-1 sparse routing; canonical scale/training-stability baseline. | https://arxiv.org/abs/2101.03961 |
| MOE02 | **Mixture-of-Experts with Expert Choice Routing** (2022) | ANCHOR | Reverses token→expert allocation into expert→token selection; useful reminder that routing primitive itself is a design choice. | https://arxiv.org/abs/2202.09368 |
| MOE03 | **DeepSeekMoE: Towards Ultimate Expert Specialization** (ACL 2024) | ANCHOR | Shared vs routed experts and fine-grained expert segmentation; important specialization reference. | https://aclanthology.org/2024.acl-long.70/ |
