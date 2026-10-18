# Game NPC Agent 阅读总账与覆盖欠账

更新：2026-10-18（Asia/Shanghai）。本轮按领域而非矿区选择来源，完成 **95篇论文正文＋1个完整作者改写研究章，共96项独立研究**。其中14张原有规范卡在原位置重写／加深，82张建立独立规范卡；有些新卡对应旧库曾提及的题名，因此不称82篇此前完全未知的论文。

与前轮31项定向阅读按题名、arXiv／DOI核对无重复。本页不把这两批简单相加称为127篇全文：前轮含定向选读、技术文与其他来源，其原范围保留在[前轮登记](FIELD_REVIEW_2026-10-18.md#reading-register)。旧库其余卡也没有随本轮日期自动升级。

## 怎样理解阅读记录

- **完整正文**：读了引言、方法、任务／证据、分析和局限等研究正文；每项明确实际版本与附录范围。不是全部参考文献、长提示、视频、图像、代码和数据均已检查。
- **作者改写章**：同伴研究PA23完整读第一作者博士论文第7章，未取得CHI PLAY2018正式PDF；只算一个研究，也不称整本博士论文已读。
- **主源身份**：正式发表、作者自报接收、预印本和不同PDF版本分开；会议模板、搜索标题、再入库日期不作接收／新论文证据。
- **证据与解释**：作者方法／设置／结果（DOCUMENTED）与本库近邻比较、跨论文推论、待检验问题分开。未报告的人数、成本、评审分数不补猜。
- **文件核验**：96份主要实读文件的SHA-256已核；哈希只说明来源文件一致，不证明阅读质量。完整机器记录见[READING_CATALOG.json](READING_CATALOG.json)，每篇正文事实保存在唯一规范卡。

本轮通过综述追索、经典引用链、近年正式论文集和作者预印本相互校对；没有全会议库筛选分母或系统偏倚分析，因此不是PRISMA式穷尽综述。以下分组只用于导航，不是互斥学科或研究投入优先级。

## 六篇本轮综述怎样互补

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

## 本轮直接改正的知识问题

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

数量增加不等于覆盖完成。下表包括未读新来源、同论文版本／附录，以及尚需系统追索的整条研究线；**均不额外进入95＋1计数**。其他旧摘要／项目来源还在相应专题页明确标注。

| 来源或方向 | 当前范围 | 为什么需要补 |
|---|---|---|
| [Beyond Pre-Defined Scripts: Player Perceptions on Generative NPC Dialogues](https://doi.org/10.1145/3742413.3789221) | metadata_and_abstract_only | Original ACM PDF request returned access failure; institutional metadata seen, methods/results not read. |
| [RPGAgent](https://doi.org/10.1145/3772318.3790326) | institutional_publication_notice_only | No full paper obtained; acronym title not expanded from memory. |
| [Gathering Self-Report Data in Games Through NPC Dialogues](https://doi.org/10.1145/3411764.3445411) | metadata_and_abstract_only | Full methods, conditions and participant-level results not obtained/read. |
| [Spoken Conversational AI in Video Games – Emotional Dialogue Management Increases User Engagement](https://doi.org/10.1145/3267851.3267896) | institutional_abstract_only | Original ACM PDF access failed; do not treat title as verified empirical conclusion. |
| [Exploring Presence in Interactions with LLM-Driven NPCs: A Comparative Study of Speech Recognition and Dialogue Options](https://vbn.aau.dk/ws/portalfiles/portal/747035191/Exploring_Presence_in_Interactions_with_LLM_Driven_NPCs_A_Comparative_Study_of_Speech_Recognition_and_Dialogue_Options.pdf) | late_search_discovery_not_downloaded_or_read | Primary PDF link surfaced during final metadata verification; excluded rather than count discovery as reading. |
| [An Empirical Evaluation of AI-powered NPCs in VR](https://arxiv.org/abs/2507.10469) | not_read_possible_duplicate | Possible same-study predecessor of Dialogs with GenAI NPCs; no independent-paper counting without identity verification. |
| Narrative Planning: Balancing Plot and Character（Riedl & Young, JAIR 39, 2010） | downloaded_not_read_beyond_identity | 需补完IPOCL的正式意图论证、人物理解实验、完整算法与失败边界；本轮CPOCL/Glaive/Sabre不能代替此前原文。 |
| 更多剧情规划、经验管理、用户模型与作者控制的经典原始系统及新综述 | coverage_gap_not_bibliographically_exhausted | 当前只有1篇2013综述及少数规划/管理者代表，不能声称覆盖互动叙事史；需补Fabulist/Mimesis、Thespian等原始系统以及此后整合性综述，先核身份再读。 |
| BDI、社会规范、组织/角色制度、文化差异与社会认知架构 | coverage_gap_not_bibliographically_exhausted | PsychSim/EMA/FAtiMA只覆盖部分个体心智和情绪建模；命名游戏与GovSim不代表整个规范与组织研究。需要可执行制度、例外、义务冲突及文化差异的原始研究。 |
| [FAtiMA Modular最终出版章节](https://link.springer.com/chapter/10.1007/978-3-319-12973-0_3) | final_chapter_not_read_author_draft_read | 已读12页作者稿有Figure??及未完段落，正式书目为44–56页。需比对最终版本；不能把同篇补完再计为新题名。 |
| [Emergent social conventions and collective bias in LLM populations，独立Supplementary Materials](https://doi.org/10.1126/sciadv.adu9368) | main_and_methods_read_supplement_not_read | 正文Methods已核，但详细模型提示、额外规模/历史/字母集合及稳健性图可能在独立补充材料。不能声称已穷尽全协议附件。 |
| [Reproducibility Study of Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents](https://arxiv.org/abs/2505.09289) | primary_title_and_abstract_located_not_full_read | 独立复现可检查GovSim强基线、异质群体及提示语言敏感性；本轮只确认该原始预印本存在，不能使用其摘要升级机制证据。 |
| [The AI Economist后续2022 Science Advances正式版及早期2020版本中的人类实验](https://doi.org/10.1126/sciadv.abk2607) | 2021_preprint_read_other_versions_not_full_read | 本轮34页2021稿不是正式2022版；需要核版本间实验、假设及人类验证变化，不能用论文家族名称合并证据，更不能将同论文版本算新增。 |
| [AgentSociety：另一个作者集的75页社会仿真研究（arXiv:2502.08691）](https://arxiv.org/abs/2502.08691) | identity_distinguished_not_full_read | 与本轮Jun Zhang等ACL Industry 11页并行框架不是同一论文；更广社会、制度干预与数据校准主张需要独立阅读全文。 |
| 更多游戏经济/宏观经济代理、制度学习与外部数据校准研究 | coverage_gap_not_bibliographically_exhausted | AI Economist、MMOAgent和Vox Deorum覆盖三个不同问题，仍不足以审视市场价格、异质人群、政策响应、经济预测的泛化与识别；EconAgent、MMOEconomist等应先核原始版本与身份。 |
| 商业游戏需求、关系、派系、犯罪、声誉、经济及日程系统的一手工程材料 | coverage_gap_neighbor_team_may_partially_cover | 这25项多为研究原型与邻接仿真，不能替代真实开发中的内容编写、调试、存档、可解释失败与性能约束；需对照The Sims等需求模拟与RPG派系/社会系统的一手材料。 |
| 长期关系、角色成长、情绪可信性、群体制度的真人玩家纵向研究 | coverage_gap_longitudinal_players | 相关论文有人类读者或标注者，仍缺长期实际玩家行为与持续世界体验；作者工具和玩家研究也尚未充分覆盖所需人群与时间跨度。 |
| 25项中逐篇read_scope明确未读的长示例、热力图、会务清单及代码实现 | explicit_partial_supplement_scope | 本轮已读全部正文与决定性方法/评分/样本协议，但非所有PDF逐字、非代码审计、非复现实验。若后续主张依赖未读具体附件，需要先补该附件。 |
| CivRealm及学习控制线相关近邻 | delegated_neighbor_team_not_independently_full_read_here | Vox Deorum正文足以识别其抽象层区别，但性能比较应由学习控制线的CivRealm全文记录交叉核，不能据Vox单方跨论文数字宣布优越。 |
| [LLM-Based NPCs in Video Games: A Systematic Mapping Study](https://pure.etsmtl.ca/en/publications/llm-based-npcs-in-video-games-a-systematic-mapping-study/) | primary_metadata_and_abstract_only | IEEE Transactions on Games 2026 early access，DOI 10.1109/TG.2026.3733302；正式全文访问未取得。检索377／纳入42及技术比例只见摘要，不作为已读正文结论。 |
| [Improved Non-Player Character (NPC) behavior using evolutionary algorithm—A systematic review](https://doi.org/10.1016/j.entcom.2024.100875) | metadata_and_abstract_only | Entertainment Computing 52 (2025), 100875；正式全文访问未取得。 |
| [The Case for Dynamic Difficulty Adjustment in Games（Hunicke 2005）](https://doi.org/10.1145/1178477.1178573) | metadata_only_not_full_read | 经典DDA原文未完成阅读；Dynamic Scripting与Enemy Within不能代替整条难度适应谱系。 |
| 导航、感知、避障、人群、现代运动生成、完整MARL和更多DDA方法 | coverage_gap | 本轮控制／合作24篇提供代表链条，并非该方向完整综述。详见学习控制专题的缺口表。 |
| [HER正式ACL2026版与arXiv v4完整版本比对](https://aclanthology.org/2026.findings-acl.1283/) | v1_main_and_v4_critical_sections_read | 完整正文实读v1，并补v4实验、伦理及F–H；未逐页比对正式38页。补版本不重复计数。 |

维护时先查题名、DOI／arXiv和现有规范卡，再补原卡，避免同一研究因改题名、正式发表、附录或代码更新重复计数。新事实若改变判断，直接修正相应主题段落；争议保留来源和不确定性，不以追加结论掩盖旧错误。阅读优先补薄弱方向及会改变现有认识的反证，不靠堆叠同一种小任务凑数量。
