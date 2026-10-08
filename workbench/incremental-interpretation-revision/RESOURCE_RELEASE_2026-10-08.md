# 资源释放与资产入口（2026-10-08）

**08:19 已提前停用本工作GPU并删完剩余模型权重。** 整个本用户目录实测约38GiB，当前项目约17GiB。08:55持久timer实际运行并成功退出，09:00:04/24检查无占卡；09:01:42完整实核0本用户GPU/0本工作queue、17目录0权重，见[核验摘要](results/resource-release-20261008-summary.json)。他人进程不在释放范围。E107标注已完整结束，本次仅CPU整理，无API在途请求。

- 本项目根目录：`/data1/xiangding/work/incremental-interpretation-revision/`。
- 今日剩余6模型38个权重文件删除190652941768bytes（177.5594GiB）；清单 `model-weight-release-inventory.json`，SHA `dcefbcbd20f5fbf4c5e050225b43b82d624340c0cee43a147d910959e94983d7`。
- 4个旧下载残片删除3554672640bytes（3.3105GiB）；清单 `abandoned-model-download-release-20261008.json`，SHA `6c311ca68b6ef5cd0ca703ed0e77ceb463824a9c67ef75a2f2b8af19b0d8cdb7`。
- 此前11个完成实验模型权重294.97GiB及安装/下载缓存已释放，历史清单 `cleanup-unused-models-20261007.json`、`cleanup-20261007.json`、`cleanup-pip-http-20261008.json`等保留。不能把历史manifest理解为权重当前仍在。
- 17个模型目录均0权重；tokenizer/config/revision/下载hash全部保留。当前可用性 `asset-availability-after-cleanup-v2.json`，SHA `dd2ed8ecf437eb87d24ee297316e67c19a8bba496f532dc3b74a55b14538e4a4`，原可用性快照不覆盖。
- 当前95个外置结果map文件的路径/大小/SHA索引 `retained-result-index-after-weight-release-v1.json`，SHA `1c8d3dd30b2b2a93244132d067daf83fbbb5cf0dfd3b0a033f48b99a2b6caf87`。这是已存在文件清单，包含历史/interim，并非95个独立完整结论；完成状态以各实验卡/complete标记为准。
- 科学原始数据、生成输出、逐token LP、输入/配置、Step请求/响应、全部失败/勘误/终图、论文缓存均保留。大头为E52约6.2GiB、E64约4.7GiB；未为节省空间删除科学证据。
- 执行环境合计约14GiB保留，当前轻量环境依赖原研究环境的`.pth`，避免误删依赖。HF cache约20MiB、pip cache4KiB；没有继续下载模型。

`GPU_RELEASE_REQUESTED.json`已08:19写入，runner拒绝重新占卡；持久服务为`ssn-iir-release-20261008.timer/service`，本地helper `gpu_deadline_release_v1.py`。今后需人重新授权GPU并更新截止规则，恢复权重只能走国内HF镜像；入口见[scripts/download_current_models.py](scripts/download_current_models.py)、[scripts/download_panel.py](scripts/download_panel.py)，不直连HF。当前CPU结果分析无需权重。

仓库保持原注册/证据等级，不改线状态。最新入口为[探索总结](EXPLORATION_SUMMARY.md)、[逐次方向与结果](EXPLORATION_RECORD.md)、[E107](experiments/E107-critical-dependency-commitment-audit.md)完整终图与[摘要](results/E107-critical-dependency-summary.json)。E108仅准备；资源释放与档案收尾不等于找题任务完成。
