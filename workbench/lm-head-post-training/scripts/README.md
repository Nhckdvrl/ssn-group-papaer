# scripts/ 索引

脚本放在同一层，因为它们共用 `models.py`（模型登记）、`verifier.py`（答案判分）和 `e04_generate.render`（评测模板）。文件名前缀是**最早引入它的实验**；后来的实验复用时不改名，复用关系见下表。所有脚本在计算节点上通过 `run_node.sh`（transformers 环境）或 `run_vllm.sh`（vLLM 环境）运行，大文件写到节点本地 `/tmp/xiang_lmhead/`，进 git 的只有 `results/` 下的汇总。

## 公共

| 文件 | 作用 |
|---|---|
| `models.py` | 模型与谱系对登记（`MODELS`、`PAIRS`），权重路径 `/tmp/xiang_lmhead/models/` |
| `verifier.py` | 取最后一个 `\boxed{}` 或 “Answer:” 行，字符串规范化 + 数值比较 |
| `build_inputs.py` | 固定输入集：E01 文本、E02 题目、`--export-math500`、`--export-e02`、`--export-hard`（E07 的 `math_l5`、`olymp`，清单 `data/e07_problems.json`） |
| `run_node.sh` / `run_vllm.sh` | 节点运行器：指定 GPU 与日志名，设置环境变量 |
| `fetch_ranges.py` / `verify_models.py` | 分段并行下载 safetensors 并按 HF sha256 校验 |

## LM Head 阶段（E01–E02）

| 文件 | 实验 | 作用 |
|---|---|---|
| `lmhead_geom.py` / `test_geom.py` | E01、E02 | 头部几何（列空间投影、增益、杠杆、主角）与 23 项对照测试 |
| `e01_weights.py` / `e01_function.py` | E01 | 相邻 checkpoint 的权重解剖；固定输入上的 logit 变化三项分解 |
| `e01_vs_adam.py` | E01（I04） | 真实头部逐行位移与模拟 Adam 预测的比较 |
| `e02_rollout.py` / `e02_geometry.py` / `e02_headadam.py` | E02 | on-policy rollout；回放梯度几何；头部 AdamW 模拟（E02b） |
| `chain_e02.sh` / `summarize.py` | E02 | 单卡串起 E02 三步；E01/E02 结果打印成表 |

## 输出行为阶段（E04–E07）

| 文件 | 用于 | 作用 |
|---|---|---|
| `e04_fit.py` / `summarize_e04.py` | E04-A | 拟合全局仿射成分 τ·z₀+b 与跨来源迁移 |
| `e04_local_tau.py` / `e04_forks.py` / `e04_tail.py` | E04-A2/A3/A4 | 按熵分桶的逐位置温度、分叉处改选内容、尾部质量 |
| `e04_mcq.py` | E04-C | 选择题：全局字母先验 vs 题内区分 |
| `e04_generate.py` + `e04_biasproc.py` | E04-B，E07 锚点 | vLLM 生成（温度、top-p、min-p、全局偏置、熵门控、强制开头）；`--prompts` 可为题集路径，`--out_dir` 指定输出 |
| `e04_gen_summary.py` | E04-B | 生成运行的准确率、格式、风格读数 |
| `e04_hybrid.py` | E04-D、E06、E07 | **两模型同步解码**：在指定位置由另一个模型或另一种取法决定下一 token。模式见文件头（E04-D/E06 的采样/众数/截尾模式，E07 的 `greedy_*` 与 `t_*` 模式）；`--problems`、`--subset_n`、`--sort_by`（按锚点长度排序成批）、`--shard i/n`、`--force_prefix`、周期性重复即停 |
| `e04_hybrid_summary.py` | E04-D、E06 | 同步解码条件的准确率与按题配对差 → `results/e04/hybrid_qwen.json` |
| `e05_extract_forks.py` / `e05_rollout.py` / `e05_analyze.py` | E05 | 抽取改选分叉；对每个候选 token 做 K 次续写（父或子模型）；价值差与相关 |
| `e07_summary.py` | E07 | 网格条件 + vLLM 锚点 → 选择效应、去随机化、低熵纠正、按 Base 解题率分层、换词内容 → `results/e07/summary_<pair>.json` |
