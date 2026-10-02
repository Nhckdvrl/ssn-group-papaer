# 文献与阅读证据账本

核验日：2026-10-02。D=主文和与定位有关的附录定向深读；M=方法/实验关键节核对；A=摘要或官方元数据；N=只发现入口、未验证正文。D 不等于逐页审计全部证明、参考文献及代码。会议身份只写本轮由官方来源核实的；其余保守标为预印本，不根据检索摘要猜接收状态。

## 核心与近邻

| ID | 论文 / 版本 | 阅读 | 用途与来源 |
|---|---|---|---|
| P01 | Self-Play Pretraining with Zero Data, 2609.30063v1 | D＋PDF 图表＋作者资产 | [全文](https://arxiv.org/html/2609.30063v1)；§2–4、App A/B/E/F/G；PDF p10 Fig3/4、p31 Table5 |
| P02 | Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability / SOAR | D（v1），v3 核心与资源复核 | [v3](https://arxiv.org/html/2601.18778v3)；真实学生收益、nested compute、教师迁移 |
| P03 | RSIBench-Data, 2607.25886v1 | D＋官方 README | [全文](https://arxiv.org/html/2607.25886v1)；协议、六任务、选择偏差、限制 |
| P04 | DataEnvGym, 2410.06215v3，ICLR 2025 | D＋官方 README | [全文](https://arxiv.org/html/2410.06215v3)；[会议](https://proceedings.iclr.cc/paper_files/paper/2025/hash/846d3ef94d8c1a833a62cff05569c851-Abstract-Conference.html) |
| P05 | Can Generalist Agents Automate Data Curation? / Curation-Bench, 2606.04261v2 | D＋代码入口 | [全文](https://arxiv.org/html/2606.04261v2)；研究型 scaffold、昂贵强基线、跨模型迁移 |
| P06 | Anchored Self-Play for Code Repair, 2607.03523v1 | D（主文与训练配置），部分附录待补 | [全文](https://arxiv.org/html/2607.03523v1)；目标漂移、real anchors、冻结生成器基线 |
| P07 | Scaling Self-Play with Self-Guidance, 2604.20209v1 | M | [全文](https://arxiv.org/html/2604.20209v1)；目标引导、形式验证，完整算法/附录待补 |
| P08 | Self-Adapting Language Models / SEAL, 2506.10943v1 | D（主文与关键实验） | [全文](https://arxiv.org/html/2506.10943v1)；双层优化、自编辑、适配信号 |
| P09 | Self-Questioning Language Models, 2508.03682 | D（正文、超参与评估口径） | [全文](https://arxiv.org/html/2508.03682v1)；简洁 3B self-play，冻结 proposer 对照 |
| P10 | Absolute Zero, 2505.03335，NeurIPS 2025 | A＋方法概览，完整深读待补 | [论文](https://arxiv.org/abs/2505.03335)；[会议 PDF](https://papers.nips.cc/paper_files/paper/2025/file/9837dc00ff67d176373268ed48042d49-Paper-Conference.pdf) |
| P11 | PopuLoRA, 2605.16727v1 | M＋主表与计算口径 | [全文](https://arxiv.org/html/2605.16727v1)；群体、匹配、cross-play 已有所有权 |
| P12 | CurateEvo, 2607.06140v1 | A＋引言/框架 | [全文](https://arxiv.org/html/2607.06140v1)；失败驱动的数据代码演化近邻；不能冒充已全文审计 |
| P13 | Recursive self-improvement of AI research agents / AIDE², 2609.26457v1 | M（框架、主要限制） | [全文](https://arxiv.org/html/2609.26457v1)；系统级 RSI 与权重级 RSI 的区分 |
| P14 | Experimental Experience Modeling for Autonomous Research, 2609.39392v1 | D（主文含方法/实验/限制性读法） | [全文](https://arxiv.org/html/2609.39392v1)；经验库＋针对性 pilot 近邻 |
| P15 | AutoLLMResearch, 2605.11518v1 | M（方法、数据混合环境、跨保真与成本） | [全文](https://arxiv.org/html/2605.11518v1)；不能 claim 首次跨尺度实验经验迁移 |
| P16 | PAC, 2608.30528v1 | M（方法、课程轨迹与定位） | [全文](https://arxiv.org/html/2608.30528v1)；更新强度＋真实进度组合已存在 |

## 已核验的基础锚点：用于谱系，不假称都已深读

| ID | 论文 | 阅读 | 官方来源 |
|---|---|---|---|
| P17 | STaR，NeurIPS 2022 | A | [会议页](https://papers.nips.cc/paper_files/paper/2022/hash/639a9a172c044fbb64175b5fad42e9a5-Abstract-Conference.html) |
| P18 | Self-Instruct，ACL 2023 | A / 引用链 | [论文](https://arxiv.org/abs/2212.10560) |
| P19 | DoReMi，NeurIPS 2023 | A | [会议页](https://papers.nips.cc/paper_files/paper/2023/hash/dcba6be91359358c2355cd920da3fcbd-Abstract-Conference.html) |
| P20 | DoGE，ICML 2024 | A | [会议页](https://proceedings.mlr.press/v235/fan24e.html) |
| P21 | LESS，ICML 2024 | A | [会议页](https://proceedings.mlr.press/v235/xia24c.html) |
| P22 | ADO，ICLR 2025 | A | [会议页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/923285deb805c3e14e1aeebc9854d644-Abstract-Conference.html) |
| P23 | Universal pre-training by iterated random computation, 2506.20057 | A / P01 引用链 | [论文](https://arxiv.org/abs/2506.20057) |
| P24 | LANCE, EMNLP 2025 main | A | [会议 PDF](https://aclanthology.org/2025.emnlp-main.914.pdf) |
| P25 | SPIRAL, 2506.24119 | A | [论文](https://arxiv.org/abs/2506.24119)；本轮不据二手摘要填写会议状态 |
| P26 | SPELL, 2509.23863，ICLR 2026 | A | [会议 PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/61af4e55bbc1e29b4f8e2669a829a683-Paper-Conference.pdf) |
| P27 | PiKE，NeurIPS 2025 | A | [会议 PDF](https://papers.nips.cc/paper_files/paper/2025/file/f7a94134f1c726796c6f81fb946e489d-Paper-Conference.pdf) |
| P28 | The Last AI Built by Humans: Toward Genuine RSI, 2609.11873 | A＋相关分类节 | [综述/观点](https://arxiv.org/html/2609.11873v1)；不是成功 RSI 的实证证明 |
| P29 | Self-Improvements in Modern Agentic Systems: A Survey, 2607.13104 | A | [综述](https://arxiv.org/html/2607.13104v1) |
| P30 | A Survey on Self-Evolution of Large Language Models, 2404.14387 | A | [综述](https://arxiv.org/html/2404.14387v2) |

## 最新入口与本轮未解决的阅读债务

- 检索到 `Effective Synthetic Data Curation Requires Group-Level Signals` / 2610.00779 的列表条目，但直接摘要/HTML 抓取失败，**不将其内容当已核实证据**。任何 group-interaction 叙事开始前补核验。
- `Learning at the Right Pace` / 2606.22305、`Gap-Adaptive Teacher Scheduling` / 2609.37898：只发现入口，暂不据此写方法事实。
- 补读 AZR、CurateEvo、SGS 的全套方法和训练代码，再决定哪一套值得做正式 method baseline；目前只把它们当定位边界。
- P20/P21/P22/P27 的方法及强实现必须在开展数据价值估计前补齐。官方会议元数据核验不等于 baseline 复现。
- 为候选阶段补齐近期接收论文、公开评审和 venue corpus 的系统审计；本轮没有完成“最近十篇接收论文全部全文＋公开评审”的 D5 标准。
