# E14 — 删除监督量约束后的来源配方补货（2026-10-03，跑前）

- **状态：** RUNNING（两队列已启动；init已真实训练，used修复启动前清单schema后按原seed接续）；E13尚无六支终点/评分，本卡及采样规则在看到E13结果前冻结。
- **类型：** EXPLORE；强简单竞争baseline，不是新框架或新的资格门。
- **对应：** P03（简单静态成功）、P06（避免把局部细化当选题）；I01相关动作，不预设C01/C02、workbench/idea状态不变。
- **问题（一句话）：** 去掉exact监督量匹配、仅保留旧策展集的来源配方，能否成为同预算下更简单而有用的实际补货行动？

## 为什么现在运行

E13检验replay/池内部分补货/池外source×exact n补货。其成功可能只需source配比；其失败也可能是限制性抽样造成，而不是廉价配方不可行。现在预写并增加两条source-only训练，能同时改变这两种解释，避免看分数后挑替代baseline。P05已经做简单配比、同配比不同draw及forward-loss过滤；P54已有强random/组件/预算/池依赖。我们不占有“简单配方强”，只测学习后实际补货是否还值得保留策展资格。全文及实现边界见P05/P21/P54论文卡。

## 设置：一个新数据动作，两个父状态

1. **父状态**：复用E13 init论文父模型与used=E12 icons_exact_s17完整625步终点；精确revision/权重hash/E12 launch及completion沿用，不以E13输出选择父模型。optimizer/moments、step counter、scheduler全部重置。
2. **新动作source_only_fresh**：S=E12冻结ICONS公开池10K子集。保留S逐slot的source，但不保留n。COCO/GQA/OCR-VQA/VG/TextVQA/text-only计数分别为6460/1589/1028/755/85/83；这是S配方，**不是**E12五视觉源均衡。从公开ICONS池外按source随机无放回抽样，排除S完整记录及S所有原image路径；全10K fresh，完整key去重，不改答案。slot来源和seed29的sampler permutation与E13一致。
3. **随机性**：sampling/train/data seed均29，抽样用固定`E14|29|source_only_fresh` salt，与训练RNG独立。只跑init/used两支，共一个paired训练seed；不筛seed。记录selected positions/full-record SHA、源计数、label向量和文件SHA，CPU物化后即冻结。
4. **训练契约**：Curation-Bench SHA24eea1526492c00cee421f5db0793789e00aabb2；同E12/E13单A100、LM/projector全参、vision冻结、BF16、2048、assistant-only、batch1×GA16、1epoch/625步、LR2e-5/cosine/warmup.03/零decay/fusedAdamW。使用原trainer，不改loss。实际每窗sum CE/N中的N按本动作标签计，不硬填E13的549,353。读取同EOS processor并记录真实label/input tokens、图像数、truncation、每source剂量和实际625窗口。
5. **边界明确**：本动作不保留E13的46旧anchors（旧标签6.026%，text-only源约54.92%），监督量/窗口权重/内容支持均可能变。这是部署行动比较，**不是label length单因素因果实验**；不追加anchor/token对齐GPU。排image path非pixel-dedup。父状态历史预算是所测状态，used总分不能归于刷新。
6. **底座复用**：E13已冻结全池metadata与E12全量Arrow/JSON审计、双父processor、sampler、同八任务污染审计入口。只核新subset身份/新标签向量与污染，不再重做665K审计、不新建环境；fvcrc12优先用两张空闲A100，不抢他人。大文件节点本地`/var/tmp/xiang-data-rsi/e14/`，小manifest入git。

## 读数与决策

- **读数：**E12/E13固定八项规范化均值及完整任务向量；primary每状态`source_only_fresh−fresh_law`，并与fresh_selected/replay的真实终点效用比较。报告相对父增益和完整动作/训练/评价成本。10K/625步一致不等于监督token或FLOPs一致；不以TF-IDF/teacher正确率/loss分数代替学习收益。
- **阳性对照：**E12 init→random+3.343分已成立，E13六支是同时运行的共享真实训练对照。runtime observer逐行n/每窗N核实际自有剂量，不能把单个首窗当625步完成。
- **噪声地板 + MIE：**E12同checkpoint唯一复跑差−.0519，只是一例节点/推理/judge变化；本地训练SD/CI未知。约1平均分或完整任务变化足以改变部署行动时优先追进，非自动裁决。一个paired seed的null不证明等价，不把任务/题目当独立训练重复。
- **混杂审计：**parent/optimizer reset/LR/steps/EOS/template/data_seed/terminal eval已控制；slot来源保持。n/数据内容/旧anchor曝光/图像复用/CPU-I/O和前向代价是新实际行动的组成或未控制变量，完整报告。八公共任务已有观察，非private；后续策略泛化需独立新task/learner/episode。只取预定终点，不用test挑checkpoint。
- **决策表（跑之前写）：**
  - source-only与law保住池内完整效用 → 不再细化exact-n；下一项问最简单来源配方在新记录/学生上是否可部署，与强均衡及免费池复用比较，不造router。
  - law输但source-only救回 → 不把law失败归成廉价规律无效；研究整套限制性抽样的行动损失，内容/曝光/anchors等仍是竞争解释，仅有稳定决策后果才追。
  - source-only/law均有实质损失而fresh-selected保留收益 → 内容资格有未被吸收的效用；转现成forward-loss/noise-filter等最低必要内容信息，非继续matching或立刻建全梯度库。
  - 仅used出现有后果的排序分歧 → 再确认必要状态信息与seed稳定性，不凭单矩阵升级C01。
  - 差很小/不改变动作 → 保留null，结束本轮补货分解，转其他高收益问题；不据此关闭领域/工作线。
- **算力预算：**两成功SFT约2–3 A100h、八任务评价约1h；总分配上限8 A100h含前检/导入/失败，judge增量Blackwell单列上限4h，API0。CPU物化/搬运/墙钟分别记。与E13独立ledger，不把预算等同实际。

## 结果（执行后追加，不回改跑前设计）

- **CPU动作已冻结**：[采样/剂量结果](../results/E14_cpu_source_only_summary.json)、[节点搬运](../results/E14_data_staging_manifest.json)，脚本39b709e/SHA1d631c48…；全10K fresh、旧完整key/旧image path/ICONS成员交集0、source slot一致、anchors0。实际监督量1,078,803（E13的1.96377倍）、input8,190,604、unique images9,674、zero labels0、truncated10/no末EOS9；不从token比推线性更新强度。与E13 fresh-law交254记录/694图像路径，允许并报告，未用于筛选。八任务污染clean/无跳项是原阈值语义，非零匹配。CPU82.194s，11文件1,483,944,780 bytes唯一copy22.531s，全source/target SHA一致；manifest SHA b649fa16fd8954caa1e90884407b257dc47b5b1ebf1ff08b1867412cb626664d。12节点路径`/var/tmp/xiang-data-rsi/e14/subsets/source_only_fresh/`。
- **CPU launcher核对**：[小证据](../results/E14_CPU_launch_summary.json)，复用E13冻结read-only observer而不改其globals。双父11row processor与seed29 sampler核对通过；自有625窗口监督量和1,078,803，首窗1,553/min601/max4,011，均非零。此为CPU预期，不是GPU实测。预算watch经独立只读审查修复自有orphan/等待队列的cap退出漏洞；未加防御GPU测试。
- 两支训练终点/八项效用/CI：待运行，训练方差未知。
- 主张变化：C01–C04仍L0；该卡不是科学结果。
- POST-HOC分析：尚无。

- **启动前失败与修复（17:25UTC，效用未观察）**：used首次CPU前检37.934s以rc1退出，尚未创建run_dir/训练窗口。错误是E13 staging清单用`name`、运行清单用`path`，直接dict比较误报父模型变化；独立实读15文件bytes/SHA全部一致。原launcher与init运行保持冻结，新增v2只规范filename key、不减弱内容校验。按同父/同动作/同seed29接续；旧stderr/queue尝试及37.934s成本全部保留，预算watch覆盖追加尝试。不是训练null、seed筛选或科研反证。

- **实际训练与评价接续**：[首窗口证据](../results/E14_first_runtime_windows.json)记录init实测59窗口，首N=1,553，所有已观察microbatch n/窗口N与CPU预期对应，seed/optimizer reset/GA/原loss均实测成立；59窗口不等于625终点。used v2启动与原失败见[恢复溯源](../results/E14_used_preflight_recovery.json)。[评价driver](../results/E14_eval_launch_provenance.json)在fvcrc12 PID1456317/ticks1819280067等双625终点，源码00862a288c…；[现成环境核对](../results/E14_eval_environment_preflight.json)已通过。独立fvcrc20 GPU3/8033复用E12同judge/checkpoint/配置，真实build0.23.0+cu129记录；新物理卡/port为部署偏离，judge尚未启动，已有他人进程则等待idle。终点本地使用、copy0，judge4h单列守护；旧waiting driver启动条件修复的原档案保留，未运行评价或挑checkpoint。

- **双父真实训练已成立（17:46:36UTC）**：init/used实读158/67窗口，均有runtime、尚无completion。两卡约54.8GB，自有actual n/N与预期对应；used恢复已过全部父/数据/包/processor前检。此为运行进度，不是training utility。
