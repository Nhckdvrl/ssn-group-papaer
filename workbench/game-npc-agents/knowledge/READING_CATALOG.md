# Game NPC Agent 阅读总账与覆盖欠账

更新：2026-10-19。总账现在包含**两批138项独立工作记录**：2026-10-18广域扩展96项，2026-10-19四兴趣矿区新增42项。新批次包含38项论文/理论文章/作者稿、1项demo与设计短稿合并记录、2篇技术报告、1个完整书章；不能统称42篇正式顶会长文。正文、附录、版本及发表身份逐项分开。

原批次95篇论文正文＋1个完整作者改写研究章的范围原样保留；两批共14张已有卡维护、124张新规范卡。42项与已计数96/31项按身份去重，但有旧库已提及或选读的题名：例如CoG开放对话补正式短文，旧库已读同家族学位论文；ACL互动戏剧补正式全文，旧库已有预印本选读。因此不称42项此前全库完全未知研究。

**类型口径：** 旧96项的`source_kind`原样保留，其中旧`paper`标签也包含FAtiMA Modular等书章作者稿；全账类型总数沿用历史标签，不冒称已统一重分类所有出版物。本批42项的38＋1＋2＋1是明确分开的新批次来源口径。条目数量不等于相互独立的实验、作者或玩家样本数。

更早31项含定向选读、技术文等不同范围，继续见[前轮登记](FIELD_REVIEW_2026-10-18.md#reading-register)，不简单相加成169篇全文。四兴趣方向的综合判断和矿区入口见[B–E总图](../MINES.md)。

## 怎样理解阅读记录

- **完整正文**：读了引言、方法、任务／证据、分析和局限等研究正文；每项明确实际版本与附录范围。不是全部参考文献、长提示、视频、图像、代码和数据均已检查。
- **作者改写章**：同伴研究PA23完整读第一作者博士论文第7章，未取得CHI PLAY2018正式PDF；只算一个研究，也不称整本博士论文已读。
- **主源身份**：正式发表、作者自报接收、预印本和不同PDF版本分开；会议模板、搜索标题、再入库日期不作接收／新论文证据。
- **证据与解释**：作者方法／设置／结果（DOCUMENTED）与本库近邻比较、跨论文推论、待检验问题分开。未报告的人数、成本、评审分数不补猜。
- **文件核验**：原96份主要实读文件及新批次可取得的PDF/PS/HTML原件分别登记SHA-256；作者网页全文无完整本地原件时明确没有PDF哈希。哈希只说明来源文件一致，不证明阅读质量。完整机器记录见[READING_CATALOG.json](READING_CATALOG.json)，每篇正文事实保存在唯一规范卡。

两批通过综述追索、经典引用链、近年正式论文集和作者预印本相互校对；没有全会议库筛选分母或系统偏倚分析，因此不是PRISMA式穷尽综述。以下分组只用于导航，不是互斥学科或研究投入优先级。

## 2026-10-18广域批次：六篇综述怎样互补

| 综述 | 适合提供的结构 | 覆盖限制 |
|---|---|---|
| [The Oscars of AI Theater](../../../library/themes/game-npc-social/papers/OSCARS_SURVEY_2025.md) | 角色数据、模型、agent与评价 | 角色扮演视角，非整个游戏控制与体验领域 |
| [RPA Evaluation Survey](../../../library/themes/game-npc-social/papers/RPA_EVALUATION_SURVEY_2025.md) | 模拟属性×下游任务；122篇纳入研究 | 明确排除有限／预定义动作任务，不能照搬为NPC全景 |
| [Two Tales of Persona](../../../library/themes/game-npc-social/papers/TWO_TALES_PERSONA_2024.md) | 模型角色与用户个性化两轴 | 广义应用综述，无统一游戏实证 |
| [Albrecht–Stone](../../../library/themes/game-npc-social/papers/ALBRECHT_STONE_2018_SURVEY.md) | 他者建模的假设、模型类型、信息和目标 | 2018方法综述；不能把当时开放问题直接称2026仍未解决 |
| [NPC合作设计综述](../../../library/themes/game-npc-social/papers/NPC_COOPERATION_REVIEW2022.md) | 174篇文献的回应性、外观、沟通、情感、行为和团队设计 | 检索截止2021、单库主题综合，非2026全景或效果量元分析 |
| [Riedl–Bulitko互动叙事](../../../library/themes/game-npc-social/papers/RIEDL_BULITKO_2013.md) | 作者意图、人物自治、玩家模型 | 经典概念谱系，非近期模型排名或统一玩家比较 |

前轮Gallotta、Hu与AI-Native Games三项综述继续由[原综合](FIELD_REVIEW_2026-10-18.md#surveys)维护范围；综述引用的论文没有因此全部变成已读。

<a id="role-evaluation"></a>
## 角色、评价、行动接口与安全：24篇正文

范围栏为导航性缩写，完整原句、附录边界和版本在规范卡及JSON中保留。

| ID | 独立研究与规范卡 | 出版／实读版本 | 阅读范围摘要 |
|---|---|---|---|
| `R01` | [The Oscars of AI Theater: A Survey on Role-Playing with Language Models](../../../library/themes/game-npc-social/papers/OSCARS_SURVEY_2025.md) | arXiv:2407.11484v9, 2025-01-10 | 完整正文 pp.1–22（§1–8），表1与图1–7；参考文献 pp.22–29仅用于追溯，不宣称逐项原文阅读。 |
| `R02` | [Towards a Design Guideline for RPA Evaluation: A Survey of Large Language Model-Based Role-Playing Agents](../../../library/themes/game-npc-social/papers/RPA_EVALUATION_SURVEY_2025.md) | arXiv:2502.13012v3, 2025-03-27 | 完整正文 pp.1–10（§1–8、limitations）；附录A–D pp.17–18（纳排标准、检索式和案例）；附录E指标词典尚未逐项阅读。 |
| `R03` | [Two Tales of Persona in LLMs: A Survey of Role-Playing and Personalization](../../../library/themes/game-npc-social/papers/TWO_TALES_PERSONA_2024.md) | arXiv:2406.01171v3, 2024-10-05; EMNLP 2024 Findings | 完整正文 pp.1–9（§1–7、limitations）；附录数据集表未逐项精读。 |
| `R04` | [RoleLLM: Benchmarking, Eliciting, and Enhancing Role-Playing Abilities of Large Language Models](../../../library/themes/game-npc-social/papers/ROLELLM_2024.md) | ACL 2024 Findings, pp.14743–14777 | 完整正文 PDF pp.1–9（§1–6、limitations）；附录C数据清洗与E部分超参。其余附录未宣称完整读。 |
| `R05` | [Character-LLM: A Trainable Agent for Role-Playing](../../../library/themes/game-npc-social/papers/CHARACTER_LLM_2023.md) | EMNLP 2023, main.814 | 完整正文 PDF pp.1–10（§1–5、limitations）；图4与表1–3；案例附录未逐例全读。 |
| `R06` | [InCharacter: Evaluating Personality Fidelity in Role-Playing Agents through Psychological Interviews](../../../library/themes/game-npc-social/papers/INCHARACTER_2024.md) | ACL 2024 main, pp.1840–1873 | 完整正文§1–7、limitations（印刷页1840–1849）；表1–3与图1–4；附录未完整读。 |
| `R07` | [CharacterEval: A Chinese Benchmark for Role-Playing Conversational Agent Evaluation](../../../library/themes/game-npc-social/papers/CHARACTEREVAL_2024.md) | ACL 2024 main, pp.11836–11850 | 完整研究正文§1–7与limitations，PDF pp.1–9；表1–4；附录评分细则未完整读。 |
| `R08` | [Large Language Models are Superpositions of All Characters: Attaining Arbitrary Role-play via Self-Alignment](../../../library/themes/game-npc-social/papers/DITTO_2024.md) | ACL 2024 main, pp.7828–7840 | 完整正文 pp.1–10（印刷页7828–7837），表1–3与图1–5；未宣称完整附录。 |
| `R09` | [PersonaGym: Evaluating Persona Agents and LLMs](../../../library/themes/game-npc-social/papers/PERSONAGYM_2025.md) | EMNLP 2025 Findings, pp.6999–7022 | 完整正文 pp.1–9（6999–7007），表1–3、模型偏差与人评段；未完整读附录。 |
| `R10` | [CharacterBox: Evaluating the Role-Playing Capabilities of LLMs in Text-Based Virtual Worlds](../../../library/themes/game-npc-social/papers/CHARACTERBOX_2024.md) | arXiv:2412.05631v1, 2024-12-07 | 完整正文 pp.1–9、表1–4与图2–3；未完整读提示附录。 |
| `R11` | [CoSER: Coordinating LLM-Based Persona Simulation of Established Roles](papers/COSER_2025.md) | ICML 2025, PMLR 267:64822–64858 | 完整正文 pp.1–10、表1–6；未宣称37页附录全部读完。 |
| `R12` | [HER: Human-like Reasoning and Reinforcement Learning for LLM Role-playing](../../../library/themes/game-npc-social/papers/HER_2026.md) | arXiv:2601.21459v1（2026-01-29）完整正文；v4（2026-04-29）关键差异补核；ACL 2026 Findings pp.25725–25762（正式出版信息已核，正式PDF未通读） | 完整阅读v1正文 pp.1–9 与附录F/G/H pp.22–23；补核v4 §4结果、Ethics及附录F–H，确认关键比较与数据声明仍在。未宣称完整通读v4或正式版全部38页。 |
| `R13` | [Character-R1: Enhancing Role-Aware Reasoning in Role-Playing Agents via RLVR](../../../library/themes/game-npc-social/papers/CHARACTER_R1_2026.md) | arXiv:2601.04611v1, 2026-01-08 | 完整正文 pp.1–9（提取文本的额外分页符不算物理页）；附录A方法标签来源及B基准说明。 |
| `R14` | [F.A.C.U.L.: Language-Based Interaction with AI Companions in Gaming](papers/FACUL_AAAI2026.md) | arXiv:2511.13112v2, 2025-11-27；AAAI2026正式条目已核验 | 完整主文PDF pp.1–8：引言、相关工作、全部方法、实验、用户研究、结论；补充材料尚未逐项读。 |
| `R15` | [MASCOT: Multi-Agent Socio-Collaborative Companion Systems](papers/MASCOT_EMNLP2026.md) | arXiv:2601.14230v3, 2026-09-14；作者项目/主页标注EMNLP2026 Main accepted，未以ACL正式论文集条目核验 | 完整正文PDF pp.1–9（§1–5、limitations）；表1–3与人评图6；附录未完整阅读。 |
| `R16` | [AGWM: Affordance-Grounded World Models for Environments with Compositional Prerequisites](papers/AGWM_2026.md) | arXiv:2605.06841v1, 2026-05-07, preprint | 完整正文PDF pp.1–9（§1–5、limitations、表1–4）；附录未完整阅读。 |
| `R17` | [BALROG: Benchmarking Agentic LLM and VLM Reasoning On Games](../../../library/themes/game-npc-social/papers/BALROG_2025.md) | ICLR 2025 正式会议论文 | 完整正文 pp.1–10，表1–3、能力分析与开放问题；37页中的任务附录未完整读。 |
| `R18` | [VideoGameBench: Can Vision-Language Models Complete Popular Video Games?](../../../library/themes/game-npc-social/papers/VIDEOGAMEBENCH_2026.md) | arXiv:2505.18134v3, 2026-05-14；实验模型仍主要是2024–2025版本 | 完整正文 pp.1–10、表1–4，实时/Lite、检查点定义、失败模式；未完整读38页附录。 |
| `R19` | [LARP: Language-Agent Role Play for Open-World Games](../../../library/themes/game-npc-social/papers/LARP_2023.md) | arXiv:2312.17653v1, 2023-12-24 | 完整正文 pp.1–9（§1–7）；参考文献不计逐篇阅读。 |
| `R20` | [OpenCharacter: Training Customizable Role-Playing LLMs with Large-Scale Synthetic Personas](../../../library/themes/game-npc-social/papers/OPENCHARACTER_2025.md) | arXiv:2501.15427v2, 2025-02-18 | 完整正文 pp.1–12、表1–5及全部主要数据消融；参考文献未逐项阅读。 |
| `R21` | [RPGBench: Evaluating Large Language Models as Role-Playing Game Engines](../../../library/themes/game-npc-social/papers/RPGBENCH_2025.md) | arXiv:2502.00595v1, 2025-02-01；未核实正式接收 | 完整正文 pp.1–9、表1–7与BFS伪码；未完整读24页附录。 |
| `R22` | [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](../../../library/themes/game-npc-social/papers/AGENTDOJO_2024.md) | NeurIPS 2024 Datasets and Benchmarks；arXiv:2406.13352v3, 2024-11-24 | 完整正文 pp.1–10；框架、4域、攻击/防御/效用定义；未逐页读攻击模板附录。 |
| `R23` | [Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents](../../../library/themes/game-npc-social/papers/ASB_2025.md) | ICLR 2025；arXiv:2410.02644v4, 2025-05-30 | 完整正文 pp.1–10、表1–8；未逐页读攻击操作附录。 |
| `R24` | [Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?](../../../library/themes/game-npc-social/papers/AGENT_FIREWALLS_2026.md) | arXiv:2510.05244v2, 2026-03-23 | 完整正文 pp.1–11、表1–6、基准审计与自适应攻击；未完整读39页附录及未独立复现代码。 |

<a id="learning-control"></a>
## 学习、控制、合作与难度：24篇正文

范围栏为导航性缩写，完整原句、附录边界和版本在规范卡及JSON中保留。

| ID | 独立研究与规范卡 | 出版／实读版本 | 阅读范围摘要 |
|---|---|---|---|
| `albrecht_stone_2018_survey` | [Autonomous Agents Modelling Other Agents: A Comprehensive Survey and Open Problems](../../../library/themes/game-npc-social/papers/ALBRECHT_STONE_2018_SURVEY.md) | Artificial Intelligence 258:66–95 | Abstract and complete main text §§1–6, Appendix A, PDF pages 1–37; references not individually followed; Tables 2–9 captions/assumption axes read; tex…（完整范围见卡） |
| `carroll_2019_human_aware` | [On the Utility of Learning about Humans for Human-AI Coordination](../../../library/themes/game-npc-social/papers/CARROLL_2019_HUMAN_AWARE.md) | NeurIPS 2019 | Complete main text sections 1-8, PDF pages 1-9; Appendix A, F-H; end of Appendix E, PDF pages 13,17-19 |
| `hu_2020_other_play` | [“Other-Play” for Zero-Shot Coordination](../../../library/themes/game-npc-social/papers/HU_2020_OTHER_PLAY.md) | ICML 2020; PMLR 119:4399-4410 | Complete main text sections 1-8, PDF pages 1-9; negative-results appendix not systematically read |
| `strouse_2021_fcp` | [Collaborating with Humans without Human Data](../../../library/themes/game-npc-social/papers/STROUSE_2021_FCP.md) | NeurIPS 2021 | Complete main text sections 1-6, discussion, impact and conclusion, PDF pages 1-10; Separate appendices referenced by paper not present in retrieved o…（完整范围见卡） |
| `zhao_2023_mep` | [Maximum Entropy Population-Based Training for Zero-Shot Human-AI Coordination](../../../library/themes/game-npc-social/papers/ZHAO_2023_MEP.md) | AAAI 2023, 37(5):6145-6153 | Complete official main text PDF pages 1-7; arXiv Appendix C end and D, pages 16-17 |
| `yu_2023_hsp` | [Learning Zero-Shot Cooperation with Humans, Assuming Humans Are Biased](../../../library/themes/game-npc-social/papers/YU_2023_HSP.md) | ICLR 2023 | Complete main text sections 1-7, PDF pages 1-9; Appendix D.1-D.3, E.2, F.2-F.4 and Tables 5,6,19,24; pages 20,21,23,26-28,31; Not all proofs or event …（完整范围见卡） |
| `cec_2025` | [Cross-environment Cooperation Enables Zero-shot Multi-agent Coordination](../../../library/themes/game-npc-social/papers/CEC_2025.md) | ICML 2025, PMLR 267:27198–27220 | Complete main text §§1–7, PDF pages 1–9; Appendix A.1–A.3 and start A.4, pages 14–15; page 19 hyperparameters, limitations and start qualitative analy…（完整范围见卡） |
| `wang_2026_coot` | [CooT: Learning to Coordinate In-Context with Coordination Transformers](../../../library/themes/game-npc-social/papers/WANG_2026_COOT.md) | ICML 2026, PMLR 306:125587–125625; official proceedings identity verified | Complete main text §§1–6, PDF pp.1–9; all main quantitative tables and adaptation results; Appendices A–C pp.14–25; human study D.1–D.3 and coding tab…（完整范围见卡） |
| `jing_2026_icrl4aht` | [Benchmarking the Limits of In-Context Reinforcement Learning for Ad-Hoc Teamwork](../../../library/themes/game-npc-social/papers/JING_2026_ICRL4AHT.md) | ICML 2026, PMLR 306:54278–54319; official proceedings identity verified | Complete main text §§1–6, PDF pp.1–9; Tables 1–7 and all main diagnostic figures; Appendices A–B and C.1–C.2 pp.15–26: environments, teammate families…（完整范围见卡） |
| `peng_2018_deepmimic` | [DeepMimic: Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills](../../../library/themes/game-npc-social/papers/PENG_2018_DEEPMIMIC.md) | ACM TOG 37(4), Article 143 / SIGGRAPH 2018 | Complete main text §§1–11, PDF pages 1–13; tables 1–6 and ablations; supplemental pages 15–18 and videos not read/viewed; Critical evidence table visu…（完整范围见卡） |
| `peng_2021_amp` | [AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control](../../../library/themes/game-npc-social/papers/PENG_2021_AMP.md) | ACM TOG 40(4), Article 144 / SIGGRAPH 2021 | Complete main text §§1–9, PDF pages 1–13; tables 1–3 and ablations; appendices and videos not fully read/viewed; Critical evidence table visually veri…（完整范围见卡） |
| `peng_2022_ase` | [ASE: Large-Scale Reusable Adversarial Skill Embeddings for Physically Simulated Characters](../../../library/themes/game-npc-social/papers/PENG_2022_ASE.md) | ACM TOG 41(4), Article 94 / SIGGRAPH 2022 | Complete main text §§1–11, PDF pages 1–14; task definitions, table 1, coverage and recovery metrics; appendix hyperparameters and videos not read/view…（完整范围见卡） |
| `baker_2022_vpt` | [Video PreTraining (VPT): Learning to Act by Watching Unlabeled Online Videos](../../../library/themes/game-npc-social/papers/BAKER_2022_VPT.md) | NeurIPS 2022 | Complete main text §§1–5, PDF pages 1–10; separate Appendices A–I and videos not read/viewed |
| `sima_2024` | [Scaling Instructable Agents Across Many Simulated Worlds](../../../library/themes/game-npc-social/papers/SIMA_2024.md) | Technical report / arXiv; formal venue not verified | Complete main text §§1–5, PDF pages 1–21; references and contributor statements excluded; videos not viewed |
| `sima2_2025` | [SIMA 2: A Generalist Embodied Agent for Virtual Worlds](../../../library/themes/game-npc-social/papers/SIMA2_2025.md) | Technical report / research preview; formal venue not verified | Complete main text §§1–5, PDF pages 1–27; complete Appendices A–C, pages 37–40; Figures 6 and 10, Table 1 visually verified on rendered pages 14, 16 a…（完整范围见卡） |
| `multigail_2023` | [Generating Personas for Games with Multimodal Adversarial Imitation Learning](../../../library/themes/game-npc-social/papers/MULTIGAIL_2023.md) | IEEE Conference on Games (CoG) 2023; EA author publication page verified | Complete main text I–VI, PDF pages 1–8; Algorithm 1, Tables I–IV; internal alpha-label inconsistencies noted; prior knowledge base had brief mention o…（完整范围见卡） |
| `spronck_2006_dynamic_scripting` | [Adaptive Game AI with Dynamic Scripting](../../../library/themes/game-npc-social/papers/SPRONCK_2006_DYNAMIC_SCRIPTING.md) | Machine Learning 63(3):217–248, 2006; institutional record verified | Complete main text §§1–7, PDF pages 1–40 and ending sentence page 41; algorithms 1–2, tables I–VI |
| `leibo_2021_meltingpot` | [Scalable Evaluation of Multi-Agent Reinforcement Learning with Melting Pot](../../../library/themes/game-npc-social/papers/LEIBO_2021_MELTINGPOT.md) | ICML 2021, PMLR 139:6187–6199; official proceedings | Complete main text §§1–9, PDF pp.1–9; all benchmark protocol, substrate descriptions, baseline setup and conclusion; Main-paper Figures 1–5 inspected …（完整范围见卡） |
| `zhang_2024_proagent` | [ProAgent: Building Proactive Cooperative Agents with Large Language Models](../../../library/themes/game-npc-social/papers/ZHANG_2024_PROAGENT.md) | AAAI 2024, 38(16):17591–17599; DOI 10.1609/aaai.v38i16.29710 | Complete main text, PDF pp.1–7, all method/evaluation/discussion/conclusion sections; Table 1 and Figures 1–4; Author supplementary pp.1–7, Appendix A…（完整范围见卡） |
| `zhang_2024_coela` | [Building Cooperative Embodied Agents Modularly with Large Language Models](../../../library/themes/game-npc-social/papers/ZHANG_2024_COELA.md) | ICLR 2024, official conference proceedings | Complete main text §§1–6, PDF pp.1–9; Tables 1–2 and Figures 1–5; Appendices A–D, pp.16–24: perception, memory, execution, environments, model trainin…（完整范围见卡） |
| `wang_2024_zsc_eval` | [ZSC-Eval: An Evaluation Toolkit and Benchmark for Multi-agent Zero-shot Coordination](../../../library/themes/game-npc-social/papers/WANG_2024_ZSC_EVAL.md) | NeurIPS 2024, Datasets and Benchmarks Track; official proceedings PDF | Complete main text §§1–6, PDF pp.1–10 (conclusion continues on p.10); Algorithm 1, Tables 1–3, Figures 1–6; Appendix C pp.19–22: evaluation count, mod…（完整范围见卡） |
| `jaderberg_2019_quake` | [Human-level performance in 3D multiplayer games with population-based reinforcement learning](../../../library/themes/game-npc-social/papers/JADERBERG_2019_QUAKE.md) | Science 364(6443):859–865, 2019-05-31; DOI 10.1126/science.aau6249 | Complete 2019 published main text, PDF pp.1–5, references/acknowledgements on p.6; DOI/title/authors/acceptance date cross-checked against UCL institu…（完整范围见卡） |
| `durst_2024_mlmove` | [Learning to Move Like Professional Counter-Strike Players](../../../library/themes/game-npc-social/papers/DURST_2024_MLMOVE.md) | Computer Graphics Forum 43(8), e15173 / SCA 2024; DOI verified | Complete main text §§1–7, PDF pages 1–11; Tables 1–3 and human evaluation; separate Supplemental Material and videos not read/viewed |
| `pfau_2020_enemy_within` | [Enemy Within: Long-term Motivation Effects of Deep Player Behavior Models for Dynamic Difficulty Adjustment](../../../library/themes/game-npc-social/papers/PFAU_2020_ENEMY_WITHIN.md) | CHI 2020, Paper 296, pages 1–10; DOI verified | Complete main text Introduction through Conclusion, PDF pages 1–8; architecture, sample sizes, Tables 1–4 and limitations |

<a id="social-narrative"></a>
## 叙事、社会、情绪与制度：25篇正文

范围栏为导航性缩写，完整原句、附录边界和版本在规范卡及JSON中保留。

| ID | 独立研究与规范卡 | 出版／实读版本 | 阅读范围摘要 |
|---|---|---|---|
| `riedl_bulitko_2013` | [Interactive Narrative: An Intelligent Systems Approach](../../../library/themes/game-npc-social/papers/RIEDL_BULITKO_2013.md) | AI Magazine 34(1):67–77 | 全文PDF pp.1–13，包括全部正文§1–4与参考文献；图示文本可读，非系统性元分析 |
| `sabre_2021` | [Sabre: A Narrative Planner Supporting Intention and Deep Theory of Mind](../../../library/themes/game-npc-social/papers/SABRE_2021.md) | AIIDE 17(1):99–106 | 全文pp.99–106；形式定义、算法1、表1、消融与局限全部阅读 |
| `cpocl_2011` | [CPOCL: A Narrative Planner Supporting Conflict](../../../library/themes/game-npc-social/papers/CPOCL_2011.md) | AIIDE 7(1):97–102 | 全文pp.97–102；定义1–19、算法1、失恋例子与限制全部阅读 |
| `glaive_2014` | [Glaive: A State-Space Narrative Planner Supporting Intentionality and Conflict](../../../library/themes/game-npc-social/papers/GLAIVE_2014.md) | AIIDE 10(1):80–86 | 全文pp.80–86；算法1、意图路径/可能世界/启发式定义与表1全部阅读 |
| `psychsim_2005` | [PsychSim: Modeling Theory of Mind with Decision-Theoretic Agents](../../../library/themes/game-npc-social/papers/PSYCHSIM_2005.md) | IJCAI 2005 | 全文6页、§1–4与表1；PDF部分公式/否定符抽取乱码，本文记录不转录这些符号或表中精确条件 |
| `ema_2009` | [EMA: A process model of appraisal dynamics](../../../library/themes/game-npc-social/papers/EMA_2009.md) | Cognitive Systems Research 10(1):70–90 | 全文28页；正文§1–5、全部认知算子/情绪/应对规则表、鸟事件逐时刻案例与局限 |
| `fatima_modular_2014` | [FAtiMA Modular: Towards an Agent Architecture with a Generic Appraisal Framework](../../../library/themes/game-npc-social/papers/FATIMA_MODULAR_2014.md) | Emotion Modeling, LNCS 8750:44–56 | 公开作者稿完整12页；§1–6、伪代码和OCC对应表；p8 Figure ??、p10未完成文字使正式版差异仍待核 |
| `dodm_2006` | [Declarative Optimization-Based Drama Management in Interactive Fiction](../../../library/themes/game-npc-social/papers/DODM_2006.md) | IEEE Computer Graphics and Applications 26(3),正式书目32–41 | 全文10页；29剧情点图、30管理动作、7特征、全部实验图与表1、局限 |
| `citysim_2025` | [CitySim: Modeling Urban Behaviors and City Dynamics with Large-Scale LLM-Driven Agent Simulation](papers/CITYSIM_2025.md) | EMNLP 2025 Industry:215–229 | 全文15页；正文§1–7、App A–D全部，配置/表1–5/评价与负例齐读 |
| `talk_of_town_2015` | [Toward Characters Who Observe, Tell, Misremember, and Lie](../../../library/themes/game-npc-social/papers/TALK_OF_TOWN_2015.md) | AIIDE Experimental AI in Games Workshop, WS-15-21:56–62 | 全文7页；知识类型、证据强度/来源/修订机制、实现状态与相关工作 |
| `panda_2025` | [Persona Dynamics: Unveiling the Impact of Personality Traits on Agents in Text-Based Games](papers/PERSONA_DYNAMICS_ACL2025.md) | ACL 2025 Main, 31360–31394 | 完整正文 pp.1–10；附录 A–D 的数据/训练/统计/人类轨迹协议 pp.13–16、E–F pp.22；全25游戏结果及旧基线 Table 14/15/18、全部GPT-4提示 Table 21 pp.28–29；其余图例附录仅定位未逐页通读 |
| `govsim_2024` | [Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents](../../../library/themes/game-npc-social/papers/GOVSIM_2024.md) | Advances in Neural Information Processing Systems 37, NeurIPS 2024 Main Conference | 完整正文 pp.1–10；完整机制/提示/运行协议与主消融附录 B–E pp.16–32；全部子技能定义/提示 pp.32–35；附录曲线与会务checklist未逐项读 |
| `norms_2025` | [Emergent social conventions and collective bias in LLM populations](../../../library/themes/game-npc-social/papers/NORMS_2025.md) | Science Advances 11(20), eadu9368 | 全部正文与Materials and Methods，PDF pp.2–9（期刊 pp.1–8）；引用与代码/数据声明 pp.10–11；另册Supplementary Text和S图表未取得，不宣称读过 |
| `concordia_2023` | [Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia](../../../library/themes/game-npc-social/papers/CONCORDIA_2023.md) | arXiv preprint; no archival venue verified | 完整正文 pp.1–23及全部实现附录 A pp.23–26；参考文献仅按相关条目核读，不等同代码审计 |
| `agentsociety_2025` | [A Parallelized Framework for Simulating Large-Scale LLM Agents with Realistic Environments and Interactions](../../../library/themes/game-npc-social/papers/AGENTSOCIETY_2025.md) | ACL 2025 Industry Track, 1339–1349 | 全部11页正文、表1–2及实现/替代模拟提示/指标附录 A–B |
| `sotopia_2024` | [SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents](../../../library/themes/game-npc-social/papers/SOTOPIA_2024.md) | ICLR 2024 | 完整正文 pp.1–9；任务与评价全部文字协议/人类招募和校准附录 A–G pp.18–31；界面截图仅按正文所述查看，长对话例库 pp.33–45未逐篇通读 |
| `sotopia_pi_2024` | [SOTOPIA-π: Interactive Learning of Socially Intelligent Language Agents](../../../library/themes/game-npc-social/papers/SOTOPIA_PI_2024.md) | ACL 2024 Main, 12912–12940 | 完整正文 pp.1–9；完整数值/训练采样/筛选/版本/检查点协议 A–B pp.13–17；人类评价C全文（图版除外）pp.17–23；D–G额外案例与MMLU逐学科图未通读 |
| `sociodrama_2026` | [Agent Sociodrama: Social-Dynamics-Guided Persona Recasting for LLM Agent Teams](papers/AGENT_SOCIODRAMA_2026.md) | arXiv preprint; no peer-reviewed venue verified | 完整正文 pp.1–10；限制、状态更新、指标、任务、recasting算法及完整逐轮/消融/人类协议附录 A–G pp.14–18；p.19全数值表核读，后续图版未逐张分析 |
| `hamlet_2026` | [HAMLET: A Hierarchical and Adaptive Multi-Agent Framework for Live Embodied Theatrics](papers/HAMLET_2026.md) | ICLR 2026（OpenReview会议PDF及官方proceedings索引确认） | 完整正文第1–11页；附录A–B第14页、C–J第16–31页完整机制、标注、训练、延迟与提示；第15页文学清单未逐条核、第32页贡献说明未细读 |
| `ncp_2026` | [Can LLM Agents Stick to the Script? A Benchmark for Long-Horizon Consistency in Interactive Narratives](papers/NCP_2026.md) | ICML 2026，PMLR 306:85171–85192（官方会议页核实） | 完整正文第1–10页及附录A–H第13–22页；第15页图表字形乱码，其统计已以表6正文核对；参考文献未逐项阅读 |
| `cdt_2026` | [Deriving Character Logic from Storyline as Codified Decision Trees](papers/CDT_2026.md) | ACL 2026 Main，12480–12509（ACL Anthology正式PDF） | 完整正文第1–10页；附录A–E第13–17页全部实验与成本、F第18页机制解释、G第24–26页全部提示；第19–22页长人物展示与27–30背景表未逐项完整阅读 |
| `dynamic_persona_2026` | [Beyond Static Persona Consistency: Dynamic Persona Coherence in LLM Role-Playing](papers/DYNAMIC_PERSONA_COHERENCE_2026.md) | ACL 2026 Main，28942–28956（ACL Anthology正式PDF） | 完整正文第1–8页及附录A–F第10–15页；包含全部人物、状态、评分、基线、完整结果与跨评判器/语言/超参协议；参考文献选择性核对 |
| `mmoagent_2025` | [Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling](papers/MMOAGENT_KDD2025.md) | KDD 2025 Research Track，3366–3377（官方KDD清单及ACM DOI检索核实） | 完整正文第1–9页；附录A–E第11–12页全部资源/行动/参数/真人数据与评判协议；参考文献未逐篇查证 |
| `vox_deorum_2025` | [Vox Deorum: A Hybrid LLM Architecture for 4X / Grand Strategy Game AI -- Lessons from Civilization V](papers/VOX_DEORUM_2025.md) | arXiv预印本；截至本轮主源仍写Under review，FDG 2026模板及占位DOI不是录用证据 | 完整正文第1–9页；附录A.1系统提示第10–11页全部，A.2状态样例首段第11页/末段第16页，B第16–17页全部输出；第12–15页长状态转储未逐行读 |
| `ai_economist_2021` | [The AI Economist: Optimal Economic Policy Design via Two-level Deep Reinforcement Learning](../../../library/themes/game-npc-social/papers/AI_ECONOMIST_2021.md) | arXiv 2021实读版本；后续Science Advances 2022论文题名不同，未取得并核完正式全文，不冒记为已读2022版 | 完整第1–31页正文与全部Methods，含税制、拍卖、奖励、训练与统计；第33页来源声明及第34页完整算法；第32–33页文献条目非独立读书目 |

<a id="player-authoring"></a>
## 玩家体验、作者工具与交互：22篇正文＋1个作者改写章

范围栏为导航性缩写，完整原句、附录边界和版本在规范卡及JSON中保留。

| ID | 独立研究与规范卡 | 出版／实读版本 | 阅读范围摘要 |
|---|---|---|---|
| `NPC-PA01` | [What do games teach us about designing effective human-AI cooperation? A systematic literature review and thematic synthesis on design patterns of non-player characters](../../../library/themes/game-npc-social/papers/NPC_COOPERATION_REVIEW2022.md) | GamiFIN 2022, CEUR Workshop Proceedings, pp.95–104 | 全文正文 §1–5、pp.95–100，Tables 1–2；参考文献浏览。不是2026新综述。 |
| `NPC-PA02` | [A Voice-Controlled Dialogue System for NPC Interaction using Large Language Models](../../../library/themes/game-npc-social/papers/VOICE_CONTROLLED2025.md) | IWSDS 2025, pp.29–38 | 全文正文 §1–8、pp.29–37；Tables 1–2 与 Figures 1–4 的文字/说明；参考文献浏览。 |
| `NPC-PA03` | [Player-Driven Emergence in LLM-Driven Game Narrative](../../../library/themes/game-npc-social/papers/PLAYER_EMERGENCE2024.md) | IEEE Conference on Games (CoG) 2024 | 全文正文 §I–VII，Tables I–IV、Figures 1–3文字；独立补充玩家日志未取得/未读。 |
| `NPC-PA04` | [A Framework for Exploring Player Perceptions of LLM-Generated Dialogue in Commercial Video Games](../../../library/themes/game-npc-social/papers/DISCO_PERCEPTIONS2023.md) | Findings of EMNLP 2023, pp.2295–2311 | 全文正文 §1–10、附录 A–G，方法、量表/界面、提示、结果统计；未运行开源界面。 |
| `NPC-PA05` | [Press A or Wave: User Expectations for NPC Interactions and Nonverbal Behaviour in Virtual Reality](../../../library/themes/game-npc-social/papers/PRESS_WAVE2024.md) | Proceedings of the ACM on Human-Computer Interaction 8, CHI PLAY, Article 333 | 全文正文 §1–7、pp.1–19、图表文字；单独47游戏明细/编码本未取得，未玩这些游戏。 |
| `NPC-PA06` | [WhatELSE: Shaping Narrative Spaces at Configurable Level of Abstraction for AI-bridged Interactive Storytelling](../../../library/themes/game-npc-social/papers/WHATELSE2025.md) | CHI 2025 | 全文正文 §1–9、Tables 1–3、Figures 1–8文字/说明；PDF没有文中提到的提示附录，外部补充未读。 |
| `NPC-PA07` | [Affective Mirroring in Video Game NPCs: A Pilot Study Evaluating Player Engagement](../../../library/themes/game-npc-social/papers/AFFECTIVE_MIRRORING2025.md) | Foundations of Digital Games (FDG) 2025 | 4页全文 §1–6、Figures 1–2文字/说明；无独立附录。 |
| `NPC-PA08` | [Presence and Engagement in an Interactive Drama](../../../library/themes/game-npc-social/papers/FACADE_PRESENCE2007.md) | CHI 2007, pp.1475–1484 | 全文正文、Table 1、图说明；参考文献浏览。未读取36小时原始录像。 |
| `NPC-PA09` | [StoryVerse: Towards Co-authoring Dynamic Plot with LLM-based Character Simulation via Narrative Planning](../../../library/themes/game-npc-social/papers/STORYVERSE2024.md) | Foundations of Digital Games (FDG) 2024 | 全文正文 §1–5、Figures 1–4、两案例；没有人评/系统实验可另行核读。 |
| `NPC-PA10` | [StoryAssembler: An Engine for Generating Dynamic Choice-Driven Narratives](../../../library/themes/game-npc-social/papers/STORYASSEMBLER2019.md) | Foundations of Digital Games (FDG) 2019 | 全文正文 §1–10、Figures 1–5文字，实际作者生产案例；参考文献浏览。 |
| `NPC-PA11` | [Towards Explainable Social Agent Authoring Tools: A case study on FAtiMA-Toolkit](../../../library/themes/game-npc-social/papers/FATIMA_EXPLAINABLE2022.md) | arXiv preprint; peer-reviewed publication not verified | 全文正文 §0.1–0.10、§1–3，全部统计表/方法；文内提到的问卷附录不在PDF，未取得。 |
| `NPC-PA12` | [FAtiMA Toolkit: Toward an Accessible Tool for the Development of Socio-emotional Agents](../../../library/themes/game-npc-social/papers/FATIMA_TOOLKIT2022.md) | ACM Transactions on Interactive Intelligent Systems 12(1), Article 8 | 约37页作者稿全文正文 §1–8及各用例，参考文献浏览；未将引用的Sueca原始研究冒称本轮全文阅读。 |
| `NPC-PA13` | [DiaryPlay: AI-Assisted Creation of Interactive Story Vignettes for Everyday Storytelling](../../../library/themes/game-npc-social/papers/DIARYPLAY2026.md) | CHI 2026 | 全文正文 §1–9、Tables 1–3、附录 A 参与者信息；外部补充提示未读。 |
| `NPC-PA14` | [Orchid-Creator: An Authoring Tool Supporting LLM-Driven Interactive Narrative Creation](../../../library/themes/game-npc-social/papers/ORCHID_CREATOR2026.md) | CHI 2026 | 全文正文 §1–10、两用户研究与六个月案例，图表统计文字；未逐像素读取箱线图，未取得原始研究数据。 |
| `NPC-PA15` | [Elsewise: Authoring Open-Ended Interactive Narrative with Possibility Space Visualization](../../../library/themes/game-npc-social/papers/ELSEWISE2026.md) | UIST 2026 listed by author; no final publisher DOI verified in this reading | 全文正文 §1–9、附录 A、图表文字、玩家模拟人设/故事主题；外部画布材料未读。 |
| `NPC-PA16` | [Conversational Interactions with NPCs in LLM-Driven Gaming: Guidelines from a Content Analysis of Player Feedback](../../../library/themes/game-npc-social/papers/VAUDEVILLE_FEEDBACK2024.md) | Chatbot Research and Design, CONVERSATIONS 2023 Revised Selected Papers, LNCS 14524, pp.167–184 | 全文正文 §1–7、Table 1全部设计建议、图文；没有对132条原始评论重新编码。 |
| `NPC-PA17` | [Let’s Talk Games: An Expert Exploration of Speech Interaction with NPCs](../../../library/themes/game-npc-social/papers/LETS_TALK2024.md) | International Journal of Human–Computer Interaction; online 2024-04-19, later vol.41(5) | 全文正文 §1–10、Tables 1–2、主题及图说明；外部问卷/编码本未读。 |
| `NPC-PA18` | [Gaming with Etiquette: Exploring Courtesy as a Game Mechanic in Speech-Based Games](../../../library/themes/game-npc-social/papers/ETIQUETTE2024.md) | International Journal of Human–Computer Interaction; online 2024-08-14, later vol.41(11) | 全文正文 §1–6、Tables 1–5、附录 A 全部 A1–A9 Holm 比较；外部OSF材料未读。 |
| `NPC-PA19` | [Dialogs with GenAI NPCs: Exploring Player Interactions with Speech Agents in a VR Game](../../../library/themes/game-npc-social/papers/DIALOGS_GENAI2026.md) | International Journal of Human–Computer Interaction; online 2026-02-02 | 全文正文 §1–8、Table 1、图表结果说明、Limitations；参考文献浏览，外部补充问卷/编码本未读。 |
| `NPC-PA20` | [How Should I Respond to “Good Morning?”: Understanding Choice in Narrative-Rich Games](../../../library/themes/game-npc-social/papers/NARRATIVE_CHOICE2022.md) | Designing Interactive Systems (DIS) 2022 | 全文正文 §1–9、Tables 1–4、图说明；参考文献浏览。摘要16游戏与方法/Table2的12游戏不一致，未与正式16页版逐行比较。 |
| `NPC-PA21` | [Personalized Quest and Dialogue Generation in Role-Playing Games: A Knowledge Graph- and Language Model-based Approach](../../../library/themes/game-npc-social/papers/PERSONALIZED_QUEST2023.md) | CHI 2023 | 全文正文 §1–8、Tables 1–11、生成示例与问卷图说明；参考文献浏览。未运行代码。 |
| `NPC-PA22` | [Ontologically Faithful Generation of Non-Player Character Dialogues](papers/KNUDGE_2024.md) | EMNLP 2024, pp.9212–9242 | 全文正文 §1–8、Limitations/Ethics、Tables 1–6；附录 A–L 方法文字、Algorithm1、Tables7–8及关键任务/人物/评价和修订提示/树样例。未逐字读全部重复长提示和所有巨大树节点，非全部附录逐图审查。 |
| `NPC-PA23` | [I’m Glad You Are on My Side: How to Design Compelling Game Companions](../../../library/themes/game-npc-social/papers/COMPANIONS_DISSERTATION2019.md) | CHI PLAY 2018, pp.141–152; study read through author dissertation adaptation | 完整第7章 §7.1–7.6、Tables10–12；不是整本博士论文全文，不冒称正式会议版逐页一致。 |

<a id="mines-2026-10-19"></a>
## 2026-10-19：四兴趣矿区的42项正文阅读

本节是新增规范记录，不与旧题名、预印本版本、附录或后续发表重复相加。B/C/D/E分组只服务阅读和矿区定位；同一工作可以被四区交叉引用。

### B · 角色表演、人物塑造与延展：12项

| ID | 规范卡 | 实际版本/发表身份 | 阅读范围 |
|---|---|---|---|
| `NPC-B01` | [ArcANE: Do Role-Playing Language Agents Stay in Character at the Right Time?](../../../library/themes/game-npc-social/papers/ARCANE_2026.md) | arXiv v2；作者自报 EMNLP 2026 Main 接收，未独立核会场条目；arXiv:2606.05553v2, 2026-09-02 | 完整正文 pp.1–10；附录 D.2–F pp.18–20、P pp.27–29；其余附录、逐条提示、数据和代码未完整读。 |
| `NPC-B02` | [RoleBreak: Character Hallucination as a Jailbreak Attack in Role-Playing Systems](../../../library/themes/game-npc-social/papers/ROLEBREAK_2025.md) | COLING 2025 Main；ACL Anthology 2025.coling-main.494, pp.7386–7402 | 完整正文与limitations，PDF pp.1–9；附录完整提示/代码未读。 |
| `NPC-B03` | [Mitigating Hallucination in Fictional Character Role-Play](../../../library/themes/game-npc-social/papers/ROLEFACT_2024.md) | Findings of EMNLP 2024；ACL Anthology 2024.findings-emnlp.846, pp.14467–14479 | 完整正文PDF pp.1–9含limitations；附录与代码未完整读。 |
| `NPC-B04` | [TimeChara: Evaluating Point-in-Time Character Hallucination of Role-Playing Large Language Models](../../../library/themes/game-npc-social/papers/TIMECHARA_2024.md) | Findings of ACL 2024；ACL Anthology 2024.findings-acl.197, pp.3291–3325 | 完整正文 pp.1–10；附录pp.30–31全量评价说明、H.1人工复核、算法；其余附录未完整读。 |
| `NPC-B05` | [PsyMem: Fine-grained Psychological Alignment and Explicit Memory Control for Advanced Role-Playing LLMs](../../../library/themes/game-npc-social/papers/PSYMEM_2026.md) | TACL 2026；ACL 2026.tacl-1.24；TACL 14:510–529；正式PDF页脚April2026 | 完整正文pp.1–11；附录B–E主要方法、人工标注、稳健性pp.18–20；完整提示和代码未逐项读。 |
| `NPC-B06` | [Memory-Driven Role-Playing: Evaluation and Enhancement of Persona Knowledge Utilization in LLMs](../../../library/themes/game-npc-social/papers/MEMORY_DRIVEN_ROLEPLAY_2026.md) | Findings of ACL 2026；ACL 2026.findings-acl.1175, pp.23475–23510 | 完整正文pp.1–9；附录A人物/片段统计、C.3/E构造、K–N评委校准/关联/预算（印刷23487–23489、23494–23496）；其余长提示示例代码未全读。 |
| `NPC-B07` | [Thinking in Character: Advancing Role-playing Agents with Role-Aware Reasoning](../../../library/themes/game-npc-social/papers/THINKING_IN_CHARACTER_2025.md) | NeurIPS 2025；NeurIPS 2025 official conference PDF | 完整正文pp.1–10；附录B–E pp.14–17；其余提示、案例、checklist和代码未全读。 |
| `NPC-B08` | [Crafting Customisable Characters with LLMs: A Persona-Driven Role-Playing Agent Framework](../../../library/themes/game-npc-social/papers/SIMSCONV_2025.md) | Findings of EMNLP 2025；ACL 2025.findings-emnlp.1100, pp.20216–20240 | 完整正文pp.1–9含limitations；附录A/C pp.11–12；其余完整提示/数据代码未全读。 |
| `NPC-B09` | [Crab: A Novel Configurable Role-Playing LLM with Assessing Benchmark](../../../library/themes/game-npc-social/papers/CRAB_2025.md) | ACL 2025 Main；ACL 2025.acl-long.731, pp.15030–15052 | 完整正文pp.1–9；附录7.1–7.9方法/标注/未见角色/训练统计，pp.10–14相关段落；p.19表14角色提示。长案例和其余提示未全读，图表全数值未逐项视觉复核。 |
| `NPC-B10` | [ORIBA: Exploring LLM-Driven Role-Play Chatbot as a Creativity Support Tool for Original Character Artists](../../../library/themes/game-npc-social/papers/ORIBA_2025.md) | arXiv preprint；ACM投稿排版，接收身份未核；arXiv:2512.12630v1, 2025-12-14 | 完整正文pp.1–20；A.1/A.2/A.4文字pp.25–26、28；图像式问卷p.27及全部作品视觉未读，参考文献未逐项追溯。 |
| `NPC-B11` | [The Role of Emotion in Believable Agents](../../../library/themes/game-npc-social/papers/BATES_BELIEVABLE_EMOTION_1994.md) | CMU technical report；另有CACM版本未逐字比对；CMU-CS-94-136, April 1994, author PostScript | 作者技术报告9页全部读取，正文印刷1–6、参考文献7与前置页；PS本地转换PDF。CACM正式4页版本未比对。 |
| `NPC-B12` | [An Oz-Centric Review of Interactive Drama and Believable Agents](../../../library/themes/game-npc-social/papers/OZ_CENTRIC_REVIEW_1997.md) | CMU technical report；CMU-CS-97-156, June 1997, author HTML | HTML全部正文Introduction至Conclusion逐段阅读（本地1370行纯文本）；图像式架构图未视觉核查，外链注释书目未逐项追溯。 |

### C · 共同叙事、作者意图与玩家参与：12项

| ID | 规范卡 | 实际版本/发表身份 | 阅读范围 |
|---|---|---|---|
| `NPC-C01` | [Narrative Planning: Balancing Plot and Character（JAIR 2010）](../../../library/themes/game-npc-social/papers/IPOCL_2010.md) | JAIR 39; DOI 10.1613/jair.2989；author-hosted 51-page PDF; formal 2010; 2014 arXiv redeposit excluded | 全文正文 pp.1–37，附录 A.1–A.3 pp.38–47；视觉核对 p.35、pp.42–45；参考文献浏览 |
| `NPC-C02` | [Agency Reconsidered（DiGRA 2009）](../../../library/themes/game-npc-social/papers/AGENCY_RECONSIDERED_2009.md) | DiGRA 2009; DOI 10.26503/dl.v2009i1.369；author-institution archived 9-page PDF | 全部9页理论、案例、结论及参考文献 |
| `NPC-C03` | [Achieving the Illusion of Agency（ICIDS 2012）](../../../library/themes/game-npc-social/papers/ILLUSION_OF_AGENCY_2012.md) | ICIDS 2012, pp.114–125; DOI 10.1007/978-3-642-34851-8_11；author-hosted 12-page published-layout PDF | 全部12页，含三阶段招募、筛选、逐题分析及局限 |
| `NPC-C04` | [Foreseeing Meaningful Choices（AIIDE 2014）](../../../library/themes/game-npc-social/papers/FORESEEING_MEANINGFUL_CHOICES_2014.md) | AIIDE 10(1):9–15; DOI 10.1609/aiide.v10i1.12716；official 7-page PDF | 全部7页；视觉核对 pp.4–5 表3–6与图2 |
| `NPC-C05` | [A Coauthorship-Centric History of Interactive Emergent Narrative（ICIDS 2021）](../../../library/themes/game-npc-social/papers/COAUTHORSHIP_EMERGENT_NARRATIVE_2021.md) | ICIDS 2021, LNCS13138, pp.222–235；author-hosted 14-page PDF | 全部14页理论史、案例、结论及参考文献 |
| `NPC-C06` | [Drama Llama: An LLM-Powered Storylets Framework for Authorable Responsiveness in Interactive Narrative（2025 预印本）](../../../library/themes/game-npc-social/papers/DRAMA_LLAMA_2025.md) | arXiv preprint 2501.09099; formal venue unverified；arXiv2501.09099v1, 2025-01-15, 10 pages | 全文§I–VIII；附录A–C全部提示；附录D图和p.5界面/表II视觉读取 |
| `NPC-C07` | [Dramamancer: Interactive Narratives with LLM-powered Storylets（UIST Adjunct 2025，Demo）](../../../library/themes/game-npc-social/papers/DRAMAMANCER_2025.md) | UIST Adjunct 2025 Demo; DOI 10.1145/3746058.3758995; Wordplay2025 design short paper；5-page formal demo + 3-page Wordplay2025 design paper; 2026 arXiv identical text redeposit | 完整demo全部正文/图注及pp.2–4界面视觉；完整三页设计短稿；逐行核2026再存只多水印 |
| `NPC-C08` | [Towards Enhanced Immersion and Agency for LLM-based Interactive Drama（ACL 2025 Main）](../../../library/themes/game-npc-social/papers/IMMERSION_AGENCY_DRAMA_2025.md) | ACL 2025 Main Long, pp.11166–11182; 2025.acl-long.546；17-page ACL version of record; checked arXiv2502.17878v2 2025-06-03 | 正文pp.1–9，附录A–D pp.12–17完整提示/剧本/模拟玩家；p.8关键表视觉；参考文献浏览 |
| `NPC-C09` | [Language Models as Narrative Planning Heuristics（FDG 2025）](../../../library/themes/game-npc-social/papers/LM_NARRATIVE_HEURISTICS_2025.md) | FDG 2025 article31; DOI 10.1145/3723498.3723815；author-hosted 9-page published-layout PDF | 完整9页正文/表/算法/图注；p.6表2–4视觉；未逐点重建曲线 |
| `NPC-C10` | [Gameplay as On-Line Mediation Search（AIIDE Workshop 2014）](../../../library/themes/game-npc-social/papers/GAMEPLAY_MEDIATION_2014.md) | AIIDE Workshop Experimental AI in Games 2014,42–48; DOI 10.1609/aiide.v10i3.12740；official 7-page workshop PDF; later archive timestamp not publication year | 完整7页正文、伪代码、图注和案例；未逐图重建搜索树 |
| `NPC-C11` | [Narrative Planning Using LLMs as a Model of Action Believability（Halberd，2026 作者稿）](../../../library/themes/game-npc-social/papers/HALBERD_2026.md) | AIIDE 2026 forthcoming per author lab; formal proceedings not yet verified；11-page author manuscript; outdated 2024 copyright template | 全部正文/算法/实验/局限及参考文献；pp.7–9表1–6视觉核查 |
| `NPC-C12` | [Bonsai: Cultivating Author Intent in LLM-Based Interactive Digital Narratives（ICML 2026 Workshop）](../../../library/themes/game-npc-social/papers/BONSAI_2026.md) | ICML2026 Workshop on Human-AI Co-Creativity; not ICML main；workshop-hosted 16-page manuscript, no version identifier on source | 正文§1–6 pp.1–6及附录A–L pp.9–16全部；参考文献浏览；pp.6/9/13/14/15表视觉 |

### D · 情绪、关系与玩家情感：10项

| ID | 规范卡 | 实际版本/发表身份 | 阅读范围 |
|---|---|---|---|
| `NPC-D01` | [Establishing and Maintaining Long-Term Human-Computer Relationships](../../../library/themes/game-npc-social/papers/RELATIONAL_AGENTS_2005.md) | ACM TOCHI 12(2):293–327；44-page author manuscript linked from author publication list; PDF creation 2004-03-24; formal article 2005 | 完整作者稿正文PDF pp.1–40；参考文献选择性追索；未读的另一个50页早稿不重复计数 |
| `NPC-D02` | [Simulation of the Dynamics of Nonplayer Characters’ Emotions and Social Relations in Games](../../../library/themes/game-npc-social/papers/OSSE_SOCIOEMOTION_2009.md) | IEEE TCIAIG 1(4):281–297；27-page author manuscript, metadata 2009-11-02; journal issue December 2009; author list sorts into 2010 | 27页作者稿pp.1–24完整正文；参考文献选择性读；不与AIIDE/ACII短版或法语版本相加 |
| `NPC-D03` | [Emotional Appraisal Engines for Games](../../../library/themes/game-npc-social/papers/APPRAISAL_ENGINES_2016.md) | Emotion in Games, Springer, pp.215–232；18-page author chapter | 18页完整书章，包括方法/四种接入示例/13名开发者先导与结论 |
| `NPC-D04` | [Spoken Conversational AI in Video Games – Emotional Dialogue Management Increases User Engagement](../../../library/themes/game-npc-social/papers/SPOKEN_EMOTION_2018.md) | IVA 2018, pp.179–184；Author Ioannis Papaioannou uploaded full article on ResearchGate 2018-10-11 | 作者上传全文HTML完整§1–7，web extraction lines67–1218逐段读；参考文献选择性；未把PDF受限写成PDF全读 |
| `NPC-D05` | [Exploring Emotional Attachment to Game Characters](../../../library/themes/game-npc-social/papers/CHARACTER_ATTACHMENT_2019.md) | CHI PLAY 2019, pp.313–324；Aalto accepted manuscript, 13 PDF pages including cover | PDF pp.2–11全部正文；旋转表p.7另用raw核读；封面p.1、参考文献12–13选择性 |
| `NPC-D06` | [“I Harbour Strong Feelings for Tali Despite Her Being a Fictional Character”: Investigating Videogame Players’ Emotional Attachments to Non-Player Characters](../../../library/themes/game-npc-social/papers/NPC_ATTACHMENT_MASS_EFFECT_2020.md) | Game Studies 20(1), February 2020；Publisher full HTML | 完整HTML主文：理论、资料来源、词汇/质性方法、分析、讨论、结论；参考文献选择性 |
| `NPC-D07` | [An appraisal-based chain-of-emotion architecture for affective language model game agents](../../../library/themes/game-npc-social/papers/CHAIN_EMOTION_2024.md) | PLOS ONE 19(5):e0301033；Formal published 2024-05-10; first preprint 2023 | 21页正式PDF pp.1–18完整正文与三项实验；参考文献选择性；独立S1附件和OSF原始数据未读/未审计 |
| `NPC-D08` | [From Triggers to Emotions: A CPM-Grounded Appraisal Multi-Agent for Dynamic Emotional Evolution in Persona-Based Dialogue](../../../library/themes/game-npc-social/papers/CPM_MULTIAGENT_2026.md) | arXiv preprint; formal acceptance not verified；arXiv2607.07824v1, 2026-07-08 | 23页完整正文、局限、伦理与附录A–H；所有提示/主表/消融/人评/模型迁移；未运行代码 |
| `NPC-D09` | [EmoLLM: Appraisal-Grounded Cognitive-Emotional Co-Reasoning in Large Language Models](../../../library/themes/game-npc-social/papers/EMOLLM_2026.md) | arXiv preprint; formal acceptance not verified；arXiv2603.16553v1, 2026-03-17 | 完整主文pp.1–9及附录A–I pp.11–20；参考文献选择性 |
| `NPC-D10` | [Too Categorical to be Human: Emotion Concepts in LLMs and Humans](../../../library/themes/game-npc-social/papers/CORE_EMOTION_CONCEPTS_2026.md) | arXiv preprint v3; an earlier version presented at WiML Workshop @ NeurIPS 2025, not NeurIPS main；arXiv2508.05880v3, 2026-10-06; v1 title Do Machines Think Emotionally? Cognitive Appraisal Analysis of Large Language Models | 105页PDF完整主文pp.1–19；关键附录pp.32–56及100–105；未声称其余附录逐项全读；旧题/版本不重复计数 |

### E · 玩家活动、交互自由与体验测量：8项

| ID | 规范卡 | 实际版本/发表身份 | 阅读范围 |
|---|---|---|---|
| `NPC-E01` | [Exploring Presence in Interactions with LLM-Driven NPCs: A Comparative Study of Speech Recognition and Dialogue Options](../../../library/themes/game-npc-social/papers/PRESENCE_VRST_2024.md) | ACM VRST 2024；institution-hosted published-layout PDF, including repository cover; DOI 10.1145/3641825.3687716 | 完整研究正文§1–7；含封面12页PDF，图5–6另视觉核对；代码、原始数据未读/未运行。 |
| `NPC-E02` | [Open-Ended NPC Dialogue Favors Casual Players: A Pilot Comparison of Three LLM-Driven Dialogue Systems](../../../library/themes/game-npc-social/papers/OPEN_ENDED_DIALOGUE_2025.md) | IEEE CoG 2025；author-uploaded full-text HTML of 4-page formal paper; DOI 10.1109/CoG64752.2025.11114150 | 作者上传HTML完整§I–VII、表I及图说明；未取得可校验PDF，未逐图视觉核对。旧库已读同家族硕士论文相关章节，本批补正式短文。 |
| `NPC-E03` | [Symbolically Scaffolded Play: Designing Role-Sensitive Prompts for Generative NPC Dialogue](../../../library/themes/game-npc-social/papers/SCAFFOLDED_PLAY_2025.md) | arXiv preprint; formal venue unverified；arXiv:2510.25820v1, 2025-10-29; 2018 template is not publication year | 20页PDF正文§1–6、表1–5、Listings1–3完整；表3–4视觉核对；外部补充/代码未完整读。 |
| `NPC-E04` | [Pharos Night: Crown Pursuit: An AI-Native Deck-Building and Tactical Arena Game Design Based on Multi-Agent Systems](../../../library/themes/game-npc-social/papers/PHAROS_NIGHT_2026.md) | arXiv preprint; formal venue unverified；arXiv:2608.12216v1, 2026-08 | 完整研究正文§1–6、机制、表1；参考文献用于追溯，未运行Unity或核原始问卷。 |
| `NPC-E05` | [Development and Validation of the Player Experience Inventory: A Scale to Measure Player Experiences at the Level of Functional and Psychosocial Consequences](../../../library/themes/game-npc-social/papers/PXI_2020.md) | International Journal of Human–Computer Studies 135:102370；49-page author manuscript dated 2019-10-20; formal journal 2020 | 完整作者稿研究正文§1–9、印刷pp.1–34、表1–11；参考文献未逐篇追读；未复算数据。 |
| `NPC-E06` | [Independent Validation of the Player Experience Inventory: Findings from a Large Set of Video Game Players](../../../library/themes/game-npc-social/papers/PXI_VALIDATION_2024.md) | ACM CHI 2024；institution-hosted 13-page formal paper; DOI 10.1145/3613904.3642270 | 完整正文§1–11、表1–8；PDF pp.7–8表4–8视觉核对；未复算OSF数据。 |
| `NPC-E07` | [“It depends on where AI is used”: Players’ attitude patterns and evaluative logics toward different AI applications in digital games](../../../library/themes/game-npc-social/papers/PLAYERS_AI_ATTITUDES_2026.md) | arXiv preprint; work in progress；arXiv:2604.27812v1, 2026-04-30 | 14页PDF完整正文§1–5及附录A–B问卷/编码本；图1–2按文本和图说明读；未重新编码。 |
| `NPC-E08` | [Playing the Imitation Game: How Perceived Generated Content Shapes Player Experience](../../../library/themes/game-npc-social/papers/IMITATION_GAME_2026.md) | ACM CHI 2026；arXiv:2602.14254v1; formal DOI 10.1145/3772318.3790473 | 21页PDF完整正文§1–6及附录A.1–A.3；表1和问卷图12视觉核对；未复算数据或运行游戏。 |

**本批补完的旧阅读债：** Spoken Conversational AI（作者完整HTML）、Presence VRST（机构PDF）、IPOCL（正文与实质附录）。具体未读附件依各卡保留；补完不把此前仅列欠账的条目重复相加。

**版本/家族排重：** Dramamancer的UIST demo和设计短稿合成一项，2026 arXiv只是2025三页稿重存；CoRE旧题/新题、Bates技术报告/CACM线索不分拆计数；CoG与FDG2026属于同家族，后续数据复用范围未核清，不另计。CoG/ACL两项在A已有家族证据，正式全文升级不改写冻结历史。

## 2026-10-18批次直接改正的知识问题

| 原记录／常见推断 | 改正后的事实与范围 |
|---|---|
| CoSER旧卡将思考消融当动机消融 | 正式Table6重新对列；CoSER8B去动机56.81，标准56.45，不能写所有模型都改善 |
| HER摘要增幅直接照抄成百分数 | 22.86→53.12为100分扣分量表上30.26分；CoSER与HER评委不同，不跨表排榜 |
| 动态人格已经排除强商业模型＋正常历史 | Vanilla没有历史响应／状态累积；普通记忆解释未排除；PCC公式与部分表格还需澄清 |
| CDT收益全部属于树遍历 | 同一规则普通提示接近CDT-Lite，Bandori差0.34个NLI分；主扮演模型8B，1B／3B为附录 |
| 安全邻域只凭摘要和旧小模型案例 | AgentDojo／ASB补正文，加入Agentic Firewalls及效用／自适应攻击；与CaMeL是不同论文 |
| 大量NPC规模等于大量同时丰富对话 | AgentSociety区分同名论文；CitySim百万规模是稀疏set/get压力，不当丰富对话吞吐 |
| KNUDGE或玩家涌现策略已经证明新引擎玩法 | 专家读文本game effect与执行不同；Dejaboom的玩家提议未必都能执行 |
| 新日期就是新模型实证 | SIMA2是2025报告；2026 VR论文实现来自2023；VideoGameBench v3不等于重测2026旗舰 |

这些纠偏不把论文或方向判为无价值。它们用于保留正确的贡献，并防止后续选题建立在过强前提上。

## 论文之后的系统资料

另完整阅读Vox Deorum当前作者README和playing、architecture、diplomacy三份文档。它们描述跨回合外交对话、反提议、撤回、提议状态、合法性检查、游戏结算与五类既有承诺的接口，明显超过2025论文所测版本。记录保存在[Vox Deorum原卡](papers/VOX_DEORUM_2025.md)的后续项目段；只作为作者技术文档所述实现，未独立运行验证可靠性或玩家收益，**不增加论文计数**。其他原卡的官方代码／数据入口及带日期的历史核查范围也已保留。

<a id="reading-debts"></a>
## 仍然欠缺的阅读与领域覆盖

数量增加不等于覆盖完成。下表包含未读新来源、同论文版本/附录，以及尚需系统追索的整条研究线；**不额外进入138项记录计数**。已补完条目移入JSON的`resolved_reading_debts`，保留原状与解决记录。

| 来源或方向 | 当前范围 | 为什么需要补 |
|---|---|---|
| [Beyond Pre-Defined Scripts: Player Perceptions on Generative NPC Dialogues](https://doi.org/10.1145/3742413.3789221) | metadata_and_abstract_only | Original ACM PDF request returned access failure; institutional metadata seen, methods/results not read. |
| [RPGAgent: Driving Coherent Story-to-Play Generation with an LLM-Based Multi-Agent System](https://doi.org/10.1145/3772318.3790326) | institutional_publication_notice_only | CHI2026身份已核，ACM全文访问403，未取得全文；不据摘要推断完整对照或人类效果。 |
| [Gathering Self-Report Data in Games Through NPC Dialogues](https://doi.org/10.1145/3411764.3445411) | metadata_and_abstract_only | Full methods, conditions and participant-level results not obtained/read. |
| [An Empirical Evaluation of AI-Powered Non-Player Characters' Perceived Realism and Performance in Virtual Reality Environments](https://arxiv.org/abs/2507.10469) | identity_verified_distinct_abstract_only_full_text_unread | 官方arXiv已核Korkiakoski等、2025-07-14v1、18人审讯场景，与Presence VRST/Dialogs IJHCI作者与场景不同；解除疑似重复，正文仍未读。 |
| 更多剧情规划、经验管理、用户模型与作者控制的经典原始系统及新综述 | coverage_gap_not_bibliographically_exhausted | 本批补IPOCL、GME、agency/共同创作理论、现代导演和编辑工具；Fabulist/Mimesis、Thespian、后续整合性综述与大量作者实践仍待系统追索。 |
| BDI、社会规范、组织/角色制度、文化差异与社会认知架构 | coverage_gap_not_bibliographically_exhausted | PsychSim/EMA/FAtiMA只覆盖部分个体心智和情绪建模；命名游戏与GovSim不代表整个规范与组织研究。需要可执行制度、例外、义务冲突及文化差异的原始研究。 |
| [FAtiMA Modular最终出版章节](https://link.springer.com/chapter/10.1007/978-3-319-12973-0_3) | final_chapter_not_read_author_draft_read | 已读12页作者稿有Figure??及未完段落，正式书目为44–56页。需比对最终版本；不能把同篇补完再计为新题名。 |
| [Emergent social conventions and collective bias in LLM populations，独立Supplementary Materials](https://doi.org/10.1126/sciadv.adu9368) | main_and_methods_read_supplement_not_read | 正文Methods已核，但详细模型提示、额外规模/历史/字母集合及稳健性图可能在独立补充材料。不能声称已穷尽全协议附件。 |
| [Reproducibility Study of Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents](https://arxiv.org/abs/2505.09289) | primary_title_and_abstract_located_not_full_read | 独立复现可检查GovSim强基线、异质群体及提示语言敏感性；本轮只确认该原始预印本存在，不能使用其摘要升级机制证据。 |
| [The AI Economist后续2022 Science Advances正式版及早期2020版本中的人类实验](https://doi.org/10.1126/sciadv.abk2607) | 2021_preprint_read_other_versions_not_full_read | 本轮34页2021稿不是正式2022版；需要核版本间实验、假设及人类验证变化，不能用论文家族名称合并证据，更不能将同论文版本算新增。 |
| [AgentSociety：另一个作者集的75页社会仿真研究（arXiv:2502.08691）](https://arxiv.org/abs/2502.08691) | identity_distinguished_not_full_read | 与本轮Jun Zhang等ACL Industry 11页并行框架不是同一论文；更广社会、制度干预与数据校准主张需要独立阅读全文。 |
| 更多游戏经济/宏观经济代理、制度学习与外部数据校准研究 | coverage_gap_not_bibliographically_exhausted | AI Economist、MMOAgent和Vox Deorum覆盖三个不同问题，仍不足以审视市场价格、异质人群、政策响应、经济预测的泛化与识别；EconAgent、MMOEconomist等应先核原始版本与身份。 |
| 商业游戏需求、关系、派系、犯罪、声誉、经济及日程系统的一手工程材料 | coverage_gap_neighbor_team_may_partially_cover | 这25项多为研究原型与邻接仿真，不能替代真实开发中的内容编写、调试、存档、可解释失败与性能约束；需对照The Sims等需求模拟与RPG派系/社会系统的一手材料。 |
| 长期关系、角色成长、情绪可信性、群体制度的真人玩家纵向研究 | coverage_gap_longitudinal_players | 本批补Bickmore非游戏30天关系研究、ORIBA作者后续创作、游戏依恋回忆材料；它们仍不等于跨会话实际NPC玩家关系/成长与留存验证。 |
| 25项中逐篇read_scope明确未读的长示例、热力图、会务清单及代码实现 | explicit_partial_supplement_scope | 本轮已读全部正文与决定性方法/评分/样本协议，但非所有PDF逐字、非代码审计、非复现实验。若后续主张依赖未读具体附件，需要先补该附件。 |
| CivRealm及学习控制线相关近邻 | delegated_neighbor_team_not_independently_full_read_here | Vox Deorum正文足以识别其抽象层区别，但性能比较应由学习控制线的CivRealm全文记录交叉核，不能据Vox单方跨论文数字宣布优越。 |
| [LLM-Based NPCs in Video Games: A Systematic Mapping Study](https://pure.etsmtl.ca/en/publications/llm-based-npcs-in-video-games-a-systematic-mapping-study/) | primary_metadata_and_abstract_only | IEEE Transactions on Games 2026 early access，DOI 10.1109/TG.2026.3733302；正式全文访问未取得。检索377／纳入42及技术比例只见摘要，不作为已读正文结论。 |
| [Improved Non-Player Character (NPC) behavior using evolutionary algorithm—A systematic review](https://doi.org/10.1016/j.entcom.2024.100875) | metadata_and_abstract_only | Entertainment Computing 52 (2025), 100875；正式全文访问未取得。 |
| [The Case for Dynamic Difficulty Adjustment in Games（Hunicke 2005）](https://doi.org/10.1145/1178477.1178573) | metadata_only_not_full_read | 经典DDA原文未完成阅读；Dynamic Scripting与Enemy Within不能代替整条难度适应谱系。 |
| 导航、感知、避障、人群、现代运动生成、完整MARL和更多DDA方法 | coverage_gap | 本轮控制／合作24篇提供代表链条，并非该方向完整综述。详见学习控制专题的缺口表。 |
| [HER正式ACL2026版与arXiv v4完整版本比对](https://aclanthology.org/2026.findings-acl.1283/) | v1_main_and_v4_critical_sections_read | 完整正文实读v1，并补v4实验、伦理及F–H；未逐页比对正式38页。补版本不重复计数。 |
| [Toward Believable Acting for Autonomous Animated Characters](https://doi.org/10.1145/3561975.3562941) | primary_abstract_only | MIG2022第一方摘要；ACM403，表演机制/评估正文未读。 |
| [Quest of Aivengarde](https://fdg2026.org/abstracts/) | formal_abstract_only_same_family_data_overlap_unverified | FDG2026会议与机构摘要确认同一项目家族、64人描述；11页正文未读，具体数据复用范围未核清，不计新增独立研究或样本。 |
| [miniPXI](https://doi.org/10.1145/3549507) | identity_only_not_full_read | 量表原文未完整读，不能把完整PXI效度直接继承给短版或自行截断题项。 |
| [Large Language Models as Narrative Planning Search Guides](https://cs.uky.edu/~sgware/reading/papers/farrell2024large.pdf) | located_not_full_read | 作者PDF已定位，IEEE ToG2024online/2025卷期；本轮未完整读，不使用细节作新证据。 |
| 情绪理论的量化综述、多模态表演与调节 | coverage_gap | 已读2016appraisal章、CoRE及经典机制；仍需coping/regulation/action readiness、混合情绪、语音身体时机及心理效度的原始/综述链。 |
| 叙事策展、choice poetics、作者负担与重复体验 | coverage_gap | 已有agency/共同创作历史与现代工具，不等于覆盖作者长期演化意图、反事实编辑、重玩与专业制作过程。 |
| 四兴趣方向的跨文化、无障碍、非亲密关系及不同玩法 | coverage_gap | 现有小样本角色/RPG材料不能代表儿童、老年、不同语言、恐怖/喜剧、对手、宠物或竞技等体验。 |

维护时先查题名、DOI／arXiv和现有规范卡，再补原卡，避免同一研究因改题名、正式发表、附录或代码更新重复计数。新事实若改变判断，直接修正相应主题段落；争议保留来源和不确定性，不以追加结论掩盖旧错误。阅读优先补薄弱方向及会改变现有认识的反证，不靠堆叠同一种小任务凑数量。
