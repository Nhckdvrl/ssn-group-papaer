# E24：同人物编码上下文的原生utility闭环（2026-10-14）

- **状态：** DONE
- **类型：** PILOT / 原生后果校准；不把padding实现差异自动当新idea。
- **对应：** C01 / P09；E23。
- **问题（一句话）：** E23人物文本完全不变、仅编码批次改变带来的策略差，是否真正改变该角色在作者原生游戏中的收益与世界状态？
- **设置：** 原v3-large全test100、原16NPC/200cycles、full/no_consist公开trained seed42/43/44。body PersonaConfig、preferred_actions、BigFive、needs dynamics、原reward与物理规则全不变；仅输入编码分别cached（原作者batch32）、source_recomputed（数值地板）、singleton（部署单条/实际最后非pad）、long_peer（同最长原文本一起编码；伙伴不进入游戏）、proper_pool（原batch32最后非pad）、fixed_max128（同文固定padding）。3原世界seed24011/24012/24013，每seed按固定RNG打乱同100角色，16/cohort不足时依原E17padding重复最后4角色，only actual100纳入focal汇总。源独立行为协议batch-before-cycle、原AEC步骤。先first16 test/Full42/world24011 cached episode和byte-exact replay，测成本；若可承受再全部300focal trajectories/variant/mode。torch采样seed与world位置/needs/同伴角色次序在variant间相同，后续状态自然分叉，无动作脚本fallback。
- **读数：** 原生每角色累计reward、action轨迹/终端needs/位置、pref-action rate、critical needs fraction；相同persona/worldseed的return差与paired按persona簇bootstrap95%。六种code original text相同；source-recomputed为数值噪声地板，proper pooling是已知工程控制非新算法。不同动作不等于策略失败/人格失效，reward中persona style与preferred标签已有作者定义，不能独立外推人类人格效度。所有trace在cache，summary进git。
- **阳性对照：** 原trained weights strict-load/hash，cached两次完整episode逐byte相同；每variant original persona json/config/hash不变；原body/游戏初始化state严格相同。E23原500编码与公开数组500/500 cos≥.99999，float error可定位；其它encoder搭伙文本没有进入native场景。
- **噪声地板 + MIE：** 原完整replay无差；source-recomputed vscached的差为fp16/版本微扰地板，3world seeds全保留。相对native reward≥5%且超地板/跨训练seed一致，才值得深挖shared projection/utility条件机制；动作变但utility差小→角色行为可以多样且收益稳健，承认正结果。阈值只是pilot决策，非自动科学判决。
- **混杂审计：** all16 code同时变，含population/peer动态效果，不当单focal纯direct effect；独立same-state action影响在E23已有记录。properpool修复会改变既有训练分布，不能把更规范encoder直接叫更好策略。只v3-large公开角色，非整篇所有game/UE5/MeltingPot；source PCA/跨语言50designer与MeltingPot readout负结果已有ownership。world reward人工style归因和utility分开。当前source引擎与历史训练reward版本阅读债仍存在。
- **决策表（跑之前写）：** 原生收益稳健→记录encoding变化却utility保持，不强上训练；明显utility改变→按原context-batching与pooling分解机制，并加单focal/共同state/control；只是浮点微扰或actor布局→降级，别称角色耦合；正控制失败→先修资产/协议；已有普通correctpool控制充分解决→工程/审计改进，不冒领科学创新。
- **算力预算：** 单CPU线程≤1小时（预计约10分钟），0GPU/0API；只小MLP native physics，3seed全保留。07:00后本项目≤8GPU。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

六公开政策×六编码条件×三世界seed完成，每条件300个focal轨迹；原人物文本/body/reward与初始世界固定，cached完整episode逐byte重放通过。原文固定pad到128的收益变化（Full42/43/44；NoCons42/43/44）分别为−3.07/−13.56/−4.51；−2.22/−3.88/−3.56，约下降2–14%。Full43的persona簇95%区间[−18.06,−9.38]。正确pool相对旧缓存的收益变化方向随policy种子不同：Full43+8.92[5.63,12.31]，NoCons44−1.12；不能讲通用修复收益或Full特有稳健性。

单CPU线程250.10秒、0GPU/0API。完整数值/CI见[E24结果](../results/E24_encoding_native_utility.json)，raw cache/runs/e24_encoding_native。这里只证明编码部署上下文可能改变作者原生utility；含全部16角色同时变码的群体效应，作者style reward仍限制外部人格效度。普通正确pool消除编码批次依赖，**此项审计本身不构成好的新idea**。E25将从正确编码重新训练，而非把旧模型分布偏移称新机制。
