# Self-Learning Runtime Foundation

## 这一版解决什么

Foundation 把 Week 1 的人类可读任务链连接到一个确定性学习状态内核。它能够：

- 校验 `course-manifests/week-01.yaml` 的字段、文件路径、Gate ID、依赖环和回退目标；
- 从 Gate 0 开始一次只呈现一个主动任务；
- 只在学生分支生成当前 Gate 的作答模板，且不覆盖已有回答；
- 只接受学生已经手动 commit 的作答与附件；
- 记录分支、commit SHA 和内容哈希，而不是持续监控编辑行为；
- 把学习历史追加写入 JSONL，并在重启后重放恢复；
- 拒绝非法状态跳转、缺失证据 PASS 和冲突证据自动判定。

当前 MVP 已为 Gate 0 接入版本化 rubric 和稳定 Agent Verifier，但还不能收集 Lab 输出、调用 grader 或生成教学诊断。Gate 1–6 尚无 rubric，不允许模型自由判分。

## 数据所有权

```text
course-manifests/week-01.yaml   只读机器规则；引用课程源，不复制正文
tasks/ resources/ labs/         仓库维护的课程源与公开接口
resources/*.pdf                 学习者正式阅读版本；Runtime 不解析 PDF
homework_answer/                学习者拥有的产物；Runtime 只初始化空模板且不覆盖
.learning-os/events.jsonl       本地私有的追加式审计真相
LearnerState                    从 Ledger 重放得到的缓存视图
```

课程定义、学生产物、原始证据、诊断建议和状态转换是五种不同角色。PDF 是发布产物，不是机器状态真相；hidden grader 与 solutions 不进入 Coordinator 上下文。

## CLI 流程

```bash
uv sync --group dev
git switch -c learner/<你的名字>/week-01
uv run learning-os start week-01
uv run learning-os next
```

完成命令显示的作答文件后，由学生本人执行：

```bash
git add homework_answer/week-01/
git commit -m "answer: week 01 gate 0"
uv run learning-os submit --gate week-01-gate-0
uv run learning-os status
uv run learning-os resume
```

`start` 会先验证 manifest 和当前 Git 分支。`main`、`master` 或 detached HEAD 会被拒绝；Runtime 不会替学生创建或切换分支。检查通过后，它只初始化当前 Gate 的作答文件，再创建事件账本。如果 session 已存在，它会拒绝覆盖并要求使用 `resume`。

`next` 读取 manifest 与重放状态，输出当前能力、当前 Gate、原因、唯一动作、检查项、提示等级和证据索引。

`submit` 先检查必填区块与附件，再以只读 Git 命令确认这些文件已经进入当前 commit。所有检查通过后才依次追加 `artifact_observed`、`attempt_submitted` 和合法的 `transition_applied`。检查失败不会留下半次尝试；它也不会根据运行时长或一句“理解了”推断掌握状态。

`status` 和 `resume` 都从 Ledger 重放；缓存不是审计真相。

## 恢复与停止规则

- Ledger 每行是一个完整 UTF-8 JSON 事件，并在写入后 flush 和 `fsync`。
- 历史行不原地修改；修正必须使用新事件。
- 最后一行或任意历史行损坏时立即停止重放，并报告具体行号。
- 第一个事件不是 `session_started` 时拒绝构造状态。
- 提交 Gate 与当前 Gate 不一致时拒绝写入。
- `insufficient_evidence` 与 `failed` 是不同状态；两者都不能被当成 PASS。
- Runtime 不自动删除、安装依赖、提交、推送或修改学生代码。

## 哪些会迁移到真正的 Agent

这一版不是在精雕 CLI 对话，而是在固定未来 Agent 可调用的确定性工具边界：

| 当前组件 | 进入 Agent 后的去向 |
| --- | --- |
| Manifest 与 Gate 契约 | 保留，继续定义课程规则与当前任务 |
| AnswerWorkspace | 保留，作为初始化和结构检查工具 |
| GitGuard | 保留，作为已提交证据的来源证明工具 |
| EventLedger 与状态重放 | 保留，作为可恢复、可审计记忆 |
| Policy 与 State Machine | 保留，限制 Agent 能否推进或回退 |
| CLI 参数解析与固定打印文本 | 替换为 Agent 对话和 tool calls |
| 当前 Coordinator 文案投影 | 简化或替换；不把它当智能本体 |

因此当前状态机的“聊天外形”是模拟的，但状态授权和证据链不是模拟数据。以后 Agent 可以改变解释方式，却不能绕过学生独立作答、手动 commit 和证据验证。

## 稳定 Agent Verifier

现在的职责链是：

```text
学生 commit 的证据
  → LearningRuntime 从指定 commit 读取并核对哈希
  → Verifier 只逐项返回 criterion 结果
  → 严格校验输出字段、criterion 覆盖和原文引证
  → PolicyEngine 生成 recommendation
  → LearningStateMachine 执行合法状态转换
```

Agent 无权输出 `gate_status`、`recommendation`、`target_gate` 或 `evidence_refs`。出现额外字段、缺失 criterion、无效引证或非法 failure mode 时，本次判定失败，状态保留在 `evidence_pending`，不会误 PASS。

稳定判定键由课程、Gate、答案哈希、排序后的附件哈希、rubric ID/版本/内容哈希和 verifier 版本组成，不包含 evidence ID。相同输入复用 Ledger 中第一次有效结果；rubric 或 verifier 变更会形成新判定。

程序接口如下；CLI 当前尚未提供 `evaluate` 子命令：

```python
from learning_runtime.runtime import LearningRuntime
from learning_runtime.verification.siliconflow import SiliconFlowVerifier

runtime = LearningRuntime(repo_root, repo_root / ".learning-os")
receipt = runtime.evaluate_current(SiliconFlowVerifier.from_env())
```

配置只从环境变量读取：

```text
SILICONFLOW_API_KEY       必填，不得提交
SILICONFLOW_BASE_URL      可选，默认 https://api.siliconflow.cn/v1
SILICONFLOW_MODEL         可选，默认 Qwen/Qwen3.6-35B-A3B
```

`.env` 已被 Git 忽略，`.env.example` 只包含空占位符和非敏感默认值。网络错误、无效 JSON 或 schema 校验失败均不能推进状态。

## 可验证的 Agent 边界

`tests/learning_runtime/test_agent_tool_seam.py` 会在真实的临时 Git 仓库中，让 Fake Agent 调用 `LearningRuntime.start_session()` 和 `submit_answer()`。学生填写与 commit 由测试中的学生模拟器完成；调用前后会核对 HEAD 与 Git status，证明 Runtime 没有替学生执行 Git 写操作。

```bash
uv run pytest tests/learning_runtime/test_agent_tool_seam.py -q
uv run pytest tests/learning_runtime/test_stable_verifier.py -q
uv run pytest tests/learning_runtime/test_agent_state_authority.py -q
uv run pytest -m live tests/live/test_siliconflow_live.py -q
```

最后一个 live test 只在本地设置 `SILICONFLOW_API_KEY` 时发起真实请求；未设置时自动跳过。其余测试使用固定响应，不消耗 API 配额。

## 下一子项目

下一步构建对话式 Agent loop 和 tool schema，让 Agent 负责解释当前任务、触发提交与调用 Verifier；随后为 Gate 1–6 逐步增加 rubric、公开测试和 grader adapter。提示阶梯 Coach 与 Diagnostician 后置。现有工作区、Git 来源证明、稳定判定注册表、Ledger、Policy Engine 和 State Machine 继续作为权限底座。
