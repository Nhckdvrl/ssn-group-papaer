# Beliefs About the Speaker’s Reasoning Ability Influence Pragmatic Interpretation（Open Mind 2025）`[证据级别：正文全文、附录A–E全文与A原界面图]`

Mayn/Loy/Demberg，9:89–120；[作者最终稿](https://www.uni-saarland.de/fileadmin/upload/lehrstuhl/demberg/Publications/Beliefs_About_the_Speaker%E2%80%99s_Reasoning_Ability_Influence_Pragmatic_Interpretation.pdf)，[OSF](https://osf.io/f5nmv/)。32页文字全部读；Appendix A原界面图单独看；Fig3–5/11只读文字解释，未独立逐点数字化。原models.R全文、graphs.R尚未全文；两实验公开CSV/排除表已下载，尚未复现Bayesian mixed regression。SI不存在独立下载假定。

1. **论文形态：** 理论区别＋人类受控实验＋个体策略；不是新benchmark leaderboard。
2. **背景压力：** Franke/Degen2016发现listener不同递归类型；Grodner/Sedivy2011、Ryskin2019与Gardner2021发现可靠性/经验影响inference，但“听者自己能解题”和“听者认为别人能选好表达”仍不同。只有所有人都对完题的average score不能识别第二层。
3. **改变的前提：** 不再默认generic perfectly rational speaker；听者把adult/4-year-old的能力信念带入同一reference game。控制题接近ceiling，关键题变化，避免把全局任务失败解释成meta-reasoning。listener L0与reasoning-about-literal-speaker L1不能混称。
4. **idea来源 DOCUMENTED：** 上述partner reliability谱系＋Franke/Degen的reasoning heterogeneity；作者选择已知较容易的simple trials，确保听者有余力考虑对方，而非凭空制造模型bug。作者承认受限message集合人工，future natural utterance不是已成立结果。
5. **与近邻距离：** Goodman/Stuhlmüller2013操作知识；这里操作关于reasoning ability的信念，二者不是同一个latent。Franke/Degen2016是listener自身类型；这里是关于speaker类型的信念。Mayn/Demberg2023拥有“任务做对不一定成功推理”；本篇把reported strategy与graded target相连。RAILS2025后续把身份信息换为实际反馈经验；BWIM2026再进入LLM build/action/clarification，因此“第一次speaker-specific calibration”无ownership空间。
6. **实验/数据：** 每人24trials：8critical＋12unambiguous＋4identical-object ambiguous；先3speaker practice，最后重做first critical并解释策略。两组between-subject speaker identity；Exp1 retained79（40adult/39child）、Exp2 retained160（80/80）。100points分给三对象。critical adult/child均值Exp1 70.8/57.3、Exp2 70.7/62.2；Bayesian group×trial interaction3.17 CrI[1.35,5.00]与1.83[.42,3.27]（sum coding，不能误读raw group差）。四chains4000，正文说warmup1000；代码未显式设warmup，brms默认需版本核对，尚未称精确统计复现。
7. **证据与短板：** Exp1 child cover story引入alien，Exp2移除并加child photo后效应复现；一个移除alien但未加photo的版本CI含零，作者公开为failed manipulation。成功组不证明“任何一句child标签就会生效”。策略解释事后收集，未报告meta-reasoning不等于未发生；categorical+graded混合解释不是identified cognitive mechanism。Appendix E比较unimodal normal simulated participants，只是异质性线索，不是正式穷尽所有mixture替代的模型比较。
8. **可迁移的研究动作：** 分开listener任务能力、speaker-policy信念、最后的解释选择；同时报告控制成功与关键变化，比较能对同一效应做出不同boundary预测的解释。不要把一切下降叫取消推断。保持个体策略/分布；一个模型多个采样不是多个人类reasoning类型。
9. **对我们：** mixture speaker model给出 P(target|red)=2/(3−λ)，λ=0/.5/1时2/3/.8/1。literal speaker仍支持target偏好；“应停止脑补”的norm必须说清生成过程，不能直接标literal条件为FPR。Appendix D λ=0归一表的triangle行印为0/0，按其前一概率矩阵应为0/1；这是局部表格算术备注，red的2/3论证不变，不宣称整篇错误。human有50%反应而Bayes-L1下界2/3，作者讨论listener L0/概率错误/processing depth，而非强行用一个λ拟合所有人。

**值得继续弄清楚的未知（RECONSTRUCTED，非finding/novelty承诺）：** 观察同样解释时，LLM是在使用关于speaker选择表达的模型，还是只随身份/回答角色改变输出？如何让对选择机制的独立预测与后续world/intent/commitment读数互相约束？公开source足以做规范审计；删除人类重要photo再迁移text-only后，不能直接宣布人类replication。
