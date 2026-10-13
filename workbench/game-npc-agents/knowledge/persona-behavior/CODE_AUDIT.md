# 矿区 A · 第一轮作者源码定点审计（2026-10-14）

本页的事实来自实际 GitHub 源码文件阅读，**未 clone/安装/运行、没有本机 GPU 复算或新行为结果**。Blob SHA 只是文件快照，**正式运行必须 pin 下面 repo commit/依赖与数据完整 SHA**。审计不把代码的设计权衡自动当论文错误。

## 1. PCSP — 真实 NPC 策略训练，但 style 有环境奖励定义
仓库 `yoosunghong/pcsp` 当前 main commit `5420f7b4fa0fdb6110e131402af9f5386ce2d0cf`（核于2026-10-14）。
- [research/src/env/mini_inzoi_v3.py](https://github.com/yoosunghong/pcsp/blob/main/research/src/env/mini_inzoi_v3.py) blob `20b505d4a8195e437ad15e098362355a82097247`：`_style_reward` = `0.3 * cosine(_bf_vecs, ACTION_STYLE_PROFILE[action])`; `_apply_action` 若 action 在 persona.preferred_actions 则再加 `0.5`；社交行动额外 `_social_bonus`。这意味着风格与行动关系**部分由环境目标函数直接定义**，跨自然游戏的解释须警惕循环指标。
- [research/scripts/run_pcsp_v3.py](https://github.com/yoosunghong/pcsp/blob/main/research/scripts/run_pcsp_v3.py) blob `a225f25a289d1aefe3bf35524ac46842d742ace6`：设置 4 agents、20 actions、33-d base observation、200-step episode；官方提供 `--smoke` 和 full/no_consist/no_diverse/concat/frozen_proj 配置。Smoke 是执行检查，非论文复现。
- [research/src/training/pcsp_trainer.py](https://github.com/yoosunghong/pcsp/blob/main/research/src/training/pcsp_trainer.py)：实际有 `PCSPConfig` 的 `lambda_consistency`、`lambda_diversity`、`_consistency_loss` 的 in-batch InfoNCE 和 `_diversity_loss`。尚未通读完整梯度路径/数值稳定性。
- [作者独立评估](https://github.com/yoosunghong/pcsp/blob/main/research/docs/evaluations/independent-behavior.md) blob `d472e016b2c973bf3d77b2497013df55ed589e49`：作者已做 3个政策 seed×100 held-out personas 等独立行为分析。不得再自称“首次发现训练指标不等于行为”。

**后续源码审计任务：** 查奖励项对状态/行动选择是否产生机械诱导，训练模型实际接收 persona conditioning 的位置、probe 的训练/校准分离、评估是否把同一内部分数计成真值；复现作者完整 baseline 时不可悄悄改变 reward 或 evaluator。

## 2. agent-sandbox — RPG 非玩家角色有执行动作，但存在脚手架行为
仓库 `ccb/agent-sandbox` 当前 main commit `d7b872e396df2ef05ff8391de53e0563ca698cf3`。
- [text_adventure_games/npc.py](https://github.com/ccb/agent-sandbox/blob/main/text_adventure_games/npc.py) blob `43197a95f2c2e287a4e3f08d7a696cdfc6ad77c4`：`LLMAgent.decide(observation) -> command`，`react_behavior` 负责合法行动路由、失败反思/重试；`make_hybrid_behavior` 允许在 LLM 失败时调用 `scripted_behavior`。要分清 NPC 的**原始首选行动、重试后行动、脚本 fallback 和世界真终态**。
- [text_adventure_games/llm_client.py](https://github.com/ccb/agent-sandbox/blob/main/text_adventure_games/llm_client.py)：`LLM_PROVIDER=mock` 可做零API集成 smoke；`LLM_BASE_URL` 可以连接本地兼容服务，但`mock` 不代表 LLM 基线。文档中旧“npc skeleton”与新实码存在版本不同步，**按指定 commit 源码判断**。
- 该平台可以观察对话/利益选择是否真正调用合法动作，**但不是官方公认的 persona/利益 benchmark**。缺少作者明确动机/交易/关系任务时，不因易跑就发明五种“好坏人格”合成任务。

## 3. ICML2026 The Personality Illusion — 不是 RPG，但基准已占自述/行为假说
`psychology-of-AI/Personality-Illusion@a934083dcccd4428396497020578e89ffc9c51f8`；
[behavioral_tasks/README.md](https://github.com/psychology-of-AI/Personality-Illusion/blob/main/behavioral_tasks/README.md) blob `db5fae0efe32bd57cd263b4a04ce97f591401e28`：risk-taking 数据 notebook生成，honesty/IAT/sycophancy 有 datasets，作者 `data/` 提供原报告/注入结果。**不等于能在游戏NPC里原样使用其心理测量。**

## 4. Rethinking Psychometric Evaluation — 精细测量自身也有脚手架
`psychology-of-AI/Rethinking-Pyschometric-Eval-LLMs@4617b3c014d9f16ea81bdbe69188f13b49664b04`。
- [src/llms/openai_compat.py](https://github.com/psychology-of-AI/Rethinking-Pyschometric-Eval-LLMs/blob/main/src/llms/openai_compat.py) blob `1c85074953a42c230ee652042031c749df180dc5`：OpenAI兼容 chat 接口，有 seed 不兼容时重试不带 seed 分支；作者默认 OpenRouter API，不能说原表纯本地复现。
- [src/runner/tpb_likert_runner.py](https://github.com/psychology-of-AI/Rethinking-Pyschometric-Eval-LLMs/blob/main/src/runner/tpb_likert_runner.py) blob `d95e285e3f72b83f35b1d1984f3edae8045cef19`：若全部量表维度评分相同，追加 `_ANTI_COLLAPSE_NUDGE` 重采样；是实际代码中的回复质量稳定处理，须在指标重复时记录有效调用/选样规则。**不因存在回复重试就认定论文不可信**。
- [src/runner/sycophancy_runner.py](https://github.com/psychology-of-AI/Rethinking-Pyschometric-Eval-LLMs/blob/main/src/runner/sycophancy_runner.py)：每个episode两步回答，`base_system_prompt` 和 `task_context` 可以独立加入；用于审计同/跨会话实验与 framing，而非偷加信息后宣称因果。
- 重点不是挖一个原实现“bug”，而是**弄清作者做了哪些公平控制、哪些未覆盖真实游戏行为**，随后再决定 RPG 迁移实验。

## 5. 原版 Generative Agents — 不适合不改造就作为零 API 主基线
`joonspk-research/generative_agents@fe05a71d3e4ed7d10bf68aa4eda6dd995ec070f4`，README 仍要求 `openai_api_key` 与 Django+模拟服务，若复现需明确本地替代/环境数据许可。它是社会模拟重要源头但**不是本矿区强 NPC 游戏动作/利益选择的低成本直接baseline**。

## 结论与阅读债
源码审计已显示：①行为“风格”可能在奖励层被显式定义；②执行动作可能部分归功于 ReAct 重试/脚本；③人格量表“行为预测”强烈依赖测量粒度、API/采样规则。这些是已有实现事实，不是我们发现 NPC 的机制。后续 local agent 先恢复原生强基线与校准实例，再选**最少**具有独立意义的测量；不要用当前笔记代替完整论文和作者附录。
