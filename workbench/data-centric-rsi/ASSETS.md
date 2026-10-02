# 资产核验与资源契约

更新：2026-10-02。远程资产审计之后已建立 E00 的本地单卡闭环；本地训练/评测是 **modified reproduction**，不可冒充论文原版数值。通用边界继承 [RESOURCES.md](../../RESOURCES.md)。

## 1. 资产分层

| 资产 | 远程确认的内容 | 未确认/不提供的内容 | 我们的用途 |
|---|---|---|---|
| [DataEnvGym](https://github.com/codezakh/dataenvgym) | math/code/VQA baseline；vLLM/Ray 推理、本地 LLaMA-Factory 训练；Gemma2-2B 的 math example | 当前依赖在本地 Blackwell/A100 是否兼容；旧 MATH 源已失效；不能假定安装即成功 | 默认 E00 主入口，先一个自然任务的完整数据→训练→评估环路 |
| [Self-Play Pretraining 代码](https://github.com/nourya-aliz/self_play_pretraining) | figures、scoring、REPRODUCING；原 acowsik 路径重定向到当前作者路径 | 不是完整训练代码发布 | 用原 scorer 建测量资产，不先从零重写 self-play |
| [P01 模型](https://huggingface.co/nourya-cohen/solomonoff-paper) | 100k–24.4M learner、多个阶段、固定先验与 reward ablation、curriculum learners | 模型卡明确没有 generator、optimizer、training code；不能视为可无缝续训的完整状态；只含完成主预算的 ladder seeds | 低耦合跨阶段评估、受控重新适配；明确 reset optimizer 的新实验身份 |
| [RSIBench-Data](https://github.com/evolvent-ai/RSIBench-Data) | 数据策略、训练/评估服务契约，Tinker 与 Harbor/E2B 路径 | 不是现成本地 GPU 后端；API 和环境有额外费用/授权 | 借鉴隔离、预算和证据接口；本地替换须标 modified/local protocol |
| [Curation-Bench](https://github.com/feiyang-k/curation-bench) | curation benchmark、策略与训练流程入口 | 大数据/I/O、当前配置在本地能否跑；未安装 | I02 强近邻及后续跨模态验证，不作为首个全量下载 |
| [SEAL](https://github.com/Continual-Intelligence/SEAL) | 官方实现入口，与 self-edit/适配论文关联 | 本轮未深入审计训练路径/本地兼容 | 备选小规模真实训练反馈 substrate |
| [SQLM](https://self-questioning.github.io/) | 官方项目与论文，简洁 3B self-play 设定 | 未完成代码逐文件/本地复现审计 | 第二候选闭环，先補方法实现和测试选择口径 |
| [SGS](https://github.com/LukeBailey181/sgs) | 官方代码入口 | Lean 环境、全部训练成本和复现步骤未审计 | 重资产近邻，非默认首跑 |
| [Group-MATES](https://github.com/facebookresearch/Group-MATES) | NeurIPS 2025 主会官方关系影响选样代码与 DCLM 配方入口 | 当前只核对论文、README 入口；内部运行路径和本地迁移未审计 | 若选定固定池组级作用为问题，它是必须对齐的强 baseline；原始 8 卡预训练不是 E00 的轻量替换 |
| [BLISS](https://github.com/MingruiLiu-ML-Lab/BLISS-Bilevel-Data-Selection) | ICML 2026 主会官方多步 bilevel 动态选样代码入口 | 8×A6000 DDP/通信及本地执行未核实，不能称已复现 | 约束“动态多步 proxy”增量；若动作空间切到预训练固定池，再审正式实现 |

上游入口可能更新；执行时先记录 commit/revision，而不是把本文日期当版本锁。

## 2. 原论文成本与本地可行性不是一回事

- **SOAR**：论文 v3 App B.9 为 32×H100/H200、48–60h/run；不是“3B 因而单卡随便跑”。其完整嵌套训练不适合作为默认探索起点。
- **ASP**：论文训练配置为约 8×H100、48h，另有程序执行/验证负担；单节点不代表廉价。
- **P01**：小模型、长 token budget、多个 reward arm 与 seed/超参搜索。已发布结果可低成本复核；完全重做训练 grid 的成本仍需另算。
- **RSIBench-Data**：名义预算为 run 16h/$500 Tinker；这既不是纯 GPU 小时，也不是我们的本地费用预测。
- **DataEnvGym**：论文显示 2B 级学生可进行较短迭代；它的历史时长不作为当前机器承诺，实际完整闭环的耗时由 E00 测量。
- **Group-MATES / BLISS**：前者论文 Table 3 的 412M/1.4B/2.8B 目标预训练分别约 104/240/740 H100 小时；后者 1B 数据选择阶段报告 11.82 小时、74.51GB 峰值显存及 8×A6000 DDP。它们是必须理解的强近邻，不宜为 E00 一轮 120 条 MATH SFT 盲目重造整套预训练系统。

论文来源：[SOAR](https://arxiv.org/html/2601.18778v3)、[ASP](https://arxiv.org/html/2607.03523v1)、[P01](https://arxiv.org/html/2609.30063v1)、[RSIBench](https://arxiv.org/html/2607.25886v1)、[DataEnvGym](https://arxiv.org/html/2410.06215v3)、[Group-MATES](https://arxiv.org/html/2502.14709)、[BLISS](https://arxiv.org/html/2510.06048)。不做 H100→A100/PRO/H20 的未经测量换算。

## 3. 硬件组织

用户提供：实验室十几张 A100、8 张 PRO 6000；实习处 16 张 H20。不同地点默认不共享数据、权限或实时训练状态；不假定同时空闲、显存/拓扑一致。

每个训练环路只占一个可用单卡/单节点槽位；跨节点并行用于 seed、学生状态、数据动作等独立分支，不跨弱网络做梯度同步。一个节点内都先测试，不能假定 PCIe 多卡一定加速。

优先文本、离线缓存和小量动作样本。基础 checkpoint、分词/byte 处理、数据分片一次准备后节点内复用；避免共享盘随机读取大量小文件。对于 code executor，必须 CPU/内存/时间限额及隔离，合成程序默认无网络、无凭证访问；错误和超时也进入成本账。

## 4. 四本成本账

`C_total = C_generation + C_execution/verification + C_student + C_improver + C_evaluation/selection`。

- 训练预算：实际训练 token、更新步、GPU-time、峰值显存与 optimizer state。
- 经验预算：teacher 调用/生成 token、无效数据、程序执行时间与验证成本。
- 搜索预算：所有候选、超参、被放弃或失败的 run、选择用反馈次数。
- 复用预算：一次构建的策略/语料资产服务多个学生时，同时报告单次成本与随学生数量变化的摊销曲线；不得预设复用一定回本。

GPU 小时、CPU 小时、API 费用和 wall-clock 分开保存。吞吐更高与统计样本更多是两种收益，不混为训练方法加速。

## 5. 执行前必须留下的 manifest

代码 SHA、模型 revision/文件 hash、数据源/许可证/去污染规则、train/dev/private split hash、训练/生成/评估 seeds、父 checkpoint hash、optimizer reset 或继承、precision/LoRA 设置、实际 token、全部失败、硬件与版本、外部反馈调用数。

P01 的发布权重不是完整训练状态：若做后续训练，明确是新 optimizer 的受控适配，不能写“复现原第 t 轮继续训练”。从发布包观察到的稳定性也不能估算所有原始 seeds 的崩溃概率。

## 2026-10-02 E00 本地资产（执行中）

- 源码：`/home/xiang/.cache/research/data-centric-rsi/DataEnvGym`，SHA `f698f39c7d77fc655942099535d06a4d11b32e3b`，可用 `git clone https://github.com/codezakh/DataEnvGym.git` 后 checkout 该 SHA 重建。大源码不进本仓库。
- 学生：`google/gemma-2-2b-it@299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8`，Hugging Face 缓存。MATH 替代数据：`EleutherAI/hendrycks_math@21a5633873b6a120296cce3e2df9d5550074f4a3`，不能声称与旧 `lighteval/MATH` 逐例一致。
- 环境：基于既有 `verl-clean` conda 的 `--system-site-packages` venv `/home/xiang/.venvs/data-centric-rsi`；额外装 `python-ulid==4.0.1`、`antlr4-python3-runtime==4.11.1`、`sh==2.4.0`、`loguru==0.7.3`。运行入口见 [`scripts/env.sh`](scripts/env.sh)、[`scripts/e00_prepare.py`](scripts/e00_prepare.py)、[`scripts/e00_student.py`](scripts/e00_student.py)。学生训练用现有 Transformers/PEFT 与官方 recipe 的关键超参；不是官方旧 LLaMA-Factory/vLLM 栈的无修改复现。
- 大型 JSONL、模型和运行日志在 `/home/xiang/.cache/research/data-centric-rsi/`；小型 split/hash 清单在 [`results/E00_manifest.json`](results/E00_manifest.json)。本地共享目录及缓存不保证跨机器自动可用，重建按脚本及上面的 revision。

## 6. E00 对原论文/源码的协议差异账（2026-10-02 全文与关键源码复核）

| 项目 | 论文 / 固定源码 | 本地 E00–E05 |
|---|---|---|
| 目标 | 论文 Table 2 为 10 轮反馈式 data generation，按 validation 选最佳学生；论文 teacher 是 GPT-4o。固定 `examples/math/open_ended.py` 则实例化 GPT-4o-mini。 | 一轮 120 条真实 MATH train 标注的静态/检索/匹配 SFT；没有 GPT teacher、生成数据、10 轮状态反馈、最佳轮选择。只能作为闭环 substrate/静态动作基线。 |
| 数据源/切分 | 论文 App B.7 称 MATH validation 从 test 抽；固定源码 `MATHTask(val_balanced_subset_50)` 从 train 抽，原 `lighteval/MATH` 已失效。 | 改用固定 revision 的 `EleutherAI/hendrycks_math`；dev 从 train 每格前 50，120 条训练题对 dev/test 题面 hash 皆零重合，test 不用于选配方。不能和论文 15.78/23.44 直接比较。 |
| 训练 | 论文 App B.1.2：LoRA r16/alpha32/dropout0.05、batch16、3 epoch、FP16、cutoff1024。固定源码示例所用 LLaMA-Factory YAML 未覆写 LoRA 参数，其 vendor 默认 r8/alpha16/dropout0；YAML 另有 `val_size=0.1`。 | 新版 Transformers/PEFT Trainer，采用**论文**所写 r16/alpha32/dropout0.05、全部 120 条、optimizer reset、24 更新步；不是源码 LLaMA-Factory 的精确执行。 |
| 评估提示 | 固定 math 示例对 base 用 `prepare_few_shot_prompt`，加载 LoRA 后因未设 `prompt_formatter` 改为仅题面；两者均应用 chat template，`apply_chat_template(..., tokenize=False)` 未加 generation prefix，temperature0/max350。 | 首轮对所有模型统一 few-shot、加 generation prefix，并在校准后统一加一行答案格式指令。这是可比的数据动作评测，**不是官方提示协议**。POST-HOC 审计补测统一 zero-shot＋格式，以及接近源码的提示口径；后者训练前后提示不同，不能估计训练因果收益。 |
| 反馈 prompt | 固定 Open-Ended 模板尝试混合 3 训练题 + 3 错题，但 `CompletedMathTaskInstance` 的题面须经 `.task_instance.instruction` 访问；模板直接读 `.instruction`，本地 sentinel 渲染为空。 | 未使用该 teacher；若后续运行官方反馈分支，必须先修并分别保存修前/修后 prompt，不从源码 bug 推断论文结果。 |

以上区别按 [DataEnvGym 论文](https://arxiv.org/html/2410.06215v3) 和固定 [官方代码](https://github.com/codezakh/dataenvgym/tree/f698f39c7d77fc655942099535d06a4d11b32e3b) 核对。每次解释结果先明确属于“论文口径”“固定源码口径”还是“本地同提示数据动作口径”。

## 7. E06–E08 新增边界与评测成本

- 原论文 MATH Open-Ended 的最佳学生来自 **10 轮、累计约 752 条**生成题；论文 B.2 的 GPT-4o teacher 为 temperature 0。E06/E07 使用本地 `Qwen2.5-32B-Instruct@5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd`、temperature 0.7、每请求一条、仅 40/arm 与 20/arm 的质量 gate；这不是原论文的生成基线。当前 shell 无 `OPENAI_API_KEY`，所以未调用原 GPT-4o teacher；E07 的答案错误只属于本地替代。原论文这些配置见[全文 §B.2/B.3](https://arxiv.org/html/2410.06215v3)。
- E00/E04/E05 均为**一轮 120 条真实标注题**、3 epoch、24 optimizer step；E08 只复用这些 checkpoint 比动作。不能从 E08 的相近收益推断 DataEnvGym 原方法在 10 轮/752 条下无效。输出文件在外部缓存 `runs/e00/e04/e05/e06/e07/e08/`，小清单在本 workbench `results/`。
- 固定 vLLM 0.11.0 的默认 V1 离线推理对同一 dev1740 贪心双跑出现 50/1740 对错翻转；按[官方确定性指南](https://docs.vllm.ai/en/v0.11.1/usage/reproducibility/)关 V1 multiprocessing 后，同 GPU 的 dev352 双跑仍翻转 8/352。再启用 `enforce_eager=True` 后，dev352 两次逐题预测哈希完全一致；E08 统一采用该后端并另复跑一次完整 dev1740 base。后端 pilot 与成本见 E00 卡。

## 8. E09 本地替代教师的原始资产与边界

- `Qwen/Qwen3-32B@9216db5781bf21249d130ec9da846c4624c16137` 的 thinking 生成在 fvcrc10 A100 GPU0 跑了 20 次；temperature0.6/top-p0.95/top-k20、最大 3072 输出 token。相对论文 GPT-4o 它同时改变模型、解码、thinking、输出上限，**不属于原论文教师复现**。
- prompt、全部 raw、包括截断的记录、严格 manifest、GPU 型号及启动时 git SHA 留在 `/home/xiang/.cache/research/data-centric-rsi/runs/e09/`；执行脚本和审计脚本在 [`scripts/`](scripts/)，小结果在 [`results/E09_teacher_gate_audit.json`](results/E09_teacher_gate_audit.json)。原始生成脚本 SHA256 `bd3e1e87e3d74ee5729ab0f1dde7f5fe6876c63a541cc86e3f377710f70f6507`，事后审计不改原始 raw。
- 20 次占用 0.488 A100·时，其中冷加载约 10.7 分钟；生成 39,398 token。预注册严格数组格式只有 1/20 通过；允许单对象的事后诊断也仅 16/20 可解析，完整可训练题解 13/20。没有学生训练 checkpoint。详情与不扩张决定见 [E09](experiments/E09-qwen3-teacher-substrate-gate.md)。

## 9. E10 强静态状态资格门

- 数据选择脚本、固定输入哈希/960 ID 清单见 [`scripts/e10_prepare.py`](scripts/e10_prepare.py) 和 [`results/E10_data_manifest.json`](results/E10_data_manifest.json)；960 条 JSONL 与 adapter/全 dev 预测/训练日志保存在 `/home/xiang/.cache/research/data-centric-rsi/data/static_960_e10.jsonl`、`/home/xiang/.cache/research/data-centric-rsi/runs/e10/`。其数据 SHA256 为 `36f0338d996d2b66fee86ce6b50e4e663726a346197f1cbbbeb777908090d208`，重建时用 `source scripts/env.sh` 的 venv 和卡上命令，不覆盖已有资产。
- 三次评估均为 fvcrc10 A100 GPU0、同一 dev1740、同一 zero-shot＋显式格式/eager/V1 multiprocessing=0；结果在 [`results/E10_state_gate_analysis.json`](results/E10_state_gate_analysis.json)。960 独立训练 3 epoch/180 step、215,214 监督 token/epoch，训练与三次评估合计约 **0.337 A100·时**、API 0；更多数据和更多优化同时变化，不是论文 DataEnvGym 生成反馈或 E00 的精确重复。`static960` 不满足本卡预设的“更强且动作不同”资格门，故保留旧静态120作当前简单基线，不沿这一词面动作扩训练矩阵。

AZR 的固定 `paper` 分支源码另缓存在 `/home/xiang/.cache/research/data-centric-rsi/AZR`，SHA `41ed983cdf541cfcd2f963f33c055d50074f3c90`，重建可 `git clone --branch paper https://github.com/LeapLabTHU/Absolute-Zero-Reasoner.git` 后 checkout 该 SHA。仅审计关键入口，未执行：其 README 要求 7B 4×80GB，论文说每次 3–5 天 A800；自带 Python executor 直接执行候选代码且 README 标注不安全。若后续借验证任务，必须先用隔离执行环境并另开资源 gate，不将此克隆称为完成 AZR baseline。

## 10. E00–E10 后的针对性 substrate 审计（只读，无新 GPU）

| 候选 | 真实行动/反馈路径 | 当前确定的边界 | 研究用途判断 |
|---|---|---|---|
| DataEnvGym code，固定源码 `f698f39` | LiveCodeBench 学生错误→GPT-4o 生成新题→另一次模型调用解答→SFT→LCB 学生评估 | `code/baselines/open_ended.py` 的新训练题路径直接 `render_data_spec`，未见运行/测试新答案；`examples/livecodebench/open_ended.py` 为 8 GPU/5轮；评测学生代码的测试不验证新监督 | 与已建 MATH 资产共享框架，但可信生成数据仍是缺口，不能直接称“可验证代码行动” |
| SQLM code，官方源码 `fe1dd02ecf4ab4f3c398acd186c6caaa970cbd58` | proposer 给题和测试输出→solver rollout→SandboxFusion 评分→proposer/solver 更新 | `ray_trainer.py` 将 proposer 自给测试当 solver ground truth；`coding_selfplay.yaml` 为 4 GPU、tensor parallel4、依赖本地 SandboxFusion 服务；内部奖励并非独立真值 | 真正动态自博弈近邻，但大改小预算训练会偏离原论文；需先核测试可靠性与固定 proposer 强对照 |
| Curation-Bench，官方 README 2026-10-02 只读 | agent 提交固定池子集→冻结 SFT→八项 VLM 评价反馈 | 官方硬件前提 ≥1TB 磁盘；主要是固定池策展而非可生成验证题；当前未克隆源码/适配弱 I/O | 数据研究 agent 近邻和后续验证平台，不作轻量生成闭环的默认首跑 |
| AZR coder3b，固定 `paper` SHA `41ed983` | proposer 给 Python 程序/输入等→执行得目标→solver rollout 与 proposer reward→联合更新 | 仓库有两份各256行的 3B coder seed 数据；`scripts/selfplay/coder3b.sh` 为**单节点2×80GB**、vLLM TP2、长序列和30 epoch；原执行器运行模型生成代码，当前未隔离；3B 的终端强静态/冻结 proposer 对照尚未复核 | 目前最接近“独立可验证生成动作＋可在单节点运行”的候选，但不是已就绪 baseline；先核完整实验和隔离成本，不在共享节点直接执行原脚本 |

这张表回答的是“下一份实际训练值不值得花”，不宣布哪篇工作的科学空间被关闭。E11 的 OpenMath 静态数据比较已起草但**未下载/运行**，因它仍不能测反馈决策，暂时不占 GPU。
