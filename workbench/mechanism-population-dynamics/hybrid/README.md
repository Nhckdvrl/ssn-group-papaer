# hybrid：混合架构（循环层 + 少量全注意力层）里，词是在哪里、靠什么拼起来的

**状态（2026-11-23 06:00）：**
- 探索子线，用户 11-23 签字开跑。workbench 在登记表里仍是 PROPOSED，ACTIVE 名额不动（R2/R7）。
- 卡 E194–E198 已跑完；E197 的 Qwen3 对照还在跑。没有推进任何主张等级（全部是 PILOT）。

## 问题（一句话）
アテンションをほとんど持たないハイブリッドLLMは、サブワードをどこで・何によって単語にまとめているのか。

（几乎没有注意力的混合模型，在哪里、靠什么把被切开的子词拼成词？）

## 目前的答案（三个机构的三个混合模型都成立的部分）
1. **在第一个注意力层之前，由最早几层循环层拼好，不比同配方的 Transformer 慢。**
   - 两对同配方模型：OLMo-Hybrid 对 OLMo-3（E194），Granite-4.0-H 对 Granite-4.0（E195）；纯 Mamba 的 Falcon-Mamba 也一样。
   - 原先的假说"拼词要等第一个全注意力层"（Bandarkar 2609.35378 的推测）被否定。
2. **起拼的必要条件是循环层里宽度 4 的短卷积。**
   - 关掉卷积的邻位抽头，任何长度的词都拼不起来，读数落到"只剩最后一片"的下限。
   - 循环记忆单独时什么都拼不了。
   - 在 OLMo-Hybrid（E196）、Granite-H（Mamba-2）和 Qwen3.5（GDN）（E198）上都成立。
   - 只有卷积时，短词照样拼好，长词受损的程度随模型而异（OLMo 强、Qwen 中、Granite 弱）。
3. **前几层没有开始拼，后面的层不会补拼。**
   - 5 片的词完全补不回来；2 片的词只部分补回。
   - OLMo-3 关掉前三层注意力后同样补不回来（E196）。所以拼词是一个固定在早期的阶段，不是"注意力和循环层谁有空谁来做"。
4. **"第一个全注意力层的跨语言事件"不是拼词，也不是跨语言靠拢（POST-HOC）。**
   - 在 Granite-H 和 Qwen3.5 上，它是"进入全注意力层的表示"的几何尖峰：随便配对的句子同样出现，并与第一主成分跳变同步（E197）。
   - 按预先写定的口径判"复现不了"；口径失误已在卡上写明。

## 它能解释的、别人留下的现象（推论，尚未直接检验）
- **Bandarkar 的蒸馏结果：** 他们把 Transformer 蒸馏成混合模型时，短卷积按恒等初始化（附录算法 1），这正是我们的"关卷积"状态。按第 2、3 条，学生模型在早期拼不了词，所以凡是第一层放全注意力的排法都胜出，切得最碎的非拉丁文字收益最大。
- **Zeng 2611.01909：** 把最早的循环块换成逐 token 投影后，检索不变、困惑度 10.6 → 44.7。我们关卷积时 NLL 也从 2.97 升到 4.03，丢掉的正是拼词。
- **Allen-Zhu Part 4.1：** Mamba2 的性能主要来自短卷积。这里给出一个语言学上的理由：短卷积在做拼词。

## 还没站住或有分歧的
- **R2（Patchscopes 复述）与 R1 不一致：** 混合模型早期层的表示更像原词，却更难被"移植后读出"。未解释（E194）。
- **"循环层更讲片段顺序"：** 只在第 1 层两对模型都复现，第 2 层不复现（E195）。
- **"只有卷积时长词拼不了"：** 只在 OLMo 上过了预定阈值（E198）。

## 卡片
| 卡 | 内容 | 结论 |
|---|---|---|
| [E194](experiments/E194-olmo-hybrid-word-assembly-pilot.md) | OLMo-Hybrid 对 OLMo-3，三把尺子 | D（R1/R2 不一致）；A 被 R1 和余弦否定 |
| [E195](experiments/E195-order-strict-assembly-replication.md) | 顺序绑定差异在 Granite、Falcon-Mamba 上是否复现 | 不复现（第 2 层） |
| [E196](experiments/E196-gdn-assembly-causal.md) | OLMo-Hybrid 前三层的卷积/记忆开关 | 卷积负责 |
| [E197](experiments/E197-first-attention-event-check.md) | 第一个全注意力层的跨语言事件 | 复现不了（口径失误）；POST-HOC 为几何尖峰 |
| [E198](experiments/E198-conv-memory-replication.md) | 卷积/记忆开关在 Granite-H、Qwen3.5 上复现 | 只复现 1（卷积必要） |

关键图：[`results/e198/fig_conv_memory_three_hybrids.png`](results/e198/fig_conv_memory_three_hybrids.png)。

## 资产位置（不进 git）
- **fvcrc13 `/tmp/xiang_e194/`：** OLMo 四个检查点、uv 环境（transformers 5.24、torch 2.8 cu128）、E194/E197 的逐条目输出。
- **fvcrc13 `/tmp/xiang_hyb/`：** Granite 一对、E195 的输出。
- **fvcrc10 `/tmp/xiang_hyb/`：** Falcon-Mamba、Qwen 一对；E196 的输出在 fvcrc10 的 `/tmp/xiang_e194/out196/`。
- **fvcrc21：** Qwen3.5 与 E198 的输出。
- 检查点都可用 `scripts/dl_hf.sh` 或 `e194_download.sh` 重下（有 sha256 校验）。用完按 compute-policy 删除。
