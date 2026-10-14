# 矿区 A 的最近邻与 idea 来源分析（2026-10-14）

下文保留初次阅读快照。**2026-10-14 已读指定正文方法/关键附录/表格并执行E07/E08**；4张新论文卡在 `../papers/`，PCSP全链与原生动作最新审计在 [SOURCE_AUDIT](SOURCE_AUDIT_2026-10-14.md)。仍未复现作者完整模型数字，不能把局部CPU核验升级为全文实证复现。

最新必须补入的近邻：[ReflAct（EMNLP2025）](https://aclanthology.org/2025.emnlp-main.1697/)已研究goal-state reflection；[ReFract（2026-10-02）](https://arxiv.org/abs/2610.03356)已有role-calibrated intent/knowledge/capability与可执行Text World Model。前者对位置/goal grounding有直接ownership，后者角色权限与我们当前观测视角归属不同但构成强近邻；正文/附录继续审计中。P02不能靠“在NPC中发现位置没接上角色”自动成为idea。

## 1. The Personality Illusion — ICML 2026 正式主会
[正式 PMLR](https://proceedings.mlr.press/v306/han26n.html) / [作者代码](https://github.com/psychology-of-AI/Personality-Illusion) / [arXiv](https://arxiv.org/abs/2509.03730)；本轮 P1 paper + P2 repo/data。
- **DOCUMENTED**：研究心理量表自述、风险选择/阿谀/诚实等具体行为、persona injection；发现自述人格不可靠地预测行为，persona 注入会改变自述但行为效果小或不稳定。
- **RECONSTRUCTED 研究动作**：人们用低价问卷代表人格 → 需要行为实验检验预测效度 → 不只测报告相关性，还控制模型对齐阶段和persona定向注入。
- **强定位**：用户提出的“角色说得像但策略不一样”已有非常接近且成熟的 owner；游戏NPC论文需要超出普通人格/行为相关性，找到**自然游戏中角色/玩家利益、合法行动与世界后果**的新知识。不要先猜“RLHF讨好先验主导”。

## 2. Rethinking Psychometric Evaluation — 2026 NeurIPS 作者声称接收
[预印本](https://arxiv.org/abs/2606.12730) / [作者开源](https://github.com/psychology-of-AI/Rethinking-Pyschometric-Eval-LLMs)；本轮 P1/局部 P2 code。作者 README 标注 NeurIPS2026，**未独立核对官方 main proceedings**；2026 ICML CTB workshop oral 不等于 ICML main。
- **DOCUMENTED**：2×2×2 框架比较 BigFive vs Theory of Planned Behavior（TPB）、同会话 vs 跨会话、参数网格 vs persona；作者报告情境化/行为化测量能提高可预测性，BigFive在具体任务上很弱。同一对话本身可能引入 priming/额外信息，应审计不能当独立行为证据。
- **RECONSTRUCTED**：最初自述-行为不一致 → 可能是心理指标尺度/上下文错位，而不是模型人格不存在 → 细化构念 + 强测量因果混杂。
- **影响**：矿区 A 首个竞争解释必须包含**粗粒度测量失配和上下文匹配效应**。若这些足以解释 NPC 故事/选择差异，仍是前人已有方向的延展，需验证实际游戏动作的新内容。

## 3. The Story Shapes the Agent — arXiv 2607.18566（2026）
[论文](https://arxiv.org/abs/2607.18566)；本轮 P1 原始摘要与索引，未确认顶会录用、代码尚未核实。
- **DOCUMENTED 作者报告**：三种文本调查游戏保持动作空间/阶段/资源约束同构，仅换疾病调查/IT故障/谋杀谜案叙事；共1890 sessions，3模型10 personas；故事框架的行为方差可达persona的5–31倍；直接与动作词汇关联的角色锚点有跨故事迁移优势，作者报告删去 anchor words 令某类转移一致性降95%。
- **RECONSTRUCTED**：普通 persona 与动作对比可能只是叙事先验 → 使用结构同构任务，将“故事”与决策结构解耦 → 再对具体词锚做小干预。
- **强限制**：**“叙事故事比人设更能影响决策”已经被这篇研究**，不能换 NPC 外壳后当成原创。需要看它是否有真正 NPC 自身目标、玩家互动与后续世界状态、是否排除角色与行动词汇不匹配；不能仅凭 abstract 把结论全推广。

## 4. Persona Vectors in Games — arXiv 2603.21398
[论文](https://arxiv.org/abs/2603.21398)；本轮 P1 摘要，代码/会场未确认。
- **DOCUMENTED 作者报告**：博弈场景中构造利他/宽恕/他人预期的 activation vectors，steering 改变策略选择和语言依据，并发现措辞/战略不一定同步。并非人物多角色 RPG 的完整实测。
- **限制**：用 activation steering 影响“战略行为”已有近邻，不能先跑 probes 再称发现“可分离人格策略表征”；若要做需至少核作者做过的因果干预、向量层、数据与真正执行决策。

## 5. PCSP — One Policy, Infinite NPCs, arXiv 2605.23652
[论文](https://arxiv.org/abs/2605.23652) / [源码](https://github.com/yoosunghong/pcsp) / [作者独立行为结果](https://github.com/yoosunghong/pcsp/blob/main/research/docs/evaluations/independent-behavior.md)；本轮 P2 指定源码。
- **DOCUMENTED**：Mini-Inzoi生活模拟中 frozen persona embedding→共享条件政策 PPO、contrastive与diversity，作者已经对400/100 train/held-out personas+3 seeds 进行独立行动特征审计；行为 probe full 0.482 vs no_consist 0.511（action-only），action+state 0.556 vs0.558。此差异是**作者的发现**。
- **方法/度量注意**：Mini-Inzoi v3 的游戏奖励本身就用动作是否属于 persona.preferred_actions 加0.5、与 BigFive 对应 ACTION_STYLE_PROFILE 的余弦加0.3；策略在该环境中学到“风格”可能部分是直接优化了研究者指定的行为图谱。不能把模型学会 reward 定义直接外推成“人类真正感到人物有独特利益”。
- **RECONSTRUCTED**：可控制上千 NPC 成本高 → 低成本条件策略，轨迹→persona信息对齐 → 需要外部行为验证。
- **未来有价值的检验**：独立于 style reward 的真实游戏行为/目标/关系是否被角色设定控制。**这是需要在自然任务和强对照中检验的研究空间，不是已经证明其外部行为毫无意义。**

## 6. RPG/真实世界任务近邻
- [LIGHT/How to Motivate Your Dragon](https://aclanthology.org/2021.naacl-main.64/)：角色原生动机/对话+物理行动；适于角色利益对照，但旧代码/任务归档待恢复，示范平均动作短，不宣称完整强本地基线。
- [CDT ACL2026](https://aclanthology.org/2026.acl-long.568/)：情景化人物决策树已研究，默认 GPT4.1 构建逻辑/评分不免费；不能把“把persona写成if-else”当创新。
- [KNUDGE EMNLP2024](https://aclanthology.org/2024.emnlp-main.520/)：RPG作者侧自然任务知识/对话图，不自动变在线行动 policy。
- [ccb/agent-sandbox](https://github.com/ccb/agent-sandbox)：MIT学术研究工程，具备世界前提/动作后果和 NPC 自己目标/人格，是低成本引擎候选而**非顶会NPC方法强基线**。

## 不能宣称新颖的五个句子
“LLM报告的人格和行为不一致”；“人格prompt影响语言比行为明显”；“叙事模板比persona强”；“加入外部persona向量能调策略”；“PCSP内部contrastive指标和独立行为一致”。这五句话要么被近邻做过、要么最后一句不符合作者独立行为报告。矿区A只能从可信真实游戏任务、新解释/控制边界、新独立测量及有效方法推进。

## 2026-10-14追加强近邻：FAccT2026
[When Identity Overrides Incentives](https://arxiv.org/html/2601.10102)，已读方法/Appendix F/G/H/I，卡见../papers/IDENTITY_OVERRIDES_INCENTIVES_2026.md。persona×payoff显式化交互、模型族差异，以及payoff优先/角色rename强prompt已被覆盖；不能给已知现象改名。我们当前原生NPC准入还不是新科学增量。

## 2026-10-14后续邻居定位
ACL2026 FAIRGAMER已研究transaction/cooperation/competition属性偏差与重复输出分布；2026 Intentional Deception已研究RPG profile条件下的动机操纵、true-statement misdirection与follow/echo。论文卡分别在../papers/FAIRGAMER_2026.md和INTENTIONAL_DECEPTION_2026.md；不把角色/激励交互、真话说服或模式改名当新idea。后者完整代码未公开，前者已读SDK/query统计路径，不冒称完整native engine。

继续正文/附录审计：HARBOR（IJCNLP-AACL2025）已有persona偏好与利润权衡、ToM/ExpertAct/DPO；SPASM已有同会话说话者视角投影/echo；AgentMark已有计划与执行分解及分布保持行为水印；TriEx已有扑克三视角解释审计、显式belief数值干预和50次rerun控制；FPPS已有个性化历史诱发事实扭曲与内部steering。对应卡均在../papers/，原生NPC框架的工程归因不能自动冒领这些机制。

PCSP比初次审计更强：正文§V-E已有50 English designer personas、语言/embedding→projection/行为overlap；作者ood-leakage-audit已测模板/两对韩语同义及排除近邻敏感性。MeltingPot PHASE5 §9–12已有candidate pool、平衡采样、两substrate各8seed、projection geometry/ID-OOD tradeoff。相关数字为作者结果，尚未本地完整复现；I02的“readout不同于policy”本身没有新颖性。

I02定位查询（2026-10-14）：venue corpus nearest已运行，候选包括Consistent Zero-Shot Imitation with Contrastive Goal Inference、Diverse Policies Recovering via PMI、PCSP；最新arXiv检索发现ECLIPTICA/CITA（2601.06157）已有固定prompt下instruction-conditioned preference因果识别和KL信任域。后者仅完成摘要/HTML方法入口核验，尚未精读全实验/作者代码，不将其数值用于结论。Projection Heads（2605.17180）已读理论§5/实验§6，official OpenReview被challenge挡住；corpus标ICML2026，官方会场未独立核对。当前compression risk高，新颖性查询只输出定位，不自动关闭矿区。

## 2026-10-14精度审计补充
新增[PERSONA组合控制](../papers/PERSONA_ALGEBRA_2026.md)、[NCP-Bench](../papers/NCP_BENCH_2026.md)、[CitySim](../papers/CITYSIM_2025.md)、[目标形成博士研究](../papers/INTERNAL_MONOLOGUE_2025.md)及[PACT未全文核验记录](../papers/PACT_UNVERIFIED_2026.md)。人格向量组合／动态适应、长期承诺、人物—需求—计划链均已有明确ownership。E32改写稳健性是正向候选证据，整套原型识别也能解释；E33只诊断单项作者利益编辑能否保留原生控制，不称首次人格组合或新训练法。

已新增[定位卡](../papers/)：CIRL（ICML2026）覆盖goal推断的相对难度/partition，BC-PMI（ICLR2025）覆盖state-action中的style互信息与示范加权；DAIL（NeurIPS2025）覆盖语言+轨迹对比及distributional critic；PerMix-RLVR（2026预印本）覆盖persona鲁棒性/任务训练权衡；LIBERO-Para与GSR（2026预印本/作者会场声明）已覆盖等义指令对原生动作的影响和重新绑定修复。PPG（ICML2021）明确辅助表征学习加policy-KL保护；Holonomy/MultiWay已有坐标对齐/规范不变几何。各卡明示正文/附录/代码阅读范围，未全复现处保持未核对，不把邻居已有现象改名。

E25–E28不能仅凭readout、重排敏感、body混杂或正交变换建立新的NPC方法。E29只为另一原生闭环准入；下一问题必须在目标/人物/真实社会动作的新因果位置上有实测，并排除普通强提示或原作者已有memory/commitment修复。venue nearest查询已补角色目标/承诺：ACL2026 Dialogue is the Plan、Dynamic Persona Coherence、EMNLP2025 Path Drift等，需要正文审计再决定实验，不由检索自动关线。

新增方法对齐：[PAMDP／ICLR2026](../papers/PAMDP_2026.md)的隐藏profile与双critic、[GCB／ICML2022](../papers/GOAL_CONDITIONED_BISIMULATION_2022.md)的功能等价、[PA-SkewFit／NeurIPS2021](../papers/GOAL_DOMAIN_ALIGNMENT_2021.md)的matched行动与跨域表示。结合BC-PMI／DAIL，当前研究动作转为解释角色编辑的利益结构、控制方向与训练形成过程，实际读数见E37／E39，不把邻近覆盖当关闭探索的理由。

E41/I03最新定位：[PPol](../papers/PERSONA_POLICIES_2026.md)已有固定任务目标的人格交流变化与同预算训练；[Poly-PPO/ICLR2026](../papers/POLYCHROMIC_PPO_2026.md)已有集合成功×多样性、matched采样与局部分支；[SIPO/NeurIPS2023](../papers/SIPO_2023.md)已明确动作差异不等于策略后果并做游戏消融。当前增量研究动作是角色属性利益控制的形成与状态条件，不冒领这三个已有主张，也不因重叠自动关闭。三卡明确正文/附录/代码覆盖范围。

用户校正后定位：不再把“利益控制”当清楚的论文主旨。当前中心是人物设定、具体请求／自身目标／社会关系与真实选择的关系；PCSP的手写奖励诊断不能独立包装新题。新增[CRPO/ICML2026](../papers/CRPO_2026.md)、[HAMLET/ICLR2026](../papers/HAMLET_2026.md)、[CoSER/ICML2025](../papers/COSER_2025.md)正文及关键附录核对：已有角色约束与迎合冲突、task/style分流、私有goal与公共剧情冲突、动机信息对表现的因果对照。E44的一句时钟／已有责任只是普通强基线；寻找能解释真实NPC选择的新认识，而非将这些命题改名。

E46–49定位补充：[UGST/TACL2026](../papers/UGST_TACL_2026.md)已有profile/policy与任务分解、逐轮goal-state提示、SFT/GRPO；[Goal-Directedness/ICML2026](../papers/GOAL_DIRECTEDNESS_ICML_2026.md)已有behavior/belief/plan分层及因果patch对照。承诺→显式agenda、已有计划冗余及具体世界动作是当前测量层次，不能仅凭不同环境或普通管线消融称新贡献。E48单case支持一个渠道，E49以其他源角色／全部既有历史检验；尚未建立可跨角色／场景的新科学规律。
