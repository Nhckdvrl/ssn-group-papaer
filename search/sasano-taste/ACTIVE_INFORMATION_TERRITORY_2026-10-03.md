# 主动探索与证据收集：baseline 本地可用性补查

核对日期：2026-10-03。仅查现有代码、接口与官方接收；未安装依赖、未下载权重、未运行实验、未开 workbench。

**结论：有具体可开始的现成入口，优先 EVOLvE / BanditBench；就绪程度是“源码与本地推理接口已核，运行未核”。不能说 LLF-Bench 已有开箱即用本地强 LLM baseline，也不能把 bandit 复现本身包装成新题。**

## 1. 找到的可执行基线：EVOLvE

- [ICML 2025 官方 PMLR](https://proceedings.mlr.press/v267/nie25b.html)核实主会接收。
- [作者仓库](https://github.com/allenanie/EVOLvE)，本次所查主分支 SHA `d9143f762e9724b857ae076d480acdb3067effff`。
- 不是只提供环境：已有 Bernoulli / Gaussian bandit、数值动作到自然语言动作的 wrapper、完整 rollout、轨迹存储；有 **UCB、Thompson sampling**，以及 LLM **原始历史 / 统计摘要 / 统计摘要 + UCB guide** 的现成实现。起步可用无外部数据的 Bernoulli，暂不依赖 MovieLens。
- 关键源码：[classics.py](https://github.com/allenanie/EVOLvE/blob/d9143f762e9724b857ae076d480acdb3067effff/banditbench/agents/classics.py)、[guides.py](https://github.com/allenanie/EVOLvE/blob/d9143f762e9724b857ae076d480acdb3067effff/banditbench/agents/guides.py)、[llm.py](https://github.com/allenanie/EVOLvE/blob/d9143f762e9724b857ae076d480acdb3067effff/banditbench/agents/llm.py)、[sampler.py](https://github.com/allenanie/EVOLvE/blob/d9143f762e9724b857ae076d480acdb3067effff/banditbench/sampling/sampler.py)。已读实际函数，非仅 README 承诺。
- 已有 `UCBAgent(core_bandit).in_context_learn(core_bandit, n_trajs=...)`；LLM 对应 `LLMAgent.build_with_env(verbal_bandit, summary=True, model=...)`，再 `in_context_learn(..., n_trajs=..., num_threads=...)`。`UCBGuide` 可接现成 UCB agent；无需先训练一个探索策略。
- reward 由环境概率模型生成；动作 parser + 数值收益评测，不需要 LLM judge。seed、episode 和模型可独立分发到单节点，弱 I/O 不构成主要结构性困难。

### 本地 LLM 接口核查结果

`LLM.generate()` 使用 `litellm.completion(model=self.model, messages=...)`。它不是 HF 模型内部直接加载，但可通过 LiteLLM 已有本地后端接入：官方 [Ollama 文档](https://docs.litellm.ai/docs/providers/ollama)给出 `model="ollama_chat/<本地模型名>"` 调本机服务的接口。这条路径无需外部付费 API。**这是源码调用链与官方后端文档共同支持的可接入判断，尚未实际端到端验证。**

两项不能省略的 caveat：

1. `LLM.__init__` 虽声明 `api_base`，实际未保存或传给 completion，子类 constructor 也不暴露它；不能照抄一个 `api_base=...` 参数就声称可接任意 vLLM。先走已有默认本地 Ollama provider，或者后续做显式、很小的 adapter，并登记其差异。
2. 原 repo `requirements.txt` 固定 TensorFlow 2.17 / ml-dtypes / TFDS，顶层导入整个 benchmark，故不能保证“只跑 Bernoulli 就自动绕过所有 TensorFlow 依赖”。作者 README 也明确记录 TFDS 问题。须实际 smoke test 后才能升为“已跑通”。

### 源码审阅发现的基线风险

`GreedyAgent` 继承 `UCBAgent`，只覆写与父类相同的 `calculate_exp_value`，未覆写 `calculate_arm_value` / 探索 bonus。按所查版本的继承链，它看起来仍会保留 UCB bonus，**不应直接把这个类当作正确 greedy 对照**。这不是实验发现，但足以要求复现前做代码审计；UCB 与 Thompson 的明确实现可先作为经典参照。不要为了“已有代码”而跳过这类检查。

## 2. LLF-Bench：环境可用，原 baseline 本地化不如上面直接

[微软仓库](https://github.com/microsoft/LLF-Bench)已在 2026-09-18 archived。查到的真实入口是 [tests/test_agents.py](https://github.com/microsoft/LLF-Bench/blob/main/tests/test_agents.py)，接 `BasicAIAgent` 和 `make_llm`；不是纸上复刻。

- bandit / gridworld 的语言反馈由模板与真值程序产生，`reset/step` 返回 instruction / observation / feedback 与 evaluator reward。环境侧不需要付费模型或 LLM judge。
- 但是 [agents/llm.py](https://github.com/microsoft/LLF-Bench/blob/main/llfbench/agents/llm.py)的 `make_llm` 只有旧 OpenAI / Azure / AutoGen 路径；未查到作者给出的本地 HF / vLLM 运行命令。`DEFAULT_LLM = make_llm(...)` 还在导入时初始化。旧版 `openai==0.28`、`pyautogen==0.1` 等意味着要先做依赖和接口适配。
- `--ignore_fp` 仍保留 reward 和 hindsight feedback，并不等于无提示纯探索；默认 all feedback 则有未来正反馈，可直告推荐行动。研究信息获取时须核清 agent 实际获得多少 oracle 信息。

因此 LLF 可当第二环境候选，**不能现阶段承诺“原 baseline 本地直接跑”**。

## 3. 与现有探索研究的距离

| 工作 | 已有 claim / 资产 | 本次核查边界 |
|---|---|---|
| [Can LLMs Explore In-Context?，NeurIPS 2024](https://papers.neurips.cc/paper_files/paper/2024/file/d951f73c521d069fefbb73396df01424-Paper-Conference.pdf) | 原始历史与外部充分统计摘要的差异已经是核心结论 | 本轮没找到可核作者代码；不能写“没有开源”，也不能把环境容易实现当复现已具备 |
| [EVOLvE，ICML 2025](https://proceedings.mlr.press/v267/nie25b.html) | 系统覆盖 bandit、algorithm guide、示范/蒸馏；已有强经典参照 | 可用作驻留起点；“给摘要/给 UCB 提示更会探索”已有人主张 |
| [Reasoning aligns language models to human cognition / 新目录 Active Probabilistic Reasoning，2026](https://arxiv.org/abs/2602.08693) | 主动证据获取、人类比较与概率推理，应在新题定位中检查 | root 已全文读；本次未核其 Drive 内容及可复现性，不能当现成首个 baseline |

## 4. 对 territory 推荐的影响

可以保留“**不知道答案时，Agent 会不会采取能使自己知道的行动**”作为宽领域，包含探索、证据选择、反馈理解、停止决策；资源适配有了具体代码支撑。最便宜的驻留起点是复现 EVOLvE 的强参照与提示层，观察现代本地模型在完整轨迹中真实出现的问题，再决定有没有跨场景的问题值得深入。

但这仍不等于主会题目 ready。还需要自然任务动机、从 bandit 向一个有实际意义的交互任务的迁移，以及把知识不足、算术/记忆不足、动作解析、信息获取策略分开的证据；不能只把旧模型换成新模型画 regret 排名。若最终只发现现有摘要/算法提示就能解释的提升，应该报告定位重合并继续驻留，不预判 territory 死亡。

检索和源码暂存 `/tmp/active_info_check_20261003/`，未纳入 git。

## 5. 收尾补查：更自然的交互入口与2026谱系

主agent按用户要求停止子agent后，独立复核了以下入口及已有源码缓存：

- **AR-Bench**：[ICML2025正式页](https://proceedings.mlr.press/v267/zhou25e.html)、[代码](https://github.com/tmlr-group/AR-Bench)。现有[猜数evaluator](https://github.com/tmlr-group/AR-Bench/blob/main/arbench/reasoner/gn/gn_evaluator.py)用程序`compare_guess`反馈，`POLICY_BASE_URL`实际传入推理函数，可接本地vLLM。这个子任务无需另一个付费judge；侦探与海龟汤分支有额外response模型，不能把全benchmark概括成零judge。
- **HELiX**：[ICML2026正式页](https://proceedings.mlr.press/v306/xu26ao.html)。从语言反馈的可辨识信息出发提出假设消除和探索理论；一般LLF已经不只是经验prompt技巧。正式PDF与摘要已核，不能把其理论保证外推到任意会撒谎或歧义不受控的语言反馈。
- **Active Probabilistic Reasoning / Reasoning aligns…**：[2026全文](https://arxiv.org/html/2602.08693v1)已把采样与推断分开，并拟合人机策略；“会答题但不会找证据”已有owner，不能拿来当我们的新结论。
- 最新目录的 *Learning from Language Feedback via Variational Policy Distillation* 等显示该邻域也在发展训练方法；仅目录级，不当成熟冻结baseline。用户要求本轮快探索，因此优先AR-Bench猜数与BanditBench现成策略层，而非复制训练闭环。

三条谱系：bandit/充分统计→EVOLvE策略引导；被动问答→AR-Bench主动询问→人机采样/推断分解；LLF-Bench多反馈→HELiX反馈信息与假设消除。共同研究对象是**交互中怎样获取信息、利用反馈并调整判断**，不是一般Agentic RL排行榜。

## 6. 压力、形态与热度

| 压力 | 已核来源 | 可以做的研究动作 |
|---|---|---|
| 记忆/算术失败混入探索策略失败 | NeurIPS2024 explore、EVOLvE | 原始history与充分统计、经典策略的公平对照 |
| 能利用给定证据不代表能自行选到它 | AR-Bench、Active Probabilistic Reasoning | 按同等信息预算分解测量；宽结论已占 |
| 语言反馈可能泄露答案或未来最优动作 | LLF-Bench模板与ignore_fp源码 | 明确信息协议，不拿oracle收益说模型更会学习 |
| 反馈的信息量与措辞长度不同 | HELiX理论与实验 | 固定可排除假设集合/任务真值，再看模型实际更新 |
| API/本地接口与经典baseline实现会改变对照 | EVOLvE源码 | 先审计和复现，不把接口故障写成认知失败 |
| 受控任务的策略能否迁移到自然活动 | AR-Bench三类任务；人机概率任务 | 一类程序反馈窗口加一个有实际解释意义的任务，不强做新大benchmark |

形态可为：自然交互失败的机制与修复、反馈可用性测量、具有可验证预测的认知策略模型。应有客观任务结果，排除一句提示即可恢复、解析器故障及不公平token预算；仅降低regret/提高猜数分数不足以保证主会资质。

`density 'in.context.*explor|explor.*in.context|language feedback|active probabilistic|active evidence'`：ICLR2026接收31/99（31%，全会27%）、ICML2026为26、NeurIPS2025为16。宽式大量误命中普通ICL，**不能作为低热度证明**。`shapes`有分数accepted55、method67%/finding44%/theory22%，仅邻域参考。EVOLvE历史ICLR2025拒稿6.50，后ICML2025接收；不将前次拒稿当领域天花板。尚未齐备同切片10接收+5拒稿全文评审，不硬凑。

驻留顺序：固定一个官方任务/本地接口 → 经典策略与LM baseline原配置复现 → 记录完整交互/耗时 → 信息量与提示/记忆对照 → 更新近邻 → 按真实问题提研究动作。与`latent-world-model-planning`的主动观测分支有交集，正式归属由人决定。
