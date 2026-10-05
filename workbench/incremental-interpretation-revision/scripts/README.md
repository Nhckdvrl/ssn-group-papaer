# 本地复现入口

原始数据、规范化 stimuli、完整 prompt、权重和逐条 prediction 留在 `/data1/xiangding/work/incremental-interpretation-revision/`。固定上游 revision 和 SHA256 见 `../results/D0-source-audit.json`；所有 loader 先核验 hash。复用 `/data1/xiangding/env/pragmatic-inference-calibration/`，torch 2.7.1+cu126、transformers 4.51.3。新任务不恢复已关闭的旧项目。

```bash
source workbench/incremental-interpretation-revision/scripts/env.sh
# git download 必须沿用上述无代理环境，并禁用 git 自有 proxy 设置。
git -c http.proxy= clone https://github.com/samsam3232/comparing_humans_llms_processing_difficulties "$IIR_CACHE/upstream/amouyal"
git -C "$IIR_CACHE/upstream/amouyal" checkout 072efefa01cb9716c2d14752eb1d4bf9830b0b81
# Jurayj / Microsoft 同样按 data.py SOURCES 的 URL / revision 下载；Microsoft 可 sparse checkout。
python3 workbench/incremental-interpretation-revision/scripts/data.py --audit-out workbench/incremental-interpretation-revision/results/D0-source-audit.json
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/download_model.py
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/verify_hf_mirror.py
CUDA_VISIBLE_DEVICES=0 "$IIR_PYTHON" -u workbench/incremental-interpretation-revision/scripts/infer.py --experiment E00 --out "$IIR_CACHE/runs/E00"
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/analyze.py "$IIR_CACHE/runs/E00/predictions.jsonl" --out workbench/incremental-interpretation-revision/results/E00-summary.json
```

schema 含 DATA_PLAN 全部字段。未标注 ambiguity position、无上游 comprehension gold 时使用 null，不从结果倒填；另保留 pair_id、upstream 条件与 row ID。位置定义为 0-based whitespace word index，tokenizer-specific positions 在推理资产中另记。bootstrap 的独立单位是 lexical set，不是 prompt/question/condition 行。

`infer.py` 保留 upstream Yes/No vocab variant 聚合，但用 FP32 softmax，保存两类 choice mass、greedy token、全部 prompt hash。不把归一化的 P(correct) 等同于模型自然输出概率。
