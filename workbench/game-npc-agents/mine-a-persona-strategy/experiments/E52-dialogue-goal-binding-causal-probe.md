# E52：自己台词中的目标物品绑定与动作竞争（2026-10-15）

- **状态：** DONE；设置在运行之前登记。
- **类型：** PILOT / 白盒因果诊断，不把单case当群体结论。
- **对应：** I04、P12；用户要求横向吃透既有矛盾，而非预设管道故事。
- **问题（一句话）：** 原角色和目标仍可见时，自我台词把worm绑定幼鸟是否改变下一物理选择？纠正为source mid-goal的nut后，内部哪个位置可传递这项变化？
- **来源：** 固定E22原鸟快照p14908_s2001_first1。源短目标eat worm、mid-goal给幼鸟nut；实际台词“No sharing, I need this worm for my hungry babies!”。此case由旧E22先前发现，本次不是按新结果再挑样。
- **设置：** Qwen3.5-27B / Qwen3-32B固定revision，现有fgvd，HF BF16/SDPA/local-only。原角色、目标、可见状态、原非speech合法菜单固定。将台词里唯一this worm改为this nut，其他字符保持；先核token对齐。原all_dialog、no_dialog、原事实cue、原目标binding cue保留，另加原persona中的等长无关提醒。全程原人格一致；修改的是显式历史内容，不称整体人格变化。
- **白盒干预：** 正确自我台词为donor，原台词为target；在decoder block输出替换唯一改变物品token的residual，层0/15/31/47/63预登记，不挑最佳层。31层target→target为sham，31层等L2随机delta为控制；反向donor←target检查方向。捕获prompt尾residual与动作tokenlogits，不以可视化单独宣称机制。
- **动作协议：** HF在共同JSON action前缀后对完整原生physical command trie进行受限采样，temperature .7、top_p1、top_k0、32draw，seed520000+draw共享配对；不裁为eat/put二选一，不生成理由再筛答案。每个draw独立原图fork执行一个native动作，记录实际物品归属及event。
- **读数：** eat worm、put worm on nests、其他全部合法动作概率；原event执行及material变化；每层patch与原输入的配对动作差和verb/目标token竞争。32draw只描述这个快照的采样波动；独立N=1。source renderer顺序用E22已保存观测与菜单，不改世界。
- **阳性对照：** 旧CPU native eat/put合法及实体后果；full goal-binding原普通恢复控制；target→target采样结果、logits与baseline一致。新HF/trie协议的黑盒条件与原E22并列报告，不冒称vLLM逐输出复现。
- **噪声地板 + MIE：** 配对32draw及sham；报告连续差值，不按bar淘汰方向。词替换、目标cue、随机patch都能改变解释，保留全部结果。
- **混杂审计：** 此历史反事实不改变Fox已发生的steal失败；研究NPC在同状态看到什么文字，不推整个交互world总效应。token替换需要位置/长度一致；不将目标重新取舍自动叫人格失败。最后层物品位置patch不能经后续层影响首动作，作为局部位置负控制。随机delta共享实际替换范数；模型家族同源，不宣称跨家族机制。
- **决策表（跑之前写）：** 修正物品词影响动作且具体位置patch按方向改变→继续目标绑定路径，独立自然case检验；只有goal reminder有效→目标优先级/信息显著性；错误/正确台词都同一动作→查看分布/logits与其他矛盾，不强求Gap；sham失败→协议不用于因果解释，保留raw并完成原黑盒；persona信息可用但动作竞争变化→“遗忘身份”不足解释。
- **算力预算：** 两独立单GPU，约0.5–1.5 GPU·时/模型，合计最多8卡，不启动旧RL。**实际：** 待运行。

## 结果
两模型各448次生成，全部448 native合法，sham逐draw动作与baseline完全一致。原base prompt哈希与E22原记录一致，但本轮强制action字段前缀并只生成命令，不能当原vLLM完整输出协议逐样本复现。

27B原输入eat worm25/32、put worm7/32；仅修改自己台词worm→nut后eat30/32、put2/32。正确词位residual→原输入在层0/15/31的eat计数30/31/28，层47/63均25；31层随机等范数为28、sham25。反向31层仍eat30，与正向不同，保留不包装可逆统一机制。

32B原输入eat6/32、emote grin24/32；改词后eat27/32、grin3/32。词位patch0/15/31为eat24/20/21，47/63为2/6；31层随机10、sham6，反向23。普通目标binding cue21/32吃虫；物理事实cue30/32放虫，并不具有统一恢复方向。全部动作分布/实际world变化见results/E52_27b_binding_patch.json与E52_32b_binding_patch.json。

该结果将“目标信息/当前目标指向的竞争”具体化为可干预词位；原角色与world未改。更改台词也可以是新目标的合法表达，不能据此给人格失效下结论；第一动作的grin/hug不等于最终任务失败。下一步需要最终资源后果与跨角色状态干预、普通强控制，以及真实自然轨迹的语义类型标注。两模型推理233.34/271.76s，load28.07/22.52s，总计约.154 GPU·时。


2026-10-15校对：实际未保存逐token action logits，保留的仅residual/tensor及真实采样动作，不能汇报logit竞争数字。原“正确/纠正”指替换成source中喂幼鸟的nut，不证明原自己台词是错误信念；也可能表达新的合法目标取舍。
