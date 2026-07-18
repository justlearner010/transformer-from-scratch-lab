# Self-Learning Runtime Foundation

## 这一版解决什么

Foundation 把 Week 1 的人类可读任务链连接到一个确定性学习状态内核。它能够：

- 校验 `course-manifests/week-01.yaml` 的字段、文件路径、Gate ID、依赖环和回退目标；
- 从 Gate 0 开始一次只呈现一个主动任务；
- 显式记录学生提交，而不是持续监控编辑行为；
- 把学习历史追加写入 JSONL，并在重启后重放恢复；
- 拒绝非法状态跳转、缺失证据 PASS 和冲突证据自动判定。

这一版还不能收集 Lab 输出、调用 grader、验证 criterion 或生成诊断。它是后续 Agent 接入前必须稳定的状态与权限地基。

## 数据所有权

```text
course-manifests/week-01.yaml   只读机器规则；引用课程源，不复制正文
tasks/ resources/ labs/         仓库维护的课程源与公开接口
resources/*.pdf                 学习者正式阅读版本；Runtime 不解析 PDF
homework_answer/                学习者拥有的产物；Runtime Foundation 不写入
.learning-os/events.jsonl       本地私有的追加式审计真相
LearnerState                    从 Ledger 重放得到的缓存视图
```

课程定义、学生产物、原始证据、诊断建议和状态转换是五种不同角色。PDF 是发布产物，不是机器状态真相；hidden grader 与 solutions 不进入 Coordinator 上下文。

## CLI 流程

```bash
uv sync --group dev
uv run learning-os start week-01
uv run learning-os next
uv run learning-os submit --gate week-01-gate-0
uv run learning-os status
uv run learning-os resume
```

`start` 会先验证 manifest，再创建事件账本。如果 session 已存在，它会拒绝覆盖并要求使用 `resume`。

`next` 读取 manifest 与重放状态，输出当前能力、当前 Gate、原因、唯一动作、检查项、提示等级和证据索引。

`submit` 只追加 `attempt_submitted`，再由状态机追加合法的 `transition_applied`。它不会根据文件缺失、运行时长或一句“理解了”推断掌握状态。

`status` 和 `resume` 都从 Ledger 重放；缓存不是审计真相。

## 恢复与停止规则

- Ledger 每行是一个完整 UTF-8 JSON 事件，并在写入后 flush 和 `fsync`。
- 历史行不原地修改；修正必须使用新事件。
- 最后一行或任意历史行损坏时立即停止重放，并报告具体行号。
- 第一个事件不是 `session_started` 时拒绝构造状态。
- 提交 Gate 与当前 Gate 不一致时拒绝写入。
- `insufficient_evidence` 与 `failed` 是不同状态；两者都不能被当成 PASS。
- Runtime 不自动删除、安装依赖、提交、推送或修改学生代码。

## 下一子项目

下一步接入 Evidence Collector、公开测试与 grader adapter、逐 criterion Verifier、提示阶梯 Coach 和只提供建议的 Diagnostician。那一层负责产生可信证据与建议；Policy Engine 和 State Machine 仍保留最终决定权。
