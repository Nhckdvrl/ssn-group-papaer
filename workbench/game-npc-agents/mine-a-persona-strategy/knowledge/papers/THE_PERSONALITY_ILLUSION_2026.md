# The Personality Illusion（ICML 2026 main）

证据：PMLR正文§2–4、Table1/Figure3–5，附录D.5/D.6/I.1/J/K/N与作者数据/代码入口已读；未复现论文统计。
来源：[PMLR](https://proceedings.mlr.press/v306/han26n.html)，[code](https://github.com/psychology-of-AI/Personality-Illusion)。PDF SHA见E08_sources.json。

- **DOCUMENTED / idea来路：** 用量表描述LLM人格的习惯缺行为效度检验；作者区分对齐阶段、问卷稳定性、具体行为与定向注入。27次扰动重复，BFI/SRQ；行为包括CCT、IAT、阿谀及两种诚实读数。主要“alignment”是回归符号是否符合事先人类心理期待，50%是符号chance，不是游戏任务成功率。
- **正文与附录边界：** RQ3主文重点agreeableness→sycophancy和self-regulation→risk；三种注入形式，附录含其它配对。D.5区分within/between model，D.6按人类效应证据强度复核；不能声称作者完全没考虑粒度/统计稳定性。未拒绝关联不等于人格不存在。
- **与我们距离：** 它已有self-report/behavior与persona注入的claim ownership。没有作者RPG人物目标→原生parser→世界后果闭环；这个设置差异本身尚不足成贡献。我们需研究作者利益目标的条件性决策，报告工具/状态失败的替代解释。
- **可迁移动作：** 问卷作为独立测量而非gold；逐模型/任务复核，不把一般相关性压成永久gap。

**已核源码快照：** psychology-of-AI/Personality-Illusion@a934083dcccd4428396497020578e89ffc9c51f8；behavioral_tasks/README.md blob db5fae0efe32bd57cd263b4a04ce97f591401e28。Risk-taking来自notebook生成，honesty/IAT/sycophancy另有datasets，data含原报告/注入结果。此代码/数据可审计，不等于可以原样作为游戏NPC心理金标。
