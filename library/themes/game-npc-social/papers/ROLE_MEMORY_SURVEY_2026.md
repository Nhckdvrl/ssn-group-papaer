# More Than a Role: Memory in LLM-based Role-Playing Agents

Shuchen Wu等。2026-10-22从[作者仓库PDF](https://github.com/aixiaodewugege/More-Than-a-Role-Memory-in-LLM-based-Role-Playing-Agents/blob/main/More_Than_a_Role_Memory_in_LLM_based_Role_Playing_Agents.pdf)选读导论、§2.4、§3行为整合、§4未来问题与局限；其余方法谱系仅定位，未全文/全部引文复核。仓库HEAD `ab18d851e1d7c465c87bcc58b5c84d1c1b598c2a`。

**发表身份校准：** README标“KDD2026 Oral”，PDF页脚为PILA ’26。[官方PILA会场](https://pila26-workshop.github.io/)列出该论文，并明确论文不进入KDD2026主会proceedings；[KDD官方workshop目录](https://kdd2026.kdd.org/workshops/)也列PILA。按KDD共址workshop综述记录，不升级成KDD Main Oral。

1. **形态：** 角色记忆研究综述与方向框架，没有本文独立方法性能实测。
2. **压力：** 人物对齐与长期互动记忆常被分开讨论，关系变化和身份连续性需要合看。
3. **改变前提：** 将角色自身知识/身份/经历与用户互动/关系状态两条记忆流放在同一系统视角下。
4. **idea来源（DOCUMENTED）：** 角色扮演与个性化记忆两套文献的整合。
5. **最近邻距离：** 比通用agent memory更强调角色立场、关系和表演；与ArcANE/PHASE/DREAM的具体方法任务不同。综述议程不等于所有能力已实现或已证明失败。
6. **主要观察：** 提倡角色条件化整合、记忆维护/信念修订、记忆对行为的实际作用、互动和长期评价。其使用广义memory涵盖外部记录及参数中保留的角色特征。
7. **边界：** 无统一量化meta-analysis，作者承认任务和评价碎片化；“必须采用联合图或参数适配”等方向建议不能作为未经实验的必要性定理。
8. **可迁移动作：** 将人物与关系变化作为完整系统问题，保留立场、回应与互动后果，不停留于事实检索分。
9. **对D：** 支持该问题是社区正在关心的研究议程；不赋予我们问题的独占权，也不因别人提出同一宽议程就放弃它。贡献须由完整方法与证据建立。
