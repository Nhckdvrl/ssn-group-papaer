# E22：原生访问权限信念与行动的最小控制（2026-10-14）

- **状态：** DONE / 部分测量资格失败已降级
- **类型：** PILOT / 解释竞争；不预设persona gap。
- **对应：** I01 / P08；E20–E21。
- **问题（一句话）：** 交流后放置食物/放弃取食，是合理目标与威胁取舍，还是对物理访问权限的误判，是否由自身台词带入？
- **设置：** 固定E21两发现性快照：p14908_s2001_first1鸟首次physical前（狐狸steal失败，虫仍在鸟手里），p14207_s2001_first0 creature首次physical前（algae仍在room、仅有对话宣称归属）。按原图+之前全部native events重放，验证物理state与缓存逐byte一致；不改人物/目标/规则。32draw/条件：no_dialog、partner_only、all_dialog、all_dialog+一句原生访问事实、all_dialog+一句原作者source goal/object绑定提醒；native physical menu在5条件中完全相同，免除E20/E21 speech候选数量差。保留相同可见非speech事件，删除history仅为显式干预，不改物理state/对方实际已听话。action和权限forecast各独立call，不把forecast写回行为。另每快照32neutral third-person forecast为强普通对照。全部seed固定220000+case*10000+condition*100+draw；每个action fork原图独立执行，原随机RNG按seed，不脚本补救。
- **读数：** 鸟：fox直接get当前held worm是否合法、native put worm on nests之后fox get是否合法；creature：自己当前get algae是否合法、eel当前get是否合法、仅say归属是否改变get合法性。原生parser/fork给确定性ground truth，预测的是Can而不是Will/道德权限。逐draw预测准确/条件差与选择类型、原物品归属变化完整保留；鸟放食物不是预定错误动作，creature避险不是预定错误动作。physics forecast不等于内部表征读出。32draw分半A/A JS与I(action)/A测量区别不混。
- **阳性对照：** CPU原非法get held item/合法steal、放公共nest后合法get；speech前后state相同，两快照legal菜单和非speechhistory复放匹配。neutral third-person与一句exact fact应能读明操作，否则不是角色机制检验。source短目标worm/中目标nut准确记录，原角色价值未改。
- **噪声地板 + MIE：** 32draw每格，bootstrap按draw只估单快照条件波动，不作2图总体CI；all_dialog动作A/A JS floor。权限条件差或核心行动差≥20pp且超floor才扩图；只一条put不能作稳定异常。误判缺失/差异仅词锚或被一句提示吸收为负结果，无新科学claim。
- **混杂审计：** discovery snapshots有选择性，明确只pilot；no_self/no_dialog改变长度/内容，若有作用须后续长度和词锚控制，不提前下机制结论。强事实cue直接给知识，不冒称训练增益；binding reminder是已有goal grounding控制。战略性威胁可能合理影响Will，权限forecast只Can。角色长期目标优先可能合理，不能把eat worm唯一gold外推人格效度。所有原始负/JSON失败保留、无付费API。
- **决策表（跑之前写）：** 权限准确、动作多样→角色/威胁取舍优先，I01权限假说降级；仅own-speech影响→已有priming解释，另查目标绑定不宣创新；一句事实或目标绑定恢复→已有强prompt/grounding解释，不新loss；错误权限条件效应与暴露共同出现→再排内容/长度/叙事，找独立source图；阳性失败→修工具，不判科学假说。
- **算力预算：** CPU gate、单GPU≤1小时；32draw×(2snap×5cond×2branch+2neutral)=704 local calls，chunk16以实测成本为准；现有fgvd+deps，0API，白天项目≤8GPU。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

尚未运行。它只能改变下一研究动作，不能据这张卡宣称已经得到好的新idea。

模型前CPU gate发现原WorldViewer按set迭代，跨Python进程对象/背包呈现顺序不同，material snapshot精确一致但字符串不同。两次0model失败目录保留e22_cpu/e22_cpu_r1；不作NPC失败。修正为核原生view语义对象与物理state一致后，复用原缓存native view以保持输入/菜单逐字相同；显式记录fresh order equality。不更改世界或persona，模型尚未运行。

完整704calls、0JSON失败、146.65秒、654560输入/25276输出token、0API，原两快照view/schema/prompt hash控制通过。Bird无对话eat32/32，all_dialog eat23/putWorm9；物理事实eat20/putWorm10，源目标绑定eat31/putWorm1。关键正向权限（放下后fox可get）all_dialog29/32，事实32/32，未支持“错误权限驱动放置”；Creature对应Can通常正确且一句事实/绑定get31/28（all20），不能把威胁响应当物理错误。

**测量降级：** 冗余负向字段put_blocks_fox_direct_get原neutral仅5/32正确，all_dialog0/32，与正向访问字段常逻辑矛盾；联合forecast准确率不具有机制解释资格。保留原读数，未事后删除该字段或重定义primary。需要新卡/通过正控制的格式才能重测该构念。原结果[E22](../results/E22_access_belief_summary.json)；I01权限机制未获得支持，普通目标绑定/priming/合理优先级仍可解释，新科学增量0。
