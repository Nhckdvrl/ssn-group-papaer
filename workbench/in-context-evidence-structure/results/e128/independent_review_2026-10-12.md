# E128 独立pre-score源码/CPU校对（2026-10-12）

**八批实际CPU通过，可按末版f0a014冻结并执行既定四checkpoint16→32。0科学评分；这是前评分检查，不是科学阳性或GPU数值通过。**

源码SHA `f0a0146708e193e017eb33a1caf955d8e4d4bf22d91d73abb403b500be92265a`；8批/192context，4032实际prefix流与mask、6144query owner-scope、6144合成整Source缓存选择、12288demo criterion/code truth独立核对。未改science/card/claims/论文、未独立GPU运行、未commit/push。

## 真值、功能对象与主读数

A始终food；B origin=service同code、service_negative=service反code、food_positive=food同code、food_negative=food反code。每private方向反转均显式进入f/s与bias/product编码，8A8B及8query完整2×2每格2次；每ctx origin food/service discordant4。四world B评论映射是本Source多重集双射，B标签stream/名字/角色/原位置固定；跨Source不交换私人监督。

冻结primary只origin、discordant4、两Actor同权的joint .5[(00+11)−(01+10)]完整词表argmax准确率，context采样单位。不是四world平均、candidate选择或两Actor同时成功概率。shared只有2个唯一词ID，表面输出不能辨Source；other-word0与Source-identifiable False相配，不能写无泄漏。

f/s均按A private code定向，bias=p，FS=f*s*p；完整Gram=8I。T=.5mean[(zA−zB)(f−s)]恰等于origin discordant两Actor correct-margin平均，A/B selectivity恰等于相应Actor的discordant correct-margin。这是同一criterion功能输出的正交投影，不是新probe/第二份独立机制证据。相同code且不同criterion让本项确实改变E127单sentiment+code的功能对象；whole-cache/输出投影仍不定位ID、独立程序或输入过滤。

## 真token、可达图与cache

HEAD在公共schema之前；两行仅顺序变，事实/词频/长度相同。四world/order所有private原位置相同；world差仅B评论token，schema order差仅schema区域。所有严格历史跨Source private边关闭，self/同Source历史保留；传递闭包无另一Source私人信息经公共relay，schema仍能形成两套private cache。whole-query每个位置/层R0，不直读全部schema token；joint读两套private，own只读请求Source及HEAD。

00/11/01/10逐层替换全部Source-owned私人K和V，公共HEAD/schema从order0；HEAD看不到未来schema，query遮住schema，原positions/RoPE不重编号。deepcopy/ptr/seq检查避免改pristine，query按8样本batch复制。coherent重建、mixed-own对应单order、A privatecache across B-world graph-zero控制代码明确；其实际GPU误差/argmax与全部21/85层消费待raw出现后再核。

末版native/instruction均independent=False，只差一句prompt；这是0-score一行修正，不改材料/85条件/primary。E124–127旧instruction是prompt+形成隔离，已在其独立审计补语义限定，不重跑或降级其主coherence。

| CPU批 | n | prefix流/mask | query owner-scope | private False/True | schema token | prefix长度 |
|---|---:|---:|---:|---:|---:|---:|
| llama_confirmation_preflight | 32 | 672/672 | 1024 | 16/16 | [15] | 400–444 |
| llama_discovery_preflight | 16 | 336/336 | 512 | 8/8 | [15] | 380–396 |
| mistral_confirmation_preflight | 32 | 672/672 | 1024 | 16/16 | [22] | 462–510 |
| mistral_discovery_preflight | 16 | 336/336 | 512 | 8/8 | [19] | 443–471 |
| qwen14_confirmation_preflight | 32 | 672/672 | 1024 | 16/16 | [15] | 400–444 |
| qwen14_discovery_preflight | 16 | 336/336 | 512 | 8/8 | [15] | 380–396 |
| qwen3_confirmation_preflight | 32 | 672/672 | 1024 | 16/16 | [15] | 400–444 |
| qwen3_discovery_preflight | 16 | 336/336 | 512 | 8/8 | [15] | 380–396 |

每批两种匿名owner排列均实际出现，两private方向8/8或16/16；confirmation Robin/Jordan、探索Alex/Sam。各checkpoint探索/确认文本无交集。Mistral discovery schema19/confirmation22 token，M回答分隔保留真实tokenizer编码；跨家族长度无需相等，同批配对位置严格匹配。

固定food-before-service/模板材料、已有binding/竞争/校准/检索解释仍在；保留一般访问与原监督不等于固定激活信息。没有新增微观矩阵或旧claim资格；source级readout设计已足以按预定功能问题执行，科学方向/数值有效性待全raw。CPU进程exit0，尾部multiprocess ResourceTracker析构噪声已保留，不是geometry/gold失败。

[JSON](independent_review_2026-10-12.json)；后续raw独立复算应保留此PRE_SCORE封存另写。
