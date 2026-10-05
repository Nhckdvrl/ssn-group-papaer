# E11：加长主语后的角色读数，是引用方式还是修订失败？（2026-10-05）

- **状态：** RUNNING
- **类型：** MEASUREMENT / P06异常追why；不注册paper novelty
- **对应：** C01 / P06 / P08
- **问题（一句话）：** 无歧义句中的extension使原角色回答下降，是把NP中心词当完整主语的引用歧义，还是最终事件理解也受损？
- **设置：** 固定Jurayj前3个NPZ源词汇组（不是根据模型结果挑选），原GP/cue/blocker/nonGP各short/extended；上游句子字节不改。原四读数保留，另加完整subject-span与head-noun题；从原component取isolated主句（6句、4个final读数）作没有前句竞争verb的控制，共30句变体/168候选QA。新句/新题与旧题都必须先由独立opencode逐句审计，全部gold=null，概率探索层；Step5额度恢复后复核，不自行gold。frozen Qwen3-8B FP32、native、thinking off、neutral system、reg/rev×base/一句repair四配置（最多672任务），现有模型/env/cache。
- **至少两个解释：** (a) exact constituent/reference：extended时引用短NP使元语言subject判定变化；完整NP/head题应改善cue/nonGP/isolated，final semantic不应同幅下降。(b) revision/attachment failure：GP extension效应主要来自前句竞争verb；换head/span仍留下GP特异下降，并与final semantic下降同向。(c) generic NP complexity/access：即使isolated或early cue，extended仍损伤完整NP/head及semantic；不会只影响原短NP role。它们可能并存，不强迫单原因。
- **读数：** 每source-set×condition×extension×question×固定配置PYes、choice mass；extension−short、full/head−original role、其extension交互和GP−cue交互，明确paired intersection与n。自然final/initial semantic原题保持，报告每条外审有效性/答案/理由；独立调用组合不是同时内部parse证据，不计算能力accuracy。
- **阳性对照：** short原role与full-span题完全相同，检查相同prompt概率差；cue/nonGP/isolated条件，及原final-semantic。所有配置报告，不选赢家。
- **噪声地板 + MIE：** 已测FP32重复max drift约2.6e−5/0 flips；同prompt重复报实际差。三词汇组pilot的bootstrap只描述此样本，不设效应/正确率停步门槛，不升级能力证据。
- **混杂审计：** 引用变长是本次被干预变量；head/full题术语与长度也变，不能仅凭改善说唯一原因。isolated移除前句也缩短输入，结合same-length extended cue/nonGP作对照。PP/RC extension类型单列，不宣称3组代表整个构式；所有新句/题由外部模型审计，agent只做hash/IDs/覆盖核对。来源前3和候选168固定，不看推理后删行。全部无gold，不把free模型叫人审或Step5。R8一句repair保持。
- **决策表（跑之前写）：** full/head只恢复无歧义的role且semantic保持 → 把原role的extension效应降为instrument问题，使用已审核自然读数追GP的实际后果；full/head/semantic仍有GP特异extension下降 → 保留attachment/revision解释并找下游事件使用对照；isolated所有读数也下降 → 追一般NP复杂度/access，不能称digging-in；三组/审计不足或mixed → 报不确定，结合E01全量配对，不扩大模板sweep。
- **算力预算：** 一独立单卡<0.04 GPU·h；审计2并发，与既有E01外审4并发合计≤8。资源模型下载零、请求显式无代理。**实际：** 待记录。

## 结果（跑完后填写；不改以上读数与决策）
- 数字（含CI）：
- 结果文件：
- 主张变化：
- POST-HOC：

### 部分cohort（本批推理之前）
- 所有已normal-finish外审返回中取原先的前3源组（固定规则，不挑Qwen结果），本snapshot为9/30变体、50候选QA/49eligible、gold=0；完整cohort仍在外审，timeout不视OK，缺失见[D0](../results/D0-E11-opencode-snapshot1.json)。
- 先跑此固定部分cohort的4既定配置（196任务），所有n1的paired CI=null，不能升级稳定结构主张；仅用于原先why问题的条件诊断，全部配置/输入保留。
- raw input SHA `6ebfdf33cebedfbc9618f8767e9e48b3423a01c01ecb69f097924cbf740d8960`。外审对NPZ:1 extended comma中原短NP-role标interpretation-dependent，full/head标clear；该审计在本次Qwen结果之前返回，理由/原始JSON留cache，agent未自行gold。

### Snapshot1结果（全量仍在外审）
- 9/30变体、50QA/49eligible、196任务，20.81s / .00578 GPU·h；28组相同prompt重复PYes差=0。初始pilot只NPZ:1有extended配对，n1所有CI=null；NPZ:2只到short，不混报两个组的扩展效应。
- NPZ:1 neutral/reg/base extended blocked：原role=.04037，fullNP=.99989，head=.99688，semantic=1；extended comma：原=.43799，fullNP=.99999，head=.99764，semantic=1。其short原role/fullNP为完全相同题且概率相同。
- 完整NP在四reg/rev×base/repair配置中均将extended blocked/cue的PYes提高到约.999–1；head在题先blocked仍有失败（.5546/.0615），不选它作赢家模板。short GP fullNP仍≈.00429（句先）/≈.00099（题先），句先semantic=1/题先≈.00089，不能把引用修复当已经解决所有GP现象。
- 按决策表：这一个项目的unambiguous role extension下降支持引用/constituent测量因素；停止把这部分当digging-in证据。n1且free审计无法建立稳定机制；GP extended和isolated extended本轮因外审timeout缺失，不能报告其结果。对所有当时incomplete外审做单worker重试，原失败保留独立目录，不基于Qwen结果选重试。
- [summary](../results/E11-opencode-snapshot1-summary.json)、[scores](../results/E11-opencode-snapshot1-scores.csv)、[config](../results/E11-opencode-snapshot1-config.json)。C01/C02保持L0，不升级novelty。
