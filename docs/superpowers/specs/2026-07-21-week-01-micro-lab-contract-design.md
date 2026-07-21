# Week 1 Micro-Lab 数据流与反馈契约

> 状态：已确认的课程设计；尚未开始迁移实现。
>
> 本文是 Week 1 micro-lab 的唯一目标契约，取代
> [`docs/week-01-micro-lab-design.md`](../../week-01-micro-lab-design.md)
> 中“shape 编码题 → score → softmax → value → projection”的旧顺序。旧文档保留为
> 决策历史，不能再作为新 Gate 或新测试的依据。

## 1. 能力问题与证据边界

**能力问题：**给定单样本 token 矩阵 `X` 及三组投影权重，学习者能否在不看答案的条件下，
独立追踪并实现一次单头 scaled dot-product attention 的数据流，并定位一个违反局部契约的错误？

这个能力不是“会背 attention 公式”，而是下面三件能观察到的事：

1. 在运行前能预测下一张量的 shape、含义或性质；
2. 能在限定接口中实现当前一小步，并读懂公开检查的反馈；
3. 能把已验证的小步组合起来，且解释一个真实失败的根因。

### 已有证据与未知项

| 项目 | 结论 | 处理方式 |
| --- | --- | --- |
| Week 0 的矩阵与 shape 学习记录 | 是历史学习资产；不重置、不隐藏 | Gate 0 可引用它，但必须产生新的 Week 1 闭卷证据 |
| 现有 Gate 0 | 已暴露 `K.T` 和 shape 链可能断裂 | 保持为推导/解释，不用编码重复验证 |
| `01-score-probe/starter.py` | 学习者工作副本可能已有未提交修改 | 迁移前必须保护；不得自动移动、覆盖或格式化 |
| 各 micro-lab 目前的顺序 | 与 attention 数据流不一致 | 仅在后续迁移任务中按本文重排 |
| 学习者的当前掌握程度 | 不能由一次通过/失败推断 | Agent 只依据当前 Gate 的已提交证据、公开检查和 rubric 判断 |

### 非目标

- 不做 batch、多头、mask、训练或性能优化；
- 不让 Agent 改写学生代码、直接给出参考实现，或绕过状态机放行；
- 不把每个名词都做成一个 Lab；
- 不把“测试通过”当作掌握的唯一证据；
- 不在本次设计提交中移动目录、改 starter、改 manifest 或改学生作答。

## 2. 知识地图：按真正的瓶颈分配练习强度

本周只保留三个 P0 瓶颈。它们不是按“公式数量”划分，而是按一个错误会阻断多少下游步骤划分。

| 节点 | 类型 | 当前 → 目标 | 依赖角色 | 优先级与理由 | 任务层 | 最小独立证据 |
| --- | --- | --- | --- | --- | --- | --- |
| 投影契约 | contract + procedure | unknown → D3 | 硬前置 | **P0**：没有合法 Q/K/V，后续均没有输入 | T1, T3 | 预测 shape；通过边界检查；说清每个投影的输入/输出 |
| 匹配到权重 | mechanism + diagnosis | unknown → D4 | 硬前置 | **P0**：`Q @ K.T`、缩放、softmax 的错误会使读取权重整体失真 | T1, T3, T4 | 转置/axis/极值的预测、检查和一例故障解释 |
| 读取与组合 | mechanism + integration | unknown → D4 | 整合 | **P0**：把权重与 V 的职责连接为最终 output，并检验数据流未被重写 | T1, T3, T5 | 改 V 的预测、局部读取检查、仅复用组件的组合 |
| shape 书面追踪 | contract | unknown → D2 | Gate 0 诊断入口 | P1：快速暴露前置缺口，不再承担编码职责 | T1 | 闭卷写出 shape 链并解释 `K.T` |
| 故障诊断 | diagnosis | unknown → D4 | 下游 | P1：验证学习者能修复而非碰巧通过 | T4 | 现象、假设、最小验证、修复后的回归检查 |

强度规则：每一个 P0 都要经历“预测 → 受约束实现 → 局部性质检查 → 变体或失败 → 后续消费者”；
P1 不为了形式完整额外制造一个代码任务。

## 3. 唯一数据流、范围与 Gate 顺序

```text
Gate 0: 纸面 shape / 机制入口（不写 starter）
    X, W_Q, W_K, W_V 的符号契约
                         |
                         v
Gate 1: QKV projection
    X, W_Q, W_K, W_V  ->  Q, K, V
                         |
                         v
Gate 2: score probe
    Q, K               ->  scores
                         |
                         v
Gate 3: stable softmax
    scores             ->  weights
                         |
                         v
Gate 4: value read
    weights, V         ->  output
                         |
                         v
Gate 5: compose
    X, W_Q, W_K, W_V   ->  weights, output
    （只调用 Gate 1–4 的公共接口）
                         |
                         v
Gate 6: inspect / diagnose
    一个真实失败         ->  可验证的根因与修复
```

这是**线性硬依赖**：Gate 2 不再提前讲 QKV 职责，Gate 4 不再隐含重写投影，Gate 5
不再是“再写一遍 attention”。任何 Gate 发现的前置缺口都回到最早不满足的 Gate，而不是
让学习者在后面堆积问题。

## 4. 结构兼容与迁移范围

| 产物角色 | 目标规范路径 | 现有模式 | 分类 | 后续迁移决定 |
| --- | --- | --- | --- | --- |
| 周导航 | `weeks/week-01/README.md` | 已存在 | canonical | 更新顺序与链接；不新增第二个入口 |
| 材料与任务说明 | `resources/week-01/`、`tasks/week-01.md` | 已存在 | canonical | 每段只链接当前 Gate 的练习与证据 |
| 可运行练习 | `labs/week-01/micro/<nn>-<name>/` | 已存在但编号/顺序错误 | incomplete | 在原 `labs/week-01/` 内重排，不另建课程根目录 |
| 局部公开检查 | `labs/week-01/micro/<nn>-<name>/tests/checks.py` | 已存在 | justified variation | 保持 `run_micro.py <name>` 入口；不让默认 pytest 把未完成 starter 当仓库 CI 失败 |
| 整合检查 | `labs/week-01/micro/compose/tests/checks.py` | 已存在 | incomplete | 增加“调用组件而非重写”的契约检查 |
| Gate 证据 | `homework_answer/week-01/gate-<nn>.md` | 已存在 | canonical | 模板按当前 Gate 类型显示所需栏位 |
| 历史证据 | `homework_answer/week-00/learning-record.md` | 单文件 | legacy, retained | 明确可见、可引用；不强行改造成 Week 1 格式 |

### 目标目录映射

| Gate | 学习责任 | 目标 Lab 目录 | 本 Gate 是否编码 |
| --- | --- | --- | --- |
| 0 | 符号 shape 与 `K.T` 解释 | 无 | 否 |
| 1 | `X` 投影成 Q/K/V | `01-qkv-projection/` | 是 |
| 2 | Q 与 K 的匹配分数 | `02-score-probe/` | 是 |
| 3 | 分数归一化成权重 | `03-stable-softmax/` | 是 |
| 4 | 用权重读取 V | `04-value-read/` | 是 |
| 5 | 复用前四步组合 attention | `compose/` | 是，只组合 |
| 6 | 诊断/inspector | 沿用现有诊断产物 | 可选的最小修复 |

迁移前的命名（`00-shape-trace`、`01-score-probe`、`02-stable-softmax`、
`03-value-read`、`04-qkv-projection`）只能视为旧编号。之后的实现必须同时更新导航、
命令别名、manifest、Gate 文案、公开检查和链接；只改文件夹名不算迁移完成。

### 学习者工作保护规则

1. 任何已有或未提交的 `starter.py` 都归学习者所有；迁移脚本和 Git 操作不得自动移动或覆盖。
2. 特别是现有 `01-score-probe/starter.py`：实施迁移前先检查 Git 状态；若有修改，先请学习者
   commit，或把该文件复制为由学习者确认的草稿，再创建 `02-score-probe/`。
3. 历史 Gate 证据只追加兼容说明，不重写其内容或提交历史。
4. 新模板只生成缺失文件；已有作答文件绝不覆盖。

## 5. 每个 Gate 的接口契约

所有函数只处理无 batch 维的二维 NumPy 数组。`n` 是 token 数，`d_model` 是输入特征维度，
`d_k` 是 query/key 特征维度，`d_v` 是 value 特征维度。MVP 约束 Q 与 K 使用相同的
特征维度 `d_k`。

| Gate | 学生实现的公共接口 | 接受的输入 | 必须产生的输出 | 明确禁止 |
| --- | --- | --- | --- | --- |
| 1 | `project_qkv(tokens, w_q, w_k, w_v)` | `X:(n,d_model)`；`W_Q:(d_model,d_k)`；`W_K:(d_model,d_k)`；`W_V:(d_model,d_v)` | `Q:(n,d_k)`、`K:(n,d_k)`、`V:(n,d_v)`；不得改动 `X` | 计算 score、softmax 或 output |
| 2 | `score_qk(query, key)` | `Q:(n_q,d_k)`、`K:(n_k,d_k)` | `scores:(n_q,n_k)`；每一格代表一个 query-key 匹配 | 在此步 softmax、读取 V，或把 K 当作 V |
| 3 | `stable_softmax(scores)` | 有限的 `scores:(n_q,n_k)` | `weights:(n_q,n_k)`；有限且每行和为 1 | 修改 `scores`，或沿错误 axis 归一化 |
| 4 | `read_values(weights, value)` | `A:(n_q,n_k)`；`V:(n_k,d_v)`；A 是非负、逐行和为 1 的分布 | `output:(n_q,d_v)` | 重新计算 Q/K/score/softmax |
| 5 | `scaled_dot_product_attention(tokens, w_q, w_k, w_v)` | Gate 1 的全部输入 | `weights:(n,n)` 与 `output:(n,d_v)` | 复制 Gate 1–4 的内部算法；跳过任何公共接口 |
| 6 | inspector/诊断入口 | 一次真实失败的输入、输出与最小复现 | 根因、修复、回归结果 | 只有现象描述；编造未运行的测试结果 |

### 每个 micro-lab 必备文件字段

| 文件 | 必须包含 | 不能包含 |
| --- | --- | --- |
| `README.md` | 问题边界、输入/输出、运行命令、预测问题、通过性质、错误类别 | 参考实现或逐行解法 |
| `starter.py` | 仅当前 Gate 的函数签名、docstring、`NotImplementedError` 占位 | 后续 Gate 的实现，或完整 attention 答案 |
| `tests/checks.py` | 正例性质、每类边界失败、确定性的错误提示 | 固定参考输出的泄题断言 |
| `homework_answer/.../gate-<nn>.md` | 该 Gate 对应的预测、实验结果、解释、自检 | 对不需要推导的 Gate 强制增加推导栏 |

## 6. 错误类别与学生可见提示协议

公开检查的责任是指出**哪一种契约被破坏**，不是给出如何写代码。每一条学生可见失败信息
必须使用同一格式：

```text
[Gate <编号> · <错误类别>]
观察到：<真实 shape / 性质 / 运行结果>
契约：<本 Gate 必须成立的输入或输出条件>
为什么阻断下一步：<下游消费者为何不能安全使用它>
先检查：<一个不含参考代码的检查方向>
```

`先检查` 只能指向维度、轴、输入是否被改动、或上一 Gate 的输出；不得写成可复制的
代码表达式，不得给出 reference output。

| Gate | 错误类别 | 必须报告的条件 | 学生获得的“先检查”方向 |
| --- | --- | --- | --- |
| 1 | `input_rank` | 任一输入不是二维 | 检查 token 与每个权重是否都是矩阵 |
| 1 | `projection_input_dim` | 某个 `W_*` 第一维不等于 `X.shape[1]` | 对齐投影的输入特征维度 |
| 1 | `qk_feature_dim` | Q、K 最后一维不同 | 比较 Q 与 K 传给 score 前的最后一维 |
| 1 | `input_mutated` | 调用后 token 内容变化 | 检查是否对输入做了原地写入 |
| 2 | `input_rank` | Q 或 K 不是二维 | 从 Gate 1 读取 Q/K 的 shape |
| 2 | `qk_feature_dim` | Q、K 最后一维不同 | 关注匹配维度而非 token 数 |
| 2 | `score_shape` | 输出不是 `(n_q,n_k)` | 用每一个 query 对每一个 key 的关系核对行列 |
| 3 | `empty_axis` | key 轴长度为 0 | 确认本次确实有可归一化的候选 key |
| 3 | `non_finite_input` | score 含 NaN 或 Inf | 回看 Gate 2 是否产生了有限分数 |
| 3 | `non_finite_output` | 归一化后含 NaN 或 Inf | 检查极端数值时的数值稳定性 |
| 3 | `row_sum_not_one` | 某一行 weights 之和不是 1 | 检查归一化是否沿 key 轴进行 |
| 3 | `negative_weight` | weights 出现负数 | 检查输出是否仍是概率分布 |
| 4 | `input_rank` | A 或 V 不是二维 | 从 Gate 3 和 Gate 1 回看各自输出 |
| 4 | `value_row_mismatch` | `A.shape[1] != V.shape[0]` | 每个 key 的权重必须能对应一行 value |
| 4 | `invalid_weight_distribution` | A 有负数、非有限值或行和不为 1 | 先修 Gate 3 的概率分布性质 |
| 4 | `output_shape` | 输出不是 `(n_q,d_v)` | 从 query 数与 value 特征维度推断结果 shape |
| 5 | `component_not_called` | 缺少任一 Gate 1–4 接口调用 | 检查数据流是否确实经过所有已验证组件 |
| 5 | `component_order_invalid` | 顺序不是 projection→score→softmax→read | 从上游输出和下游输入重新排列链条 |
| 5 | `composition_output_contract` | weights/output 的 shape 或性质不满足 | 定位第一个违反局部契约的组件，不重写整段函数 |
| 6 | `unreproduced_failure` | 没有可复现命令或真实输出 | 写下最小输入和实际命令 |
| 6 | `root_cause_missing` | 只有现象没有违反的契约 | 将观察到的现象映射回 Gate 1–5 的一个类别 |
| 6 | `regression_missing` | 修复后未重新运行相关检查 | 运行原失败检查和相邻消费者检查 |

相同输入必须得到相同的类别与提示文本；测试不允许依赖 LLM。Agent 可以根据这些类别选择
提示等级，但不能改写类别、放宽通过条件，或把模型猜测当作测试结论。

## 7. 作答、提交与 Agent 的权限边界

### 学习者的最小闭环

```text
读当前 Gate → 在 Gate 作答文件写预测 → 只改当前 starter.py
→ 运行当前公开检查 → 记录真实结果与解释 → 手动 git commit
→ learning-os submit → Policy/State Machine 决定下一状态
```

每个 Gate 的模板都应只显示必要栏位：

| Gate 类型 | 必填栏位 |
| --- | --- |
| Gate 0（推导/机制） | 闭卷答案、机制解释、提交自检 |
| Gate 1–4（局部 Lab） | 预测、测试结果、机制解释、提交自检 |
| Gate 5（组合） | 数据流图、测试结果、组件复用自检、提交自检 |
| Gate 6（诊断） | 失败现象、最小复现、根因、修复验证、提交自检 |

手写附件始终是可选项；它可以补充证据，不能替代可提交的文字说明与真实运行结果。

### 不可越界的权力分配

| 参与者 | 可以做 | 不可以做 |
| --- | --- | --- |
| 课程设计者（人） | 定义知识图、接口、错误类别、rubric、通过规则 | 事后为了某位学生临时改标准 |
| 公开检查 | 验证确定性的局部契约、返回固定类别和提示 | 判断开放题掌握程度，或提供参考答案 |
| Agent/LLM | 读取已提交证据与固定结果；按 rubric 给有限提示；建议回退 Gate | 改代码、改测试、改状态、绕过 commit、直接给答案 |
| Policy + State Machine | 验证提交、聚合证据、决定 passed/revise/reinforce | 用自由文本替代规则或捏造证据 |
| 学习者 | 写答案、改当前 starter、运行检查、提交证据 | 让 Agent 代写实现或跳过前置 Gate |

当同一错误第二次被提交时，Agent 可以从“指出类别与一项检查方向”升级到“解释被破坏的
下游关系，并给一个更小的输入让学生自行预测”；仍不能给代码或最终数值答案。是否回退由
确定的失败路由决定，不由模型概率决定。

## 8. 验证、完成标准与下一步

后续迁移实现必须通过以下检查，才可以替换现有学习路径：

1. **结构检查：**Gate 0 无编码 starter；Gate 1–5 的目录、README、starter、checks 和
   导航链接均存在，且编号与 manifest 一致。
2. **非泄题检查：**所有 starter 在新学习者副本中为未实现状态；公开检查可以指出错误类别，
   但仓库中没有可直接提交的局部答案。
3. **局部契约检查：**每个 Gate 至少有一条正例、一条边界例；错误文本符合第 6 节格式，
   相同输入输出稳定。
4. **组合检查：**Gate 5 确实调用 Gate 1–4 的公共接口，且不会把它们重新实现为一段大函数。
5. **证据检查：**模板只要求该 Gate 所需栏目；`learning-os submit` 仍要求学习者手动 commit。
6. **回归检查：**现有 Week 0 资产可见；现有已提交 Week 1 证据和 runtime 测试不被破坏。
7. **学习者验证：**由当前学习者实际完成一轮 Week 1。体验问题先记录为证据，再决定下一轮改造，
   不在学习过程中持续扩张功能。

Week 1 完成的最低条件：三个 P0 瓶颈各有独立证据，Gate 5 的数据流未重写，Gate 6 有一次
真实失败的“现象→契约→修复→回归”链。满足后才解锁 causal mask；它将作为 score 与 softmax
之间的一个新 Gate，而不会塞进已有 Lab。

## 9. 后续实施边界（本次不执行）

下一次开发应先写迁移计划，并按以下顺序执行：

1. 检查所有学习者 worktree 与未提交 starter，完成保护/确认；
2. 调整目录编号和每个局部接口；
3. 重写公开 checks 的契约提示；
4. 更新周导航、任务链、manifest、模板和 `run_micro.py` 别名；
5. 添加结构与稳定提示测试；
6. 仅在独立开发 worktree 验证通过后合并；
7. 由学习者完成完整 Week 1，再收集反馈。

这份顺序刻意把“保护学习资产”和“验证真实学习体验”放在功能扩张之前。
