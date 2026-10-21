# 矿区D资产与复现入口（2026-10-22）

完整第三方数据、权重、原文和大raw位于本机NVMe：`/var/tmp/ssn-game-npc-d/`。Git仅保留源hash/样本ID、轻量读数、代码和中文报告。父workbench保持一个ACTIVE-MAIN；B/I01暂停，矿区A不执行。

| 资产 | 固定版本 | 位置与本轮状态 |
|---|---|---|
| ArcANE代码 | `46ee34a73c7bd006ba52a7a262586f02301cdb6f` | `vendor/ArcANE`；原生Trial/context/prompt及judge模板用于D-E01/D-E03 |
| ArcANE正式公开benchmark | 随该Git revision | 实际18作品、80个有probe人物、494轴、4282 probes、13438 phase单元；9个空轴文件单列。论文Harry Potter部分未公开，不补造。详见[清单](results/assets_inventory.json) |
| ArcANE-Data训练配置 | `6076de00429ca293b6738f571196ad1264e9a433` | `data/ArcANE-Data`；完整SFT/DPO/RL parquet。与正式benchmark分开；公开10小说子集与发布权重历史12小说训练池分开 |
| ArcANE-8B-DPO | `67b9bea604bea65a5245928ed87103545814b4f7` | `models/ArcANE-8B-DPO`；完整merged权重已下载并实际推理 |
| PHASE-Tree代码 | `0be378fd23c49915255406d881f2389b46b608b8` | `vendor/PHASE-Tree`；四种文本输入使用原生prompt，状态/门控源码已核查 |
| LongEvoRoleBench | `ce09fb68439963c71c3035ee2918c21ae02a3cbc` | `data/LongEvoRoleBench`；四长程语料全部processed资产约7.14GB，含六文本变体、原始时间元数据、中间状态及演化档案；无短程全量跑分 |
| PHASE参数模型资产 | `db2aa3b516a1d78650ffd3f01ef14dcb8f6ea8b4` | `models/phase_tree_models`；下载状态以HF缓存为准，本轮文本路径不依赖、不声称已跑参数适配 |
| Qwen3-8B | `b968826d9c46dd6066d109eabc6255188de91218` | 复用本机HF缓存；D-E01/D-E03角色生成 |
| Qwen2.5-7B-Instruct | `a09a35458c702b33eeacc393d103063234e8bc28` | 复用本机HF缓存；D-E02原生backbone |
| Qwen3-32B | `9216db5781bf21249d130ec9da846c4624c16137` | 已从本机固定缓存复制到`models/Qwen3-32B`；普通章节摘要与本地PHASE评委，非角色模型新增比较行 |

目录关系：`data/arcane_D-E01/`存205个phase的原生任务/独立参考；`data/phase_D-E02/`存64问题四变体与独立评委参考；`data/arcane_D-E03/`存固定嵌套25probe/81phase及242章摘要教师任务。实际prompt/raw/token IDs在`runs/D-E0*/`，运行stdout在`logs/`。metadata/source快照保存每次调用配置，章节摘要与原文不入本仓库Git。

公开ArcANE存量判分的四作品主表与两部lowpop表已由官方脚本离线复算，放`logs/official_*_reaggregated.{json,txt,tex}`；这是历史输出重聚合，不是新模型实测。我们新judge使用Step5低推理档固定量表，须和论文原DeepSeek评委分开；PHASE本地judge为Qwen3-32B，须和原GPT-4.1分开。没有未授权OpenAI/DeepSeek/embedding调用。

## 获取与许可身份

- 代码来源：[ArcANE](https://github.com/holi-lab/ArcANE)、[PHASE-Tree](https://github.com/MemTensor/PHASE-Tree)。用`git clone`后checkout表中完整revision。
- 数据/权重：使用Hugging Face `snapshot_download(repo_id, revision=完整hash, repo_type='dataset'或省略, local_dir=资产目录)`。LongEvo本轮仅选`processed/{Friends,TheOffice,HPD,StarTrek_TNG}/**`；其余数据未下载不假称全量完成。
- ArcANE小说：官方`arc_construction.download_novels`的Gutenberg edition ID；镜像延迟时使用同eBook编号的官方www.gutenberg.org/cache/epub文本，核验eBook ID与起止标记。`data/novels/`及`results/arc_extraction/*/chapters/`均仅在vendor缓存中。
- 许可按资产分别记录：ArcANE代码MIT，repo benchmark `LICENSE-DATA`为CC BY 4.0；HF训练卡标MIT；ArcANE模型Apache-2.0；PHASE代码MIT、LongEvo卡CC-BY-NC-4.0，原语料出处仍单独存在。没有把代码许可当全部影视/小说数据许可。

## 环境与运行

现有推理解释器：`/home/xiang/miniconda3/envs/openslime/bin/python`（PyTorch 2.9.1+cu129、Transformers 5.3.0，依赖见各run metadata）。系统`python3`仅用于stdlib脚本与Step HTTP transport；导入官方ArcANE需要该现有环境的dotenv/openai等依赖。

D-E01角色生成以原生prompt为准，由`scripts/run_local_arcane.py`写官方兼容记录；D-E02/Summary教师与本地judge由`scripts/run_local_text.py`保存完整raw和token IDs。`queue_summary_actors.py`只按依赖完成状态推进；`queue_judges.py`顺序执行已登记的评分与统一技术恢复，密钥只在进程内存/子进程环境，不写文件。

离线复算：`scripts/summarize_results.py --asset-root /var/tmp/ssn-game-npc-d --experiment D-E01|D-E02|D-E03 --out 输出.json`。它取每个judge_id的首个合法分数，保留全部失败尝试计数；D-E03明确复用同一嵌套样本上的D-E01参照，不重复计为新调用。
