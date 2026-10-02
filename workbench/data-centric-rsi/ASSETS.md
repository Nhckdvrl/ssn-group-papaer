# 资产核验与资源契约

更新：2026-10-02。已做远程论文/README/模型卡核验；**未下载模型、未安装依赖、未完成 GPU benchmark**。通用边界继承 [RESOURCES.md](../../RESOURCES.md)。

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

上游入口可能更新；执行时先记录 commit/revision，而不是把本文日期当版本锁。

## 2. 原论文成本与本地可行性不是一回事

- **SOAR**：论文 v3 App B.9 为 32×H100/H200、48–60h/run；不是“3B 因而单卡随便跑”。其完整嵌套训练不适合作为默认探索起点。
- **ASP**：论文训练配置为约 8×H100、48h，另有程序执行/验证负担；单节点不代表廉价。
- **P01**：小模型、长 token budget、多个 reward arm 与 seed/超参搜索。已发布结果可低成本复核；完全重做训练 grid 的成本仍需另算。
- **RSIBench-Data**：名义预算为 run 16h/$500 Tinker；这既不是纯 GPU 小时，也不是我们的本地费用预测。
- **DataEnvGym**：论文显示 2B 级学生可进行较短迭代；它的历史时长不作为当前机器承诺，实际完整闭环的耗时由 E00 测量。

论文来源：[SOAR](https://arxiv.org/html/2601.18778v3)、[ASP](https://arxiv.org/html/2607.03523v1)、[P01](https://arxiv.org/html/2609.30063v1)、[RSIBench](https://arxiv.org/html/2607.25886v1)、[DataEnvGym](https://arxiv.org/html/2410.06215v3)。不做 H100→A100/PRO/H20 的未经测量换算。

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
