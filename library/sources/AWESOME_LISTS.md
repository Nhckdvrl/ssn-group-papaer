# 来源入口：awesome 列表、daily-arXiv 镜像、顶会名单

**用途：** 环视一个领域时的第一批入口。顶会名单回答“收了什么”，arXiv 入口回答“最新在做什么”。两者都要看。
**核查日期：** 2026-09-30。“2026 条目”= README 中链接到 2026 年 arXiv 编号的条目数，用来判断列表是否还在更新（0 表示已过时，只能用作历史谱系）。
**网络说明：** 在本仓库的云端会话中 arXiv / OpenReview / PaperNotes 网页不可直接抓取，但 `raw.githubusercontent.com` 可以用 `curl` 下载（`tools/venue_corpus/fetch.sh` 就是这样取数据的）；网页检索仍可检索到 PaperNotes 的笔记摘要。

## 1. 顶会名单与统计（优先）
| 来源 | 内容 | 用法 |
|---|---|---|
| `tools/venue_corpus/`（本仓库） | ICLR 2025/2026（含拒稿与审稿均分）、ICML 2025/2026、NeurIPS 2024/2025、ACL/EMNLP/NAACL main、CVPR/ICCV 2025 | 热度、切片接收率、论文形态、近邻定位 |
| [papercopilot/paperlists](https://github.com/papercopilot/paperlists) | OpenReview 派生的逐篇 JSON（标题、摘要、状态、分数） | `fetch.sh` 的数据源；NeurIPS 2026 名单公开后会出现 |
| [acl-org/acl-anthology](https://github.com/acl-org/acl-anthology) | *CL 会议 XML（标题、摘要） | `fetch.sh` 的数据源 |
| [dion-jy/spotlight-todai](https://github.com/dion-jy/spotlight-todai) | NeurIPS 2025 / ICLR 2026 / ICML 2026 的 oral 与 spotlight | 高信号子集 |
| [jiaxianyan/icml-2026-agent-papers](https://github.com/jiaxianyan/icml-2026-agent-papers) | ICML 2026（632）与 ICLR 2026（457）智能体论文按主题分类 | 智能体方向的密度与近邻 |
| [PaperNotes](https://papernotes.org/) | 按会议 × 题材的论文笔记（如 ICLR2026 multi-agent 47 篇、ICML2026 24 篇、ACL2026 40 篇） | 仅作发现与分类；进入定位表前必须回原文 |
| GitHub topic [`neurips-2026`](https://github.com/topics/neurips-2026) 与 README/PR 中的 “Accepted to NeurIPS 2026” | 作者自报的 NeurIPS 2026 接收（2026-09-24 出结果，完整名单未公开） | 补充最新接收 |

## 2. 最新 arXiv 的日常入口
| 来源 | 说明 |
|---|---|
| [zachysun/DailyArXiv](https://github.com/zachysun/DailyArXiv) | LLM / Multimodal / AI Agent / LLM Inference / LLM Memory，每类保留最近 100 篇，含摘要与 comment（常写有接收会议） |
| [zezhishao/DailyArXiv](https://github.com/zezhishao/DailyArXiv)、[somewordstoolate/DailyArXiv](https://github.com/somewordstoolate/DailyArXiv)、[ZCjenny549/DailyArXiv](https://github.com/ZCjenny549/DailyArXiv) | 其他关键词组合的同类镜像 |
| [luohongk/Embodied-AI-Daily](https://github.com/luohongk/Embodied-AI-Daily) | 具身 / VLA |

## 3. 按题材的 awesome 列表

| 题材 | 列表 | 2026 条目 | 备注 |
|---|---|---:|---|
| 多智能体协作 | [xxzcc/awesome-llm-mas-rl](https://github.com/xxzcc/awesome-llm-mas-rl) | 在更新 | LLM 多智能体 RL（84 条，含 reward/credit/编排分类与 benchmark gap） |
| 多智能体协作 | [edzq/LatentAgentComm](https://github.com/edzq/LatentAgentComm) | 28 | 隐空间通信的活综述，含开放问题 |
| 多智能体协作 | [junchenzhi/Awesome-LLM-Ensemble](https://github.com/junchenzhi/Awesome-LLM-Ensemble) | 27 | LLM 集成 / 合作 / 路由 |
| 多智能体协作 | [MilkThink-Lab/Awesome-Routing-LLMs](https://github.com/MilkThink-Lab/Awesome-Routing-LLMs) | 60 | 路由（含 token 级协作） |
| 多智能体协作 | [dstripelis/Awesome-LLM-Routing](https://github.com/dstripelis/Awesome-LLM-Routing) | 少 | 路由 |
| 多智能体协作 | [kyegomez/awesome-multi-agent-papers](https://github.com/kyegomez/awesome-multi-agent-papers) | 11 | |
| 多智能体协作 | [taichengguo/LLM_MultiAgents_Survey_Papers](https://github.com/taichengguo/LLM_MultiAgents_Survey_Papers) | 0 | 过时，谱系用 |
| 大小模型 | [tigerchen52/awesome_role_of_small_models](https://github.com/tigerchen52/awesome_role_of_small_models)、[FairyFali/SLMs-Survey](https://github.com/FairyFali/SLMs-Survey) | 0 | 过时，谱系用 |
| 智能体 | [VoltAgent/awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers) | 370 | 2026 年智能体论文（最新） |
| 智能体 | [js-lee-AI/awesome-llm-agent-papers](https://github.com/js-lee-AI/awesome-llm-agent-papers) | 274 | 规划 / 记忆 / 工具 / 多智能体 / 评测 / 安全 |
| 智能体 | [yxf203/Awesome-Efficient-Agents](https://github.com/yxf203/Awesome-Efficient-Agents) | 56 | 高效智能体 |
| 智能体 | [zjunlp/LLMAgentPapers](https://github.com/zjunlp/LLMAgentPapers) | 10 | |
| 智能体 | [WooooDyy/LLM-Agent-Paper-List](https://github.com/WooooDyy/LLM-Agent-Paper-List)、[AGI-Edgerunners/LLM-Agents-Papers](https://github.com/AGI-Edgerunners/LLM-Agents-Papers)、[Paitesanshi/LLM-Agent-Survey](https://github.com/Paitesanshi/LLM-Agent-Survey) | 0 | 过时，谱系用 |
| 推理 | [EIT-NLP/Awesome-Latent-CoT](https://github.com/EIT-NLP/Awesome-Latent-CoT) | 104 | 隐式推理 |
| 推理 | [YU-deep/Awesome-Latent-Space](https://github.com/YU-deep/Awesome-Latent-Space) | 106 | 隐空间（推理、动作、记忆） |
| 推理 | [multimodal-art-projection/LatentCoT-Horizon](https://github.com/multimodal-art-projection/LatentCoT-Horizon) | 0 | 综述配套，谱系用 |
| 可解释性 | [cooperleong00/Awesome-LLM-Interpretability](https://github.com/cooperleong00/Awesome-LLM-Interpretability) | 1 | 工具/教程/论文 |
| 可解释性 | [ruizheliUOA/Awesome-Interpretability-in-Large-Language-Models](https://github.com/ruizheliUOA/Awesome-Interpretability-in-Large-Language-Models)、[zepingyu0512/awesome-SAE](https://github.com/zepingyu0512/awesome-SAE)、[itsqyh/Awesome-LMMs-Mechanistic-Interpretability](https://github.com/itsqyh/Awesome-LMMs-Mechanistic-Interpretability) | 0 | 过时，谱系用；可解释性的最新进展以顶会名单与 `themes/interpretability-representation/` 为准 |
| 理解与生成 | [OpenEnvision/Awesome-Multimodal-Modeling](https://github.com/OpenEnvision/Awesome-Multimodal-Modeling) | 42 | MLLM / 统一多模态 / 原生多模态，含 UMM Zoo |
| 理解与生成 | [Purshow/Awesome-Unified-Multimodal](https://github.com/Purshow/Awesome-Unified-Multimodal)、[friedrichor/Awesome-Multimodal-Papers](https://github.com/friedrichor/Awesome-Multimodal-Papers) | 1 / 6 | |
| 游戏 / NPC | [git-disl/awesome-LLM-game-agent-papers](https://github.com/git-disl/awesome-LLM-game-agent-papers) | 127 | ACM CSUR 综述配套，持续更新 |
| 游戏 / NPC | [Eurekaleo/awesome-ai-for-games](https://github.com/Eurekaleo/awesome-ai-for-games) | 90 | *AI for Games in the Foundation Model Era* 配套 |
| 游戏 / NPC | [JayCheng113/awesome-gameagent-papers](https://github.com/JayCheng113/awesome-gameagent-papers) | 25 | 243 篇，标注方法范式与会议 |
| 游戏 / NPC | [Persdre/awesome-llm-human-simulation](https://github.com/Persdre/awesome-llm-human-simulation) | 16 | 人类/社会模拟 |
| 游戏 / NPC | [Neph0s/awesome-llm-role-playing-with-persona](https://github.com/Neph0s/awesome-llm-role-playing-with-persona) | 3 | 角色扮演 |
| 游戏 / NPC | [nuochenpku/Awesome-Role-Play-Papers](https://github.com/nuochenpku/Awesome-Role-Play-Papers)、[BAAI-Agents/GPA-LM](https://github.com/BAAI-Agents/GPA-LM)、[Social-Atoms/awesome-social-sim](https://github.com/Social-Atoms/awesome-social-sim) | 0 | 过时，谱系用 |

批量下载（在任意机器上）：
```bash
curl -sSL https://raw.githubusercontent.com/<owner>/<repo>/main/README.md -o <owner>__<repo>.md   # 分支名可能是 master
```

## 4. 博客与报告
见 [`BLOGS_REPORTS.md`](BLOGS_REPORTS.md)（B01–B23；已在各题材页按主题引用）。
