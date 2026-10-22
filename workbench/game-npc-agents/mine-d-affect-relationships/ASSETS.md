# 矿区D资产与复现入口（2026-10-22）

导航：[Baseline与复现范围](BASELINES.md) · [脚本职责与离线命令](scripts/README.md) · [结果状态](results/README.md)。本页是来源、环境与仓库外资产的唯一登记入口，不把下载缓存复制进研究仓库。

**2026-10-22源纠正：** D-E03 Monte Summary的14原生单元被本轮适配器误换成117文学章号；原归档保持完整历史，六作品S相关比较暂撤回。正确来源与新结果见[纠正记录](results/D-SOURCE-CORRECTION-2026-10-22.md)。新冻结输入在`data/arcane_D-E07_v2/`，完整旧28编译中断记录也保留；D-E06连续轨迹另在`data/closed_D-E06/`和`runs/D-E06/`。

完整第三方数据、权重、原文和大raw位于本机NVMe：`/var/tmp/ssn-game-npc-d/`。Git仅保留源hash/样本ID、轻量读数、代码和中文报告。父workbench保持一个ACTIVE-MAIN；B/I01暂停，矿区A不执行。

| 资产 | 固定版本 | 位置与本轮状态 |
|---|---|---|
| ArcANE代码 | `46ee34a73c7bd006ba52a7a262586f02301cdb6f` | `vendor/ArcANE`；原生Trial/context/prompt及judge模板用于D-E01/D-E03 |
| ArcANE正式公开benchmark | 随该Git revision | 实际18作品、80个有probe人物、494轴、4282 probes、13438 phase单元；9个空轴文件单列。论文Harry Potter部分未公开，不补造。详见[清单](results/assets_inventory.json) |
| ArcANE-Data训练配置 | `6076de00429ca293b6738f571196ad1264e9a433` | `data/ArcANE-Data`；完整SFT/DPO/RL parquet。与正式benchmark分开；公开10小说子集与发布权重历史12小说训练池分开 |
| ArcANE-8B-DPO | `67b9bea604bea65a5245928ed87103545814b4f7` | `models/ArcANE-8B-DPO`；完整merged权重已下载并实际推理 |
| PHASE-Tree代码 | `0be378fd23c49915255406d881f2389b46b608b8` | `vendor/PHASE-Tree`；四种文本输入使用原生prompt，状态/门控源码已核查 |
| LongEvoRoleBench | `ce09fb68439963c71c3035ee2918c21ae02a3cbc` | `data/LongEvoRoleBench`；四长程语料全部processed资产约7.14GB，含六文本变体、原始时间元数据、中间状态及演化档案；无短程全量跑分 |
| PHASE参数模型资产 | `db2aa3b516a1d78650ffd3f01ef14dcb8f6ea8b4` | `models/phase_tree_models`；两套hypermod约1.8GB已下载；本轮文本路径不依赖，不声称已跑参数适配 |
| Qwen3-8B | `b968826d9c46dd6066d109eabc6255188de91218` | 复用本机HF缓存；D-E01/D-E03角色生成 |
| Qwen2.5-7B-Instruct | `a09a35458c702b33eeacc393d103063234e8bc28` | 复用本机HF缓存；D-E02原生backbone |
| Qwen3-32B | `9216db5781bf21249d130ec9da846c4624c16137` | 已从本机固定缓存复制到`models/Qwen3-32B`；普通章节摘要、统一本地评委与容量参照；D-E04直接状态更新普通模型 |

目录关系：`data/arcane_D-E01/`存205个phase的原生任务/独立参考；`data/phase_D-E02/`存64问题四变体与独立评委参考；`data/arcane_D-E03/`存固定嵌套25probe/81phase及242章摘要教师任务。实际prompt/raw/token IDs在`runs/D-E0*/`，运行stdout在`logs/`。metadata/source快照保存每次调用配置，章节摘要与原文不入本仓库Git。

公开ArcANE存量判分的四作品主表与两部lowpop表已由官方脚本离线复算，放`logs/official_*_reaggregated.{json,txt,tex}`；这是历史输出重聚合，不是新模型实测。Step5 low因实际共享并发9/8限制停止，340正式尝试321合法分数单列，未转现金；D-E01/03正式比较统一用本地Qwen3-32B完整评分，不拼接评委。它与论文原DeepSeek须分开；PHASE同一本地judge与原GPT-4.1须分开。没有未授权OpenAI/DeepSeek/embedding调用。

## 获取与许可身份

- 代码来源：[ArcANE](https://github.com/holi-lab/ArcANE)、[PHASE-Tree](https://github.com/MemTensor/PHASE-Tree)。用`git clone`后checkout表中完整revision。
- 数据/权重：使用Hugging Face `snapshot_download(repo_id, revision=完整hash, repo_type='dataset'或省略, local_dir=资产目录)`。LongEvo本轮仅选`processed/{Friends,TheOffice,HPD,StarTrek_TNG}/**`；其余数据未下载不假称全量完成。
- ArcANE小说：官方`arc_construction.download_novels`的Gutenberg edition ID；镜像延迟时使用同eBook编号的官方www.gutenberg.org/cache/epub文本，核验eBook ID与起止标记。`data/novels/`及`results/arc_extraction/*/chapters/`均仅在vendor缓存中。
- 许可按资产分别记录：ArcANE代码MIT，repo benchmark `LICENSE-DATA`为CC BY 4.0；HF训练卡标MIT；ArcANE模型Apache-2.0；PHASE代码MIT、LongEvo卡CC-BY-NC-4.0，原语料出处仍单独存在。没有把代码许可当全部影视/小说数据许可。

## 环境与运行

现有推理解释器：`/home/xiang/miniconda3/envs/openslime/bin/python`（PyTorch 2.9.1+cu129、Transformers 5.3.0，依赖见各run metadata）。系统`python3`仅用于stdlib脚本与Step HTTP transport；导入官方ArcANE需要该现有环境的dotenv/openai等依赖。

D-E01角色生成以原生prompt为准，由`scripts/run_local_arcane.py`写官方兼容记录；D-E02/Summary教师与本地judge由`scripts/run_local_text.py`保存完整raw和token IDs。`queue_summary_actors.py`只按依赖完成状态推进；`queue_judges.py`的Step队列已因实际限流退出；本地评分使用`queue_local_judges.py`。密钥只在进程内存/子进程环境，不写文件。

离线复算：`scripts/summarize_results.py --asset-root /var/tmp/ssn-game-npc-d --experiment D-E01|D-E02|D-E03 --out 输出.json`。它取每个judge_id的首个合法分数，保留全部失败尝试计数；D-E03明确复用同一嵌套样本上的D-E01参照，不重复计为新调用。

## 直接状态形成参照：EvolvingWorld

官方代码固定`1de26550ccfff105f3ffe9f4b386716446291341`，HF数据固定`ae7d82d38909783805979a8055d5ae913cb982f7`。本轮大文件只下载训练混合文件和character_update单任务文件（约4.55GB），同时保存固定版本dataset card，不称完整世界模拟复现或已取得专用权重。单任务文件删除details，完整文件可恢复作品/角色/场景；两者24,977条conversation hash完全匹配。51部作品、2,671角色，22,306次相邻出场的输入profile/tracker与上次输出逐字相接；6条tracker为dict，按原生f-string存入下一输入。清单见`results/update_provenance_inventory.json`。

D-E04直接使用原生角色更新system/human；完整监督与输出留在`data/update_D-E04/`、`runs/D-E04/`，只将样本ID/hash与轻量结果入Git。这是公开训练资产上的通用模型诊断，非官方held-out rollout。该代码revision未见LICENSE文件，HF数据卡未给标准license标识；卡片正文明确说明非商用学术研究/复现，并列出训练评估用途，再分发细节未另展开。当前仅本地研究运行/读取，无vendor代码或原文再发布。原著出处仍分别核对。

## 本轮完整原始输出的持久归档

主机`fvcrc20`；独立于NVMe临时目录的持久文件：

`/home/xiang/research-assets/game-npc-agents/mine-d/2026-10-22-first-residency/raw-runs-and-frozen-inputs.tar.gz`

实际归档157文件，压缩20.12 MiB、原始105.32 MiB，全部成员逐字节SHA256核验完成，归档对应研究commit为`39e7c575`。校验和、每个成员的路径/字节/hash及归档对应研究commit见[RAW-MANIFEST](results/D-RAW-MANIFEST.json)；[运行总账](results/D-RUN-LEDGER.json)把角色、状态、教师、评委、前向与API分开。[输入与评分来源核验](results/D-INTEGRITY.json)确认同题/仅一句指令、API输入与本地相同、首个完整结果选择、PUF候选与raw hash对应、四文本NLL目标一致。归档不含权重、完整第三方corpus或vendor仓库，不因此改变原资产许可；文件仅限本地研究者访问。

已配置该研究机SSH别名时可下载（亦可替换为实际登录地址）：

```sh
scp fvcrc20:/home/xiang/research-assets/game-npc-agents/mine-d/2026-10-22-first-residency/raw-runs-and-frozen-inputs.tar.gz .
sha256sum raw-runs-and-frozen-inputs.tar.gz
mkdir -p restored-d
tar -xzf raw-runs-and-frozen-inputs.tar.gz -C restored-d
```

`environment.json`保存Python/torch/transformers/CUDA/GPU信息；各run metadata、runner_source、frozen tasks包含实际配置、模型revision、输入与完整输出。HF缓存中的Qwen3-8B/Qwen2.5-7B可按表中revision重新下载。环境恢复后可重播冻结任务，不需要重新抽样/生成故事。Step API没有可固定权重hash，原回包/usage/response_id保留；生成token IDs供应方不提供则明确null，不伪造。

Step5用于D-E01评价的部分/预试与D-E05状态actor分开：前者资源中断、不拼入本地主表；后者65请求/64完整状态、394,805已记录tokens。所有已记录Plan用量及早期最多2个在途未知调用见总账；绝不把未知计为0，也不把API壁钟加到GPU小时。

## 不调用模型的完整复算

下面命令在仓库根目录执行，`/var/tmp/ssn-game-npc-d`可换成解压后的完整资产根；如使用官方后处理，按上表恢复相应固定vendor revision。解释器推荐现有openslime环境。

实际脚本目录为`workbench/game-npc-agents/mine-d-affect-relationships/scripts/`：

- `recompute_arcane.py --asset-root <资产根> --project <仓库根>`：D-E01/D-E03主表、严格轨、跨评委与图，无新模型请求。
- `summarize_results.py --asset-root <资产根> --experiment D-E02 --out <输出>`：LongEvo原生文本内容表；加`--strict-native-json`为严格轨。
- `summarize_likelihood.py --asset-root <资产根> --out <输出>`：原句NLL，256次已保存前向分数复算，无新生成。
- `summarize_updates.py --asset-root <资产根> --out <输出>`：D-E04原生flag主表；加`--condition identity_line`为控制；另加`--plan-run <资产根>/runs/D-E05/step5`为强普通参照。
- `summarize_state_quality.py --asset-root <资产根> --out <输出>`：D-E04原生PUF准则单角色适配；加`--include-plan`给D-E04＋D-E05共同表与同题有效配对。
- `summarize_runs.py --asset-root <资产根> --out <输出>`和`verify_measurement.py --asset-root <资产根> --out <输出>`：总账与来源检查。所有算术从保留raw重建，不以人工改分覆盖原结果。

原生阅读范围、样本来源与许可说明见正文报告及四张权威论文卡；本轮没有跑PHASE参数适配、ArcANE-32B专用权重、EvolvingWorld专用checkpoint或完整多智能体rollout，也没有声称它们已被这些普通单步基线替代。

## 持续实验资产（D-E06–D-E09）

同一NVMe根下，`data/closed_D-E06`保存29轨迹/87后续问题、原句、三更新路径与强消费者冻结输入；`data/arcane_D-E07_v2`保存正确Monte源分片、完整81摘要与人物整理输入；旧`arcane_D-E07`及中断raw保留。`data/arcane_D-E08`复用同81输入，Step5实际82次Plan调用得到81卡，新增317,848记录tokens。`data/prefix_D-E09`为六人物的完整来源前缀、301固定窗口、15 probe/47 phase与查询边界证明。权重沿用上表revision，无新训练。

对应完整原始运行分别在`runs/D-E06`至`runs/D-E09`。D-E06–08推理和离线表已全部完成，D-E09两条完整前缀任务仍在运行；各自metadata区分完成状态，不能将目录存在等同完成。当前首夜持久归档不会被覆盖，持续实验完成后另建归档。

- `recompute_continuation.py --asset-root <根> --project <仓库>`：按依赖完成D-E06三消费者、D-E07修正来源全表及D-E08强教师表与图，仅离线分析。
- `recompute_prefix_results.py --asset-root <根> --project <仓库>`：D-E09全47phase主表，与共同20phase的近期上下文嵌套表分开。
- `collect_continuation_costs.py --asset-root <根> --out <账本> --include-prefix --require-complete`：D-E06–09独立调用账，含Step新增用量；不把API壁钟加入GPU小时，不重复首夜账。
- `archive_runs.py --asset-root <根> --destination <新的持久目录> --manifest <清单> --include-continuation`：所有运行结束且资格检查通过后归档。完整模型输入含实际使用的来源前缀文本，限本地研究保存；原文与权重不进Git。

另外只读取得EvolvingWorld官方六部OOD作品的`extracted_data/scenes`与`character_dynamic`，hash与规模见[D-HELDOUT-SOURCE-INVENTORY](results/D-HELDOUT-SOURCE-INVENTORY.json)；尚未据此声称新实测或所有模型都未见作品。


## 可复用连续经历索引

`data/EvolvingWorld/experience_index.sqlite`是固定4.18GB混合训练文件的只读索引，约28.66MiB，不复制正文。已将138,596条任务的精确UTF-8字节区间、SHA256与作品/角色/场景/任务元数据全部回读核验；51作品、2,671角色条目、22,306相邻出场链接。24,977更新出场均有同出场动机任务，其中19,937有互动生成任务。这是来源可用性，不是新增独立科研样本或已标好的成长真值。

[轻量索引清单](results/D-EXPERIENCE-INDEX.json)记录固定HF revision、原文件hash、索引hash/大小、任务数及核验覆盖；SQLite留在资产目录，不进Git。`experience_store.py`将同一出场的原生任务和同人物下次出场连接；保留未说话角色、无更新样本及原始源划分，不按模型表现挑选。返回的原生conversation包含监督目标，调用方必须把目标和未来记录与当前推理输入分开。

重建与使用：

```sh
python3 workbench/game-npc-agents/mine-d-affect-relationships/scripts/experience_store.py --build --source /var/tmp/ssn-game-npc-d/data/EvolvingWorld/train/all_tasks_with_details.json --index /var/tmp/ssn-game-npc-d/data/EvolvingWorld/experience_index.sqlite --revision ae7d82d38909783805979a8055d5ae913cb982f7 --expected-sha256 2f9dd6b90c7ed6870916cce91fc5d8ec6ac218f3c0ec6a225736c095bf751e07 --verify --out /var/tmp/experience-index-inventory.json
```

已有索引时去掉`--build`，用`--verify`全量核验；重建须选新目标路径，不覆盖已有来源记录。`ExperienceStore.get(row_id)`精确回读一条原任务并校验hash；`appearance(update_id)`返回同出场各任务ID及同人物下次出场ID，不自动构造新训练prompt。此入口供之后不同baseline与学习方案共享，原D-E01–09冻结输入不受影响。
