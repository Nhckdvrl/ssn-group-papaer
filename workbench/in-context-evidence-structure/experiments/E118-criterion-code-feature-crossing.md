# E118：判断方面与私人输出约定的正交反事实（2026-10-11）

- **状态：** PLANNED（跑前）
- **类型：** CLAIM / 机制功能区分；不是格式/头细化。
- **对应：** C21/C22、I04、P17；未新增完整criterion主张。
- **问题（一句话）：** 历史另一来源改变A证据时，传入的是那个来源的具体方面→标签关联，还是共同情绪信号/置信强度？
- **为什么现在做：** E117两个家族确认label缓存影响Food和Service，却没有确认答案KV边的方面选择；原生与label干预方向不同，且single A已有Service响应。此前A/B共用全局p，不能区分共同语义增益与独立私人关联。这是解释功能对象的缺口，不是修正阴性结果。
- **设置：** 保留E117自然双方面评论、A按food评价、8条A/8条B/8个未见新评论，FP32/eager/frozen。独立交叉B criterion(food/service)×B private convention(same/opposite A)四世界，A原文/标签/名字和query始终固定。A整体正反约定平衡。仅B评论四组合的双射重配实现四规则，B输出word/stream/位置/Source和评论多重集全部一致，没有直接给B标准。8条B都unique，CPU从词长匹配pool按seed选择，不看输出。词汇同类within对照交换8个B位置、保持原service rule，用于判断普通措辞置换量级。
- **干预：** 4真实world各native/A-only；三个非origin world的A-label KV移入相同recipient（其他缓存固定），native/A-only各测；历史B答案KV仅在A label形成时消费，其他A形成后再移入同recipient，native/A-only各测。另4个far输出形成的A-label donor进入相同shared recipient，测output命名在形成端的作用。所有层/实际answer+separator区域，沿用E114/E117数值实现；不扫head/layer/alpha，不新增训练。
- **读数：** z=yes−no；Food/Service gold按A私人p编码，完整四点bias/F/S/F×S同报。每种接口和B criterion的私人代码反转：Delta_task,feature=mean[z_same−z_opposite]*feature_gold/2。主量J=(Delta_food,F−Delta_food,S+Delta_service,S−Delta_service,F)/2：两个独立criterion是否使代码反转作用跟随对应输入方面。J>0支持task-specific association影响，J≈0而两方面同增支持共同情绪/强度解释；不从边际Service非零推断泄漏。所有Food/Service方向、bias/interaction同时保存，不能挑最好模型/方向。Far-label同J与Shared-label配对报；actual-donor答案KV效果对真实label缓存效果作冻结系数1预测、raw r/RMSE/zero，不拟合新系数。
- **阳性对照：** single A与4种single B（按各自gold评分）、explicit food/no-demo原子、原source-only instruction；完整native实际分块token流/split、自复制≤.001、静态答案layer0 KV差0、pristine source fingerprint/all-layer消费、全部B多重集与A非B token固定。private能力弱结果照报，不把direct阳性代替criterion推断。
- **配置：** Qwen3/Mistral先16 contexts seed118001旧词句；数值有效后原样32 contexts seed118101 validation新词/模板，包括阴性。33条件×8query=4224/8448；confirmation不与探索相同评论字节。Llama不是此次科学结论前提，完成E117后若接口/资源可用按同卡纳入，不按阳性选择。
- **噪声地板 + MIE：** FP32 full/split/self≤.001；context-bootstrap10000 seed910；须同时比较CI与target尺度，弱目标不因r高声称充分。整套full-profile读数跑前冻结，无事后截窗/幸存种子。
- **混杂审计：** B criterion的概念变化用4世界正交于输出约定；标签数和词先验固定，B full-rank原文多重集一致。8全unique要求是CPU设计，非能力/结果筛选；仍是受控合成评论，非真实个人任务。不同criterion并非相同位置都变化，代码反转与within同为8位置；不声称所有置换几何相同。query gate为诊断，不等于原生正确程序。Far-label改变B输出词先验，研究的就是命名形成作用，不能冒称词先验等价。F/R/cache交互不当独立语义模块；J识别功能方面关联，不能定位input filtering、完整抽象程序或唯一路径。
- **决策表（跑之前写）：**

| 结果 | 实际改变的认识 |
|---|---|
| label J在独立材料稳定>0，KV边也重建 | 形成路径传递与特定输入方面关联的私人输出关系，而非仅共同情绪增益 |
| label J>0、答案KV J弱/预测残差大 | label证据有task-specific功能，当前答案子图只覆盖部分形成；不继续细头搜索 |
| label两方面/共同bias改变，但J弱 | 当前影响更符合共同语义/置信变化，不把label灵敏性宣布标准运输 |
| native J明确而gated/label弱 | 区别主要在后续读/用规则；保留旧namespace形成事实，更新功能解释 |
| far降低J而shared保持 | 输出命名改变形成端的task-specific关系共享，非只最终标签选择 |
| single任意B criterion/private弱 | 全部因果margin仍按实测范围报告，不以完整两能力组合失败为前提 |
| 数值或几何失败 | 仅修执行，保存失败与旧版本，不形成科学判断 |

- **算力预算：** 独立单卡并行，Qwen/Mistral每家族≤.35GPU时，使用空卡而非分布式训练。先冻结/预检，后n16→n32；不是扩大数据集或扫标签。
- **论文定位/设计来源：** Cho information removal把共同语义与task-specific功能区分；AddUp Appendix K提醒错误映射仍可产生相近QK对齐，因此不能用广义访问解释具体criterion；Yu/Ananiadou用私人映射反转区分QK/OV。E118的增量候选是独立来源的criterion×code如何影响A已形成证据、并由具体历史消息预测；宽task selection/QK-V/上下文化所有权归已有论文，不自动声称首次。

## 结果（运行后追加）
待CPU/GPU；读数与决策表跑前冻结，源码SHA256：0fa0de9de30171a0815b01206314095864567dc735868a2ed0bd43b2db426c4c。
