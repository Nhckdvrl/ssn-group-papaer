# 游戏 NPC 与社会智能体（Game NPCs / social agents）

**范围：** 游戏 NPC 与社会智能体：角色扮演、人格与行为、NPC 队友/对手、社会模拟、ToM 与社交推理游戏。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`\b(NPCs?|non[- ]player characters?|role[- ]?play\w*|social simulation|theory of mind)\b`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 11（28% / 基准 32%） | 7 | 14 | 15（24% / 基准 27%） | 16 | 21 | 13 | 24 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T13 — Game NPCs / interactive characters

**Why keep inhabiting it**

Foundation-model NPCs are not merely dialogue generators. In actual games they sit at the junction of **character identity, memory, shared world state, social reasoning, action/control, narrative authority, latency, and player experience**. Recent work increasingly shows that optimizing one of these in isolation can move another in the wrong direction.

**Recurring assumptions worth auditing**

- fluent / persona-consistent dialogue implies a good NPC;
- remembered text implies stable relationship or behavior;
- more open-ended interaction is monotonically better;
- the LLM should own world state, social state, planning, and low-level action;
- dialogue-only evaluation predicts co-play quality;
- LLM-as-judge roleplay scores are sufficient evidence;
- adding more context/memory is always helpful;
- a believable social simulation is behaviorally faithful;
- visual realism in a game world model implies state-aware NPC behavior.

**Natural observations**

- which component owns or validates each state transition;
- linguistic persona vs action/trajectory persona;
- verbal vs non-verbal social behavior;
- player/NPC shared-state disagreement;
- long-horizon commitment survival;
- role/task dependence of structure vs openness;
- deliberative vs reflexive control timescales;
- player outcome / cognitive-load changes that disagree with response-quality scores.

**Baseline / observation first**

Prefer public substrates where the NPC actually interacts with a game loop: CPDC, collaborative Minecraft NPCs, NCP-Bench, MineAmongUs/ARIA, ReactiveGWM, or other released environments. Start by reproducing the strongest baseline and mapping which state/action/evaluation dependency is load-bearing before inventing a memory module, planner, or personality method.

**High-risk failure modes**

- “NPC” becomes a cosmetic wrapper around an ordinary chatbot benchmark;
- simulator/game engineering dominates the science;
- another generic memory/RAG/persona method;
- player-study conclusions without a clear computational object;
- chasing proprietary production NPCs that cannot be reproduced.

**Deep map:** `GAME_NPC_LANDSCAPE.md`（本目录）.
**Anchors:** NPC01–NPC12, B19–B22.

## 3. 关键论文与本目录文件

- [`GAME_NPC_LANDSCAPE.md`](GAME_NPC_LANDSCAPE.md)
- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- （无）

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B19 — Ubisoft — NEO NPC
- B20 — Ubisoft — Teammates
- B21 — NVIDIA ACE — autonomous game characters
- B22 — NVIDIA / KRAFTON — How PUBG Ally was built

## 6. 最新 arXiv 入口

- [git-disl/awesome-LLM-game-agent-papers](https://github.com/git-disl/awesome-LLM-game-agent-papers)
- [JayCheng113/awesome-gameagent-papers](https://github.com/JayCheng113/awesome-gameagent-papers)
- [Eurekaleo/awesome-ai-for-games](https://github.com/Eurekaleo/awesome-ai-for-games)
- [BAAI-Agents/GPA-LM](https://github.com/BAAI-Agents/GPA-LM)
- [Neph0s/awesome-llm-role-playing-with-persona](https://github.com/Neph0s/awesome-llm-role-playing-with-persona)
- [nuochenpku/Awesome-Role-Play-Papers](https://github.com/nuochenpku/Awesome-Role-Play-Papers)
- [Persdre/awesome-llm-human-simulation](https://github.com/Persdre/awesome-llm-human-simulation)
- [Social-Atoms/awesome-social-sim](https://github.com/Social-Atoms/awesome-social-sim)
- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `workbench/npc-persona-behavior-grounding/`
- `workbench/npc-deception-investigability/`
