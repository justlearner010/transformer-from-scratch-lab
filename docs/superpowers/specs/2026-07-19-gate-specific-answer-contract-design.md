# Gate 0 按证据必填作答契约设计

## 1. 能力问题与证据边界

> Gate 0 能否只收集证明 shape 链与 `K.T` 理解所必需的证据，同时让学生在作答前明确知道格式要求？

当前代码把同一组 8 个必填栏目应用到全部 Gate。Gate 0 只要求闭卷 shape 推导，却被迫填写实验预测、验证差异和错误诊断；这是格式强度高于任务强度的过度设计。

## 2. 最小知识与证据图

| 节点 | 类型 | 目标深度 | 重要性 | 证据 |
| --- | --- | --- | --- | --- |
| shape 闭合 | mechanism-contract | D2 | P0 | 闭卷答案 |
| `K.T` 机制解释 | mechanism | D2 | P0 | 推导或机制解释 |
| 独立完成来源 | evidence contract | D2 | P1 | 手写附件与提交自检 |

Gate 0 不验证实验操作、预测差异或故障诊断，因此不得强制收集这些栏目。

## 3. 方案与范围

采用按 Gate 配置必填栏目，而不是让所有 Gate 共用全局必填集合。

Gate 0 必填且仅必填：

1. `闭卷答案`
2. `推导或机制解释`
3. `手写与其他附件`
4. `提交自检`

`运行前预测`、`验证过程与结果`、`预测和结果的差异`、`真实错误或当前未知项` 可保留在通用模板中，但 Gate 0 留空不会阻止提交。Gate 0 的 `at-least-one` 附件规则保持不变。

非目标：不重新设计 Gate 1–6，不改模板路径，不改变 Git commit、Verifier、Policy 或状态机。

## 4. 结构与数据流

| 角色 | 路径 | 决定 |
| --- | --- | --- |
| Gate 0 机器规则 | `course-manifests/week-01.yaml` | 覆盖全局 anchor，声明四个必填栏目 |
| 通用作答模板 | `resources/week-01/answer-template.md` | 保持 8 个标题，支持后续 Gate 复用 |
| 展示契约 | `ActionContract.required_sections` | 从 Manifest 投影，不由 LLM 推断 |
| 本地/LLM 展示 | Presenter 与 CLI | 明确显示本 Gate 必填栏目 |
| 结构校验 | `AnswerWorkspace.inspect()` | 继续只校验 Gate 声明的栏目 |

```text
GateDefinition.required_sections
  -> Coordinator.next_action
  -> ActionContract.required_sections
  -> Terminal Presenter / CLI 显示

GateDefinition.required_sections
  -> AnswerWorkspace.inspect
  -> 只拒绝当前 Gate 真正缺失的证据
```

## 5. 错误与兼容性

- 缺少四个必填栏目中的任意一个：错误明确列出栏目名。
- 四个非必填栏目为空：Gate 0 结构检查通过。
- 没有附件或链接失效：仍然拒绝。
- 已存在的 8 栏完整答案继续通过。
- `ActionContract.required_sections` 使用默认空 tuple，避免破坏旧测试构造器；Coordinator 生成的真实契约必须填入 Manifest 值。

## 6. 验证与完成条件

- Manifest 测试断言 Gate 0 必填栏目精确等于上述四项。
- AnswerWorkspace 测试证明四项加附件可以通过，非必填栏目可为空。
- 缺少任一必填栏目或附件仍失败。
- Presenter 和 `learning-os next` 输出包含“本 Gate 必填栏目”。
- 全量离线测试与 PDF 验证继续通过。

完成后，学生只需补齐真正与 Gate 0 能力有关的内容；下一步仍是完成 Gate 0 真实学习闭环，而不是提前设计 Gate 1–6。
