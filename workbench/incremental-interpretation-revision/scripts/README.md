# 本地复现入口

原始数据、规范化 stimuli、完整 prompt、权重和逐条 prediction 留在 `/data1/xiangding/work/incremental-interpretation-revision/`。固定上游 revision 和 SHA256 见 `../results/D0-source-audit.json`；所有 loader 先核验 hash。复用 `/data1/xiangding/env/pragmatic-inference-calibration/`，torch 2.7.1+cu126、transformers 4.51.3。新任务不恢复已关闭的旧项目。

当前E52入口（旧实验命令只供历史复现）：

```bash
source workbench/incremental-interpretation-revision/scripts/env.sh
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/data_v2.py --out "$IIR_CACHE/E52/published-v2.jsonl"
"$IIR_PYTHON" -u workbench/incremental-interpretation-revision/scripts/step_gp_audit.py --data "$IIR_CACHE/E52/published-v2.jsonl" --out "$IIR_CACHE/E52/step-full-v4" --workers 4 --batch-size 2
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/analyze_reading_map.py --data "$IIR_CACHE/E52/published-v2.jsonl" --annotation "$IIR_CACHE/E52/step-full-v4/annotated.jsonl" --out "$IIR_CACHE/E52/qualified-v2.jsonl"
"$IIR_PYTHON" -u workbench/incremental-interpretation-revision/scripts/run_panel.py --data "$IIR_CACHE/E52/qualified-v2.jsonl" --stage map
```

实际自主执行将地图分为不依赖标签的`map-unlabelled`和完成双遍位置审计后的`landmarks`，按完整task key合并；已有输出不能覆盖，完整地图与分片不能同时重复运行。`download_panel.py`只下载ModelScope镜像的逐文件固定revision/size/SHA256；推理`local_files_only=True`且HF离线，环境HF_ENDPOINT为hf-mirror.com。`step_gp_audit.py`只允许step-5-preview/Step Plan，0600仓库外密钥；单批≤5、共享并发≤8，两个打乱pass及第三遍裁决原包全留。`import_step_pass2.py`在主pass2开始前盲导入另四并发的独立pass2；API schema失败保留、429只做传输退避。运行参数和限制见E52卡，不能把CLI历史重试误作新协议。

`thinking_map.py`/`run_panel.py --stage thinking`使用隔离的`/data1/xiangding/env/iir-e52-generation/`（vLLM0.9.2、torch2.7.0+cu126、transformers4.51.3），原评分环境不改；安装只走PyPI清华镜像，TMPDIR/PIP_CACHE_DIR在外部E52数据盘。固定完整输出与最后think闭合后的答案，R0-generation做匹配控制，cap/未知另报。`audit_reading_fillers.py`独立T3两遍；分析`--filler-audits`强制核验R3输入。`disambiguator_surprisal.py`采用词尾空白质量校正，raw/WT都存；`balanced_map.py`只计算固定面板均衡macro，`mixed_reading_map.py`的VB区间不是主bootstrap CI。全部详细协议/修订时点见E52卡，尚无新能力主张。

增量filler审计用`audit_reading_fillers.py --previous-audits <所有已完成目录>`，分析时`--filler-audits`同时传入原/增量目录，不重复选择标签。`analyze_reading_map.py --deduplicate`另写输入字节去重敏感性；主分析连接共享GP句的既有cluster。完整prompt的R3/R1长度不等记排除；分析同时输出小字段的外部validated-task ledger。补充模型用`mixed_reading_map.py --data <qualified> --map-summary <主分析json> --out <json>`，沿用全部质量排除，区间仍是VB posterior近似而非bootstrap。

E53：`paraphrase_map.py --data <published-v2> --build-out <E53/sentences.jsonl>`合并相同原句；`run_panel.py --stage paraphrase --data <sentences> --models Qwen3-8B gemma-3-12b-it Meta-Llama-3.1-8B-Instruct --calibration-out <E52/runs> --out <E53/runs>`用共享GPU锁生成。`audit_paraphrases.py --data <sentences> --runs <完成目录...> --out <audit> --previous-audits <此前完成目录...>`只给source/output、相同文本盲复用。`analyze_paraphrases.py --metadata <qualified> --data <sentences> --runs <完成目录...> --audits <全部不重复audit目录...> --out <json>`要求每个final都有审计记录；未知/失败不当语义误读，T4与两句格式分开。仪器`--source-limit 5 --blocking-slot 0`不用于科学效应筛选。

```bash
source workbench/incremental-interpretation-revision/scripts/env.sh
# git download 必须沿用上述无代理环境，并禁用 git 自有 proxy 设置。
git -c http.proxy= clone https://github.com/samsam3232/comparing_humans_llms_processing_difficulties "$IIR_CACHE/upstream/amouyal"
git -C "$IIR_CACHE/upstream/amouyal" checkout 072efefa01cb9716c2d14752eb1d4bf9830b0b81
# Jurayj / Microsoft 同样按 data.py SOURCES 的 URL / revision 下载；Microsoft 可 sparse checkout。
python3 workbench/incremental-interpretation-revision/scripts/data.py --audit-out workbench/incremental-interpretation-revision/results/D0-source-audit.json
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/download_hf.py --repo Qwen/Qwen3-8B --revision b968826d9c46dd6066d109eabc6255188de91218 --out "$IIR_CACHE/models/Qwen3-8B"
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/verify_hf_mirror.py
CUDA_VISIBLE_DEVICES=0 "$IIR_PYTHON" -u workbench/incremental-interpretation-revision/scripts/infer.py --experiment E00 --out "$IIR_CACHE/runs/E00"
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/analyze.py "$IIR_CACHE/runs/E00/predictions.jsonl" --out workbench/incremental-interpretation-revision/results/E00-summary.json
```

schema 含 DATA_PLAN 全部字段。未标注 ambiguity position、无上游 comprehension gold 时使用 null，不从结果倒填；另保留 pair_id、upstream 条件与 row ID。位置定义为 0-based whitespace word index，tokenizer-specific positions 在推理资产中另记。bootstrap 的独立单位是 lexical set，不是 prompt/question/condition 行。

`infer.py` 保留 upstream Yes/No vocab variant 聚合，但用 FP32 softmax，保存两类 choice mass、greedy token、全部 prompt hash。不把归一化的 P(correct) 等同于模型自然输出概率。

后续诊断运行：`infer.py --experiment E03/E04/E05/E06 --dtype float32 --out 新目录`；E04 指定 `--model "$IIR_CACHE/models/Qwen3-1.7B"`。1.7B 用 `download_hf.py --repo Qwen/Qwen3-1.7B --revision 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e --out "$IIR_CACHE/models/Qwen3-1.7B"` 获取。下载直接请求镜像并 `trust_env=False`；已有正确文件按 hash 跳过，不重复下载。

[共享 JSON Schema](schema.json) 与 `data.validate_record` 对齐；系统 Python 已有 jsonschema，可对 cache JSONL 逐条校验，无需向推理 venv 安装包。完整校验见 `../results/D0-schema-validation.json`。构造 Jurayj 时 `stimuli.py` 比较全部626句与固定上游 generator；疑似原句/语义问题保留在 ledger。2026-10-05最新用户授权opencode免费模型/Step逐句逐题独立标注，必要时GPT Luna子agent复核，不由主执行agent自判语义gold；旧Ling advisory与历史agent flags保留作provenance，不作为E01筛选规则。

E01已注册；用户明确取消以calibration为停步gate，按系统测量继续。E06只使用自然Amouyal原句校准角色与事件读数，衍生552条QA在本地 `normalized/E06-attachment.jsonl`，旧结果和标签不修改。

E01独立审计与推理入口（先核对实际返回完整，再批量）：
```bash
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/step_audit.py --workers 4
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/adopt_step_audit.py
CUDA_VISIBLE_DEVICES=0 "$IIR_PYTHON" -u workbench/incremental-interpretation-revision/scripts/infer.py --experiment E01 --data "$IIR_CACHE/normalized/jurayj-step5.jsonl" --dtype float32 --system-frame neutral --families NPZ --out "$IIR_CACHE/runs/E01-neutral-NPZ"
```
密钥读取仓库外0600文件或环境变量；HTTP显式`trust_env=False`，请求/响应hash、finish reason与ID完整覆盖记录在cache。实际API限流返回account concurrency=5，客户端默认4且绝不超过用户指定8；截断/timeout不算完成，不用相同截断参数盲重试。`adopt_step_audit.py`机械核对版本/覆盖并应用Step标签；全部诊断题保留null gold。`revision_map.py`保存contrast实际pair intersection和CI，role/semantic分开报告。


E13原两句question-free likelihood（24源组/96作者变体）：

```bash
source workbench/incremental-interpretation-revision/scripts/env.sh
CUDA_VISIBLE_DEVICES=0 "$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/followup_probability.py run --out "$IIR_CACHE/runs/E13"
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/followup_probability.py analyze "$IIR_CACHE/runs/E13" --out workbench/incremental-interpretation-revision/results/E13-summary.json
```

原text与逐词分数仅cache；公开摘要按24 source-set配对bootstrap。第一源词无前文，整词不评分；S2全部词均有前文。首batch以library masked-label loss独立校对S2 shift/indexing，不把surprisal解释为语义gold。


E32/E33事实词序及动作迁移（所有材料先独立逐条审计）：

```bash
source workbench/incremental-interpretation-revision/scripts/env.sh
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/role_fact_transfer_order.py analyze --new "$IIR_CACHE/runs/E32-probability" --out workbench/incremental-interpretation-revision/results/E32-summary.json
"$IIR_PYTHON" workbench/incremental-interpretation-revision/scripts/action_paraphrase_transfer.py analyze --new "$IIR_CACHE/runs/E33-probability" --out workbench/incremental-interpretation-revision/results/E33-summary.json
```

build/adopt入口见各脚本与实验卡。E33字段v1/v2与原材料均cache-only，固定字段hash见D0-E33审计。E29/E31/E32父分数原样复用；E33独立action-clear8与自然/parent交集7/6在推理前定义，所有variant含related都评分。Qwen3-8B冻结FP32，本地cache、原venv、无任何训练或representation probe；网络先source上述环境去掉所有代理。
