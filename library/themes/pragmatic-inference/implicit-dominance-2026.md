# Implicit dominance（Language and Cognition 2026）`[证据级别：全文 / 原代码与数据]`

[原论文](https://doi.org/10.1017/langcog.2026.10110)，2026-09-17发表，23页正文全读；[OSF原资产](https://osf.io/unmy6/overview)，Rmd/README/PsychoPy关键逻辑、三human表及Exp2八原图已核对。未复现R mixed模型、未独立审转写。

1. 形态：理论问题、自然对话受控真假交叉、三人类实验与替代解释控制。
2. 压力：以往用不同utterances比较explicit/implicit commitment，无法判断同一句话内两层意义怎样相互影响。
3. 改变前提：同一utterance保持，交叉操纵两层实际结果；分别问literal/implicit commitment与总体trust。三者不能统一为一个数。
4. 来源DOCUMENTED：现实white lies和technically true but misleading的对比；从自然tension产生对照，不造奇怪prompt。
5. 距离：Mazzarella2018/Bonalumi2020/Reins2021已有implicit commitment；本研究拥有同句跨层依赖、implicit dominance、trust整体整合。首次发现这些人类结构不能作为我们的claim。
6. 方法：保留91/93/85参与者；Exp1/2八强bias自然dialogues，Exp3十六对主观/客观；原预试>90%理解一致、confidence>60。Exp2修改probe/actual-event措辞排除salience解释；Exp3改变subjectivity。人类不重复同trial两个commitment问题。Exp2/3原过滤703/1253行相符；Exp2原lm三个系数9.268/2.982/18.285按论文小数精确匹配。
7. 短板：Exp1发布过滤后703而论文708，原paired-t n90/t5.157而论文df90/t5.247，保留版本不符；正文称mixed但Exp2 meaning源码改lm。每target八材料较少，主观/客观同时换字句；human正确理解后的conditional样本不等于全部LLM输出；null interaction不证明无作用。
8. 研究动作：保持一句话、分开目标对象、交叉literal/implicit证据，强结果先审措辞/事实呈现，再换语义主观性边界；解释先问对照能排除什么。
9. 对我们：判断literal事实为假不等于推断speaker的拒绝意图不成立；事件真值、speaker承诺、信任须独立。E40仅source/human驻留，不能称完成LLM实验。后续要用原八图保真转写、固定原问题与source norm，不能从literal_question或gold补造对话，也不预设模型失败。
