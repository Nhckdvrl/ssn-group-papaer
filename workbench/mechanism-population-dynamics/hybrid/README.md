# hybrid：混合架构（循环层 + 少量全注意力层）里的分工

**状态（2026-11-23）：**
- 探索子线，刚开。
- 只有一张试测卡 [E194](experiments/E194-olmo-hybrid-word-assembly-pilot.md)，状态 PLANNED，**等人签字后才跑**。没有下载，没有结果，没有主张。
- workbench 在登记表里的状态仍是 PROPOSED。正式的 ACTIVE-EXPLORE 名额目前由 in-context-evidence-structure 占着，要不要调整由人决定（R2/R7）。

## 问题
混合模型里，被切成几个 token 的词，在哪一层被拼回一个词？这一步是由循环层完成，还是要等到第一个全注意力层？

## 为什么问这个
- 11-22 起，division 的原问题"独立训练是否形成相同分工"不再作主问题：头分工线 10 月已答过同类问题，结项原因是答不出"所以呢"。
- 用导师的去题目标准筛 Gemini 的方向，方向 3 排第一。全文核查后发现它已被 Bandarkar 2609.35378 做掉。剩下的是几篇 2026 年论文之间的解释缺口，详见核查卡 [`search/sasano-taste/HYBRID_LAYER_ROLES_SCAN_2026-11-22.md`](../../../search/sasano-taste/HYBRID_LAYER_ROLES_SCAN_2026-11-22.md)：
  - Bandarkar：第一个全注意力层有一次跨语言"事件"；混合模型的全注意力层偏向看近处；第一层用全注意力时，非拉丁文字受益最大。
  - Afendulev 2609.04434：循环状态保留部件、丢失绑定。
  - Zeng 2611.01909：最早的循环块换成逐 token 投影后，困惑度 10.6 → 44.7。
- 拼词发生在哪里，可能把这几条串起来。现有的拼词研究（Kaplan ICLR 2025、Feucht EMNLP 2024、Busigin & Pinter 2606.08562）全部只在普通 Transformer 上做过。

## 工具
- **OLMo-Hybrid-7B 与 OLMo-3-7B：**
  - 分词器文件完全相同；
  - 预训练结束的检查点只差 264 步，都用 RoPE θ = 5e5；
  - 唯一的结构差别是 3/4 的层从滑窗注意力换成了 GDN；
  - 两者都有 step0（未训练）和约 1,500 个中间检查点。
- **多语言和锁相检验**留给后续卡：Qwen3.5、Granite-4.0-H（有同配方稠密对照，第一个全注意力层在第 5 层）、Nemotron-H 和 Jamba2（第 7 层）。
