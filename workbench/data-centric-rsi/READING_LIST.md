# 文献与阅读证据账本

核验日：2026-10-03。D=主文和与定位有关的附录定向深读；M=方法/实验关键节核对；A=摘要或官方元数据；N=只发现入口、未验证正文。D 不等于逐页审计全部证明、参考文献及代码。会议身份只写本轮由官方来源核实的；其余保守标为预印本，不根据检索摘要猜接收状态。

## 核心与近邻

| ID | 论文 / 版本 | 阅读 | 用途与来源 |
|---|---|---|---|
| P01 | Self-Play Pretraining with Zero Data, 2609.30063v1 | D＋PDF 图表＋作者资产 | [全文](https://arxiv.org/html/2609.30063v1)；§2–4、App A/B/E/F/G；PDF p10 Fig3/4、p31 Table5 |
| P02 | Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability / SOAR | D（v1），v3 核心与资源复核 | [v3](https://arxiv.org/html/2601.18778v3)；真实学生收益、nested compute、教师迁移 |
| P03 | RSIBench-Data, 2607.25886v1 | D＋官方 README | [全文](https://arxiv.org/html/2607.25886v1)；协议、六任务、选择偏差、限制 |
| P04 | DataEnvGym, 2410.06215v3，ICLR 2025 | D＋全文附录重读＋固定源码关键路径审计 | [全文](https://arxiv.org/html/2410.06215v3)；[会议](https://proceedings.iclr.cc/paper_files/paper/2025/hash/846d3ef94d8c1a833a62cff05569c851-Abstract-Conference.html)；[源码 f698f39](https://github.com/codezakh/dataenvgym/tree/f698f39c7d77fc655942099535d06a4d11b32e3b) |
| P05 | Can Generalist Agents Automate Data Curation? / Curation-Bench, 2606.04261v2 | D＋固定源码/强LESS发布边界复核 | [全文](https://arxiv.org/html/2606.04261v2)；研究型 scaffold、昂贵强基线、换模型/池各自重跑 10 轮；未报冻结策略跨 episode 迁移；33.6三run适配/库/manifest未发布，不能冒充已本地复现 |
| P06 | Anchored Self-Play for Code Repair, 2607.03523v1 | D（主文与训练配置），部分附录待补 | [全文](https://arxiv.org/html/2607.03523v1)；目标漂移、real anchors、冻结生成器基线 |
| P07 | Scaling Self-Play with Self-Guidance, 2604.20209v1 | M | [全文](https://arxiv.org/html/2604.20209v1)；目标引导、形式验证，完整算法/附录待补 |
| P08 | Self-Adapting Language Models / SEAL, 2506.10943v1 | D（主文与关键实验） | [全文](https://arxiv.org/html/2506.10943v1)；双层优化、自编辑、适配信号 |
| P09 | Self-Questioning Language Models, 2508.03682 | D（正文、超参与评估口径） | [全文](https://arxiv.org/html/2508.03682v1)；简洁 3B self-play，冻结 proposer 对照 |
| P10 | Absolute Zero / AZR，2505.03335v3，NeurIPS 2025 main | D（全文方法/主表/B/D 附录；固定 `paper` 分支关键源码已审，未复现） | [全文](https://arxiv.org/html/2505.03335)；[会议 PDF](https://papers.nips.cc/paper_files/paper/2025/file/9837dc00ff67d176373268ed48042d49-Paper-Conference.pdf)；[代码](https://github.com/LeapLabTHU/Absolute-Zero-Reasoner)；可执行题/答案、联合训练与强 solver-only 消融 |
| P11 | PopuLoRA, 2605.16727v1 | M＋主表与计算口径 | [全文](https://arxiv.org/html/2605.16727v1)；群体、匹配、cross-play 已有所有权 |
| P12 | CurateEvo, 2607.06140v1 | D（全文方法/related work/主表、消融与 B/C/D 附录；未核到官方可执行代码） | [全文](https://arxiv.org/html/2607.06140v1)；失败轨迹→代码演化→同父重训，分别适配 labeled/wild，联合改变 SFT/RL/推理记忆 |
| P13 | Recursive self-improvement of AI research agents / AIDE², 2609.26457v1 | M（框架、主要限制） | [全文](https://arxiv.org/html/2609.26457v1)；系统级 RSI 与权重级 RSI 的区分 |
| P14 | Experimental Experience Modeling for Autonomous Research, 2609.39392v1 | D（主文含方法/实验/限制性读法） | [全文](https://arxiv.org/html/2609.39392v1)；经验库＋针对性 pilot 近邻 |
| P15 | AutoLLMResearch, 2605.11518v1 | M（方法、数据混合环境、跨保真与成本） | [全文](https://arxiv.org/html/2605.11518v1)；不能 claim 首次跨尺度实验经验迁移 |
| P16 | PAC, 2608.30528v1 | M（方法、课程轨迹与定位） | [全文](https://arxiv.org/html/2608.30528v1)；更新强度＋真实进度组合已存在 |
| P21 | LESS，ICML 2024；2402.04333v3 | D（全文方法/结果/相关工作/关键附录；核心代码已读，未复现） | [全文](https://arxiv.org/html/2402.04333v3)；[会议](https://proceedings.mlr.press/v235/xia24c.html)；Adam influence、warmup、跨模型迁移及失败边界 |
| P20 | DoGE，ICML 2024；2310.15393v2 | D（全文方法/结果/附录阶段课程；代码未复现） | [全文](https://arxiv.org/html/2310.15393)；[会议](https://proceedings.mlr.press/v235/fan24e.html)；目标梯度、静态平均胜阶段更新 |
| P22 | ADO，ICLR 2025；2410.11820v1 | D（全文方法/结果/训练附录；代码未复现） | [全文](https://arxiv.org/html/2410.11820)；[会议](https://proceedings.iclr.cc/paper_files/paper/2025/hash/923285deb805c3e14e1aeebc9854d644-Abstract-Conference.html)；在线潜力、强 Natural 基线 |
| P31 | Actor-Curator，2602.20532v1；ICLR 2026 workshop，非主会接收证据 | D（全文方法/主表/限制；官方 README，源码内部未审计） | [全文](https://arxiv.org/html/2602.20532)；[代码](https://github.com/actor-curator/actor-curator)；一次共享 actor 更新后的逐题效用估计、在线 bandit curator；MATH500 并非普遍胜出 |
| P32 | Effective Synthetic Data Curation Requires Group-Level Signals，2610.00779v1；新预印本 | D（全文、related work、配方/成本附录及理论推导；未复现） | [全文](https://arxiv.org/html/2610.00779v1)；单步组 oracle 与逐条 proxy 的差、合成改写倍率、梯度离散度预算诊断；未覆盖连续数据改进器 |
| P33 | Group-MATES，NeurIPS 2025 main；2502.14709v2 | D（方法、22 项主实验、消融与成本附录；源码入口，未复现） | [会议](https://proceedings.neurips.cc/paper_files/paper/2025/hash/e389ad5c08184ebecaf0640e01588489-Abstract-Conference.html)；[全文](https://arxiv.org/html/2502.14709)；关系影响模型＋训练轨迹＋两阶段选择 |
| P34 | BLISS，ICML 2026 main；2510.06048v5 | D（方法、主表、关键附录；源码入口，未复现） | [会议](https://proceedings.mlr.press/v306/hao26b.html)；[全文](https://arxiv.org/html/2510.06048)；多步 bilevel proxy、动态评分、强 MATES 对照与实际 wall/显存成本 |
| P35 | PDS / Data Selection via Optimal Control，ICLR 2025 main；2410.07064 | D（全文方法、related work、主表、动态信息/G/E 附录；官方代码入口，未复现） | [会议](https://proceedings.iclr.cc/paper_files/paper/2025/hash/9ad4891facabf17aa11580686bacfe4e-Abstract-Conference.html)；[全文](https://arxiv.org/html/2410.07064)；多阶段代理求分、可复用静态选样与实际求分成本 |
| P36 | Learning at the Right Pace / ADS，2606.22305v1；预印本 | D（全文方法、related work、主表、消融与成本/限制附录；代码入口，未复现） | [全文](https://arxiv.org/html/2606.22305)；[代码](https://github.com/Richard-zrx/ADS)；GRPO 中语义群×能力边界在线排程，强 DOTS+RR 对照 |
| P37 | Montessori-Instruct，ICLR 2025 main；2410.14208v1 | D（全文方法、related work、主表、teacher/学生消融、迁移与成本附录；代码入口，未复现） | [会议](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ba1d33849b963efc6b5d3082ad68f480-Abstract-Conference.html)；[全文](https://arxiv.org/html/2410.14208)；局部 student influence→teacher DPO→跨学生数据迁移 |
| P38 | The Signal is in the Steps / LALP，ICML 2026 main；2510.03988v2 | D（全文方法、related work、主表、B/C 附录与主要混杂；代码入口，未复现） | [会议](https://proceedings.mlr.press/v306/just26a.html)；[全文](https://arxiv.org/html/2510.03988)；混合长推理 teacher 中局部概率选答案，需注意 teacher-mixture 控制 |
| P39 | OpenMathInstruct-2，ICLR 2025 main；2410.01560v2 | D（全文、A–C 附录、发布数据字段；NeMo Skills 内部尚未审计） | [会议](https://proceedings.iclr.cc/paper_files/paper/2025/hash/302ce0673c00aee2cf84bb43d0117553-Abstract-Conference.html)；[全文](https://arxiv.org/html/2410.01560)；[数据](https://huggingface.co/datasets/nvidia/OpenMathInstruct-2)；强 teacher、解答格式、题目多样性与过滤的真实 SFT 对照 |
| P40 | DUET，ICLR 2026 main；2502.00270v3 | D（方法/主结果/成本与关键附录；官方 BO 代码已核，未复现） | [全文](https://arxiv.org/html/2502.00270v3)；黑箱目标反馈→GP/BO 域配比，论文 50 次随机初始化＋10 次 BO |
| P41 | Data Mixing Agent，ACL 2026 main；2507.15640v2 | D（引言/方法/related work/主表、C–E 附录与限制；官方可运行源码未核） | [会议](https://aclanthology.org/2026.acl-long.427/)；[全文](https://arxiv.org/html/2507.15640v2)；384 代理轨迹、CQL 学固定域课程，数学→代码的冻结 agent 迁移 |
| P43 | Data Agent，ICML 2026 main；2603.07433v2 | D（全文方法、主表/消融/成本及官方 README；未运行代码） | [会议](https://proceedings.mlr.press/v306/yang26bq.html)；[全文](https://arxiv.org/html/2603.07433)；训练内 PPO 逐样本选样、loss+熵奖励；公开执行示例主要覆盖 CIFAR |
| P44 | Can Small Training Runs Reliably Guide Data Curation?，2512.24503v2；预印本 | D（主文、近邻分类、D.1–D.2 配方/机制/时长；代码未核） | [全文](https://arxiv.org/html/2512.24503)；23 预训练配方的固定超参代理排序可能翻转，低 LR 代理与调参目标更一致；不直接覆盖同模型固定 SFT 的 E12 |
| P45 | On the Difficulty of Learning a Meta-network for Training Data Selection，ICML 2026 main；2606.00571v1 | D（全文方法、§5 主表与消融、F–I 数据/基线/特征附录；代码 README 已核、源码未全审） | [会议](https://proceedings.mlr.press/v306/du26u.html)；[全文](https://arxiv.org/html/2606.00571v1)；选择器学不好可由超梯度低 GSNR 与信息不足共同造成，非 E12 直接 baseline |
| P46 | Data Mixture Optimization: A Multi-fidelity Multi-scale Bayesian Framework，NeurIPS 2025 main | D（全文及 A–E 附录；官方代码的 simulator、benchmark、BO 更新关键路径已核，未复现） | [会议全文](https://papers.nips.cc/paper_files/paper/2025/file/8e49d32f4668a41b013fbc1ed929c007-Paper-Conference.pdf)；[代码](https://github.com/namkoong-lab/data-recipes)；472 次真实预训练构建模拟器，2.6–3.3× 搜索加速在模拟器上验证；多保真/跨模型 BO 是强非 agent 近邻 |
| P47 | Once-For-All: A Train-Once and Select-Anytime Framework for Multimodal Instruction Tuning，2605.26761v2；预印本 | D（全文方法/related work、全部结果与敏感性表、A 伪代码/B 限制；未复现） | [全文](https://arxiv.org/html/2605.26761v2)；冻结 CLIP＋聚类伪标签的早停 selector，LLaVA→未见 Vision-Flan 不重训/不重聚类，同一选样跨 LLaVA/Qwen；阈值与跨池分组语义待核，未核到 OFA 官方可执行发布 |
| P48 | XMAS，ICML2026 主会；会议最终版 | D（29页主文/A–E附录含理论、图表；官方proxy/求分/聚类/采样/目标训练关键代码已审，未复现） | [会议全文](https://raw.githubusercontent.com/mlresearch/v306/main/assets/naharas26a/naharas26a.pdf)；[代码 e534dd9](https://github.com/BigML-CS-UCLA/XMAS/tree/e534dd99e9ce9b7be345bd55e055c9b4e5c91c90)；跨模态谱轨迹、簇均衡/稳定采样，真实跨目标架构复用；矩阵距离理论与谱标量桥梁、公开实现模板/QK次序/脚本参数债务见论文卡 |
| P49 | Let the Target Select for Itself / TACS，2605.09404v2；预印本 | D（主文与A–G附录定向深读；官方warmup/评分/校准/选样/训练/成本关键代码已审，未运行） | [全文](https://arxiv.org/html/2605.09404v2)；[代码35e97be](https://github.com/davidyht/TACS/tree/35e97bee2cbfcba72b7c359e34a74287955d303b)；rank1目标适配→候选归一化loss下降→base重置rank128主训；固定模型—目标对跨池复用，非跨目标/学生冻结迁移，最终评分规则须显式指定 |

| P50 | ICONS，2501.00654v4；会议身份未独立核实 | D（主文与A–F关键附录；官方梯度/投影/影响/投票/写出/目标训练关键代码已审；图像只核解释与图注，未重构梯度库） | [全文](https://arxiv.org/html/2501.00654v4)；[代码b8ce8c8](https://github.com/princetonvisualai/icons/tree/b8ce8c86d7b098836a84ec2b40d259195b7f4494)；多任务分位投票、跨任务/模型复用和预算/warmup消融已拥有；E12是公开133K池内随机10K，不是原方法10K重求票，成本与语义边界见论文卡 |
| P51 | Adapt-∞，ICLR2025主会；2410.10636v2 | D（主文及A/B/C相关附录；官方指定student求分/拼池/选样/训练接口已定向审，未复现） | [会议](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a6610efd6c767f63343a4ab28505212e-Abstract-Conference.html)；[全文](https://arxiv.org/html/2410.10636v2)；[代码d1b1b25](https://github.com/adymaharana/adapt-inf/tree/d1b1b25946379b61113a231693452d961d44de48)；动态伪skill/score专家、强random、Fig9新记录恢复旧skill已拥有；8A100下wall不抄成GPU小时 |
| P52 | OASIS，ACL2026主会最终版 | D（主文、A.2配方/基线/成本/算法/跨规模相关附录；证明假设定向核，2026-10-03官方repo empty/无refs，未复现） | [会议全文](https://aclanthology.org/2026.acl-long.158/)；在线当前FI/跨batch统计Bernoulli＋组内冗余，三seed；infinite memory-only retrieval，不能当永不重放的有限流；代码缺失不削弱论文ownership，阅读边界见论文卡 |
| P53 | OPUS，2602.05400v2；预印本 | D（独立agent主文/推导/全部结果表及固定评分/训练源码；未复现） | [全文](https://arxiv.org/html/2602.05400v2)；[代码eb9390](https://github.com/gszfwsb/OPUS/tree/eb939016d76adfd0b1681ba8631bca0931c9125f)；optimizer更新空间在线选择＋组内冗余，真实GPT2/Qwen全参训练；冻结二阶矩是明确近似，不预判失效 |
| P54 | A Critical Look at Targeted Instruction Selection，ICML2026主会最终版；arXiv v2 | D（主文与B/D/E/F/G/J/M/N/O定向附录、理论前提；图表读趋势/图注，Trainer/LESS接口定向核，未复现） | [会议](https://proceedings.mlr.press/v306/nayak26a.html)；[最终PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/nayak26a/nayak26a.pdf)；[代码c1dc028](https://github.com/dcml-lab/targeted-instruction-selection/tree/c1dc0286b06b9e2a857d925e516938f4c9619dc2)；representation×algorithm×budget、强random/base、多pool/model、135M proxy复用；不因它拥有系统测量就关题 |
| P55 | Filter-then-Weight，2604.00001v2；预印本 | M（方法/关键SFT结果与重权重消融，全部附录/源码未补齐，未复现） | [全文](https://arxiv.org/html/2604.00001v2)；optimizer-aware filter＋非负组权重、LoRA SFT真实效用，组合不再空白；正式发展备选前补全深读 |
| P56 | VisNec，2603.01195v2；预印本 | D（独立agent完整18页无附录主文/related work及score/selection/多模态展开源码；未复现） | [全文](https://arxiv.org/html/2603.01195v2)；[代码1c12fde](https://github.com/DMK041218/VisNec/tree/1c12fdeb5dc2be54d449726bbabde722e5133a26)；blind/full loss差＋覆盖约束已实证；Text只改选择信号，不是blind训练；与P47/OFA不同资产 |
| P57 | ViFT，EMNLP2025 Findings；解释近邻非主会尺度锚点 | D（主文/方法/结果/训练数据与A/C–E相关附录，示例表及源码未全审） | [官方全文](https://aclanthology.org/2025.findings-emnlp.547/)；文本任务/视觉caption分训与表示融合已有方法/效用，不能占宏观故事；引用近邻不表示投Findings |

## 已核验的基础锚点：用于谱系，不假称都已深读

| ID | 论文 | 阅读 | 官方来源 |
|---|---|---|---|
| P17 | STaR，NeurIPS 2022 | A | [会议页](https://papers.nips.cc/paper_files/paper/2022/hash/639a9a172c044fbb64175b5fad42e9a5-Abstract-Conference.html) |
| P18 | Self-Instruct，ACL 2023 | A / 引用链 | [论文](https://arxiv.org/abs/2212.10560) |
| P19 | DoReMi，NeurIPS 2023 | A | [会议页](https://papers.nips.cc/paper_files/paper/2023/hash/dcba6be91359358c2355cd920da3fcbd-Abstract-Conference.html) |
| P23 | Universal pre-training by iterated random computation, 2506.20057 | A / P01 引用链 | [论文](https://arxiv.org/abs/2506.20057) |
| P24 | LANCE, EMNLP 2025 main | A | [会议 PDF](https://aclanthology.org/2025.emnlp-main.914.pdf) |
| P25 | SPIRAL, 2506.24119 | A | [论文](https://arxiv.org/abs/2506.24119)；本轮不据二手摘要填写会议状态 |
| P26 | SPELL, 2509.23863，ICLR 2026 | A | [会议 PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/61af4e55bbc1e29b4f8e2669a829a683-Paper-Conference.pdf) |
| P27 | PiKE，NeurIPS 2025 | A | [会议 PDF](https://papers.nips.cc/paper_files/paper/2025/file/f7a94134f1c726796c6f81fb946e489d-Paper-Conference.pdf) |
| P28 | The Last AI Built by Humans: Toward Genuine RSI, 2609.11873 | A＋相关分类节 | [综述/观点](https://arxiv.org/html/2609.11873v1)；不是成功 RSI 的实证证明 |
| P29 | Self-Improvements in Modern Agentic Systems: A Survey, 2607.13104 | A | [综述](https://arxiv.org/html/2607.13104v1) |
| P30 | A Survey on Self-Evolution of Large Language Models, 2404.14387 | A | [综述](https://arxiv.org/html/2404.14387v2) |

## 最新入口与本轮未解决的阅读债务

- P32 已从官方 arXiv 全文核实；若发展 group-interaction 叙事，先明确与其一次组更新及 GMRel/GREATS 的增量，不把它的存在当自动判死。
- P49 已有目标低容量真实适配轨迹、候选前向响应评分及跨池摊销；Dolly→TyDiQA分数带经真实三seed重训支持效用排序。9例proxy/64epoch、缺失目标能力和有限子集理论范围是作者承认的压力，不自动成为我们delta。代码已发布且已审关键路径；默认metric/rank与最终协议不同，正式复现仍需固定全参数/模板/行序。仓库称ICLR final，正式接收记录未核，不猜会议身份。
- P47 已有冻结跨池/跨模型静态复用实证；不能沿用“此前 selector 都须随模型重算”的引言概括。其源外簇归属、按簇 15% 与固定 0.7 阈值的关系、示例高/低置信文案仍有复现阅读债务。标题/编号的 GitHub/HF 检索及作者公开仓库核查未核到 OFA 代码或选样清单；[VisNec 作者仓库](https://github.com/DMK041218/VisNec)虽引用 OFA，却明确发布另一论文的 VisNec 数据/LoRA，不能混用。XMAS 已补读会议最终全文和关键源码，独立记为 P48；COINCIDE 仍仅定向核方法和 proxy→target 契约，Self-Filter 仅核官方摘要，二者未完成独立深读/复现。
- 本轮围绕 frozen VLM selector 运行 venue corpus `nearest`（k=5），返回 Adapt-∞ 等持续多模态选择近邻；P51/P52已补读主文与关键附录，代码正在核，不据检索分数或标题判精确撞车，不宣称已完成D5全面扫描/公开评审审计。
- `Gap-Adaptive Teacher Scheduling` / 2609.37898：只发现入口，暂不据此写方法事实。
- CurateEvo 论文主文/附录已深读，官方完整执行源码仍未核到；SGS 的全套方法和代码仍需补读。是否把 CurateEvo 作为正式方法基线要由目标动作/反馈问题决定；AZR 已深读并审固定源码入口，但未复现。
- P20/P22/P27 的方法及强实现、P21/LESS 的官方代码执行路径，必须在把它们当正式数据价值估计 baseline 前补齐。官方会议元数据与论文深读不等于 baseline 复现。
- 为候选阶段补齐近期接收论文、公开评审和 venue corpus 的系统审计；本轮没有完成“最近十篇接收论文全部全文＋公开评审”的 D5 标准。
