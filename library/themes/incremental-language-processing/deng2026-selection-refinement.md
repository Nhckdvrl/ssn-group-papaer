# Selection, Reflection and Self-Refinement（ICLR2026）

证据：[作者v1](https://arxiv.org/html/2510.08222v1)完整主文§1–4、AppA/C、B线性高斯推导选段；[正式稿](https://proceedings.iclr.cc/paper_files/paper/2026/file/879d773f3321bcea7fa72b77b069ec5e-Paper-Conference.pdf)§1–4正文核对，新增ARC与成本表，正式AppA1/C/D/E完整、B2推导选段；其余附录未精读。v1 SHA07577f97050a25d354d0891045f9c31f0b6216384b382976e292574fa43832df；正式PDF已缓存SHAa8ab3336bbe881ffd61e2949cc0bff7b570b425625df78407f723445870fb581。MBZUAI/CMU/Stanford，Kun Zhang/Guangyi Chen组。

1. **压力与视角：** 一次得到局部答案不等于满足联合约束。将reasoning写为selection-constrained生成，强调latent变量相互依赖及局部修改需要协调调整。对象尺度是整组依赖，不是某一token正确。
2. **idea来源（RECONSTRUCTED）：** 因果selection结构→规则约束下latent依赖→DEQ/UniversalTransformer/HRM的循环计算→拆成输入建立状态与去输入的依赖自完善，再加间隔监督。创新不在循环本身，而在按该视角拆解计算阶段并得到有用结构。
3. **方法：** 同一Transformer层反复使用，前M步注入x与z，后M(N−1)步只z；默认M=N=16；每M步监督并detach，显式unroll而非DEQ隐式梯度。最终latent→head，没有显式符号constraint verifier。移除x不自动保证真理或消除shortcut。
4. **数据与正式结果：** Sudoku1000train/422786test，Maze1000/1000；Sudoku另每项1000种augmentation，不能把1000原题叫1000训练呈现。3.4M模型Sudoku66.63/Maze93.7 vs27.3M HRM55/74.5；标准Transformer1.17/0。正式稿ARC1/2 pass2为44.3/6.7 vsHRM40.3/5.0，其他循环基线未全测；与前两域pass1分开。训练/推理更快于HRM、更慢于DirectPred，参数少不是总计算少。
5. **决定性设计发现：** 无self-refinement53.11；无反复输入0（正式说明为无input injection，v1描述仅首次注入，两版本不混同）；多次中途重新输入63.32/55.25，默认66.63；独立两个f59.76。更多重读/更多算力不保证更好，输入建立与依赖调整时段有不同作用。但这些是新架构训练消融，不能直接外推已训练decoder里切边的机制。
6. **理论边界与最近邻：** 两条“fundamental hypotheses”是建模假设，不是普遍复杂度定理；v1“exponentially larger”在正式稿弱化成“much larger”。固定点迭代未给所有设置的contractivity/全局正确保证；dense-dependency观点早有RRN/HRM。AppB由加入动态先验改善欠定估计，不是无额外假设证明任何反思都好。因果是设计视角，未测既有LLM内部因果机制。
7. **对我们：** 值得借的是把关系形成与关系协调分开，并用联合可用性决定贡献；不能以一个原子恢复就叫全解析修订。E64固定混合库更不能据final没改认证native传播失败；E71的原生后续使用对比要用实测结果决定是否值得做协调方法，不追加输入/层数网格。

正式AppD每个alignment block都Opt.step并detach，不能把M×N只当等价更深网络；AppE CUB200同架构低于45%而ViT约75%，有作用域边界。该阴性不是对所有LLM反思或所有分类的普遍判决。
