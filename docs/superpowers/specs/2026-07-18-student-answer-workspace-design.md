# Student Answer Workspace 设计

## 1. 决策摘要

Self-Learning Runtime Foundation 已经能够加载 Week 1 Gate、记录提交事件并重放状态，
但当前缺少学生实际作答的正式载体。新增 Student Answer Workspace 后，学习闭环变为：

```text
学生手动创建个人分支
  -> Runtime 初始化当前 Gate 的 Markdown 作答文件
  -> 学生独立作答并可附手写图片或 PDF
  -> 学生手动 commit 本次作答
  -> Runtime 验证当前 commit 中的作答证据
  -> Ledger 记录路径、分支、commit 和内容 hash
  -> 进入 evidence_pending
```

正式作答入口使用 Markdown；手写图片、扫描 PDF 或平板推导作为附件。学生答案跟随
学生自己的 Git 分支提交，`.learning-os/` 仍然只保存本地状态与证据引用。Runtime
不创建分支、不切换分支、不执行 `git add`、`git commit` 或 `git push`。

## 2. 能力问题与证据 caveat

### 2.1 可观察能力问题

> 系统能否为当前 Gate 提供一个明确、可提交、可追溯的学生作答区，并在不修改
> 学生 Git 状态的前提下，证明本次提交引用的是学生分支中已经 commit 的真实版本？

### 2.2 当前证据

- 仓库已有 `homework_answer/week-00/`，说明 `homework_answer/` 是学生答案的既有位置；
- 当前 Week 0 文件尚未形成模板、frontmatter、Gate 粒度或 Runtime 校验契约，分类为
  `incomplete`，不是可直接复制的完整规范；
- Week 1 Manifest 已显式定义 Gate 0–6、task layer 和 required evidence；
- Runtime 已有追加式 Ledger、状态重放和 `submit --gate`；
- 当前 `submit` 只记录尝试，不检查答案文件或 Git commit。

### 2.3 未知项

- 手写附件是否显著提升推导与迁移质量，需要真实 session 验证；
- 开放式 Markdown 与手写内容如何评价，仍属于后续 Verifier/人工混合评价问题；
- Git commit 频率是否给学生造成过高操作负担，需要记录实际失败率和中断点。

这些未知项不得被解释成方案无效或学生已经掌握。

## 3. 知识与操作节点

| 节点 | 类型 | 当前 -> 目标 | 依赖角色 | 优先级 | 任务层与理由 |
| --- | --- | --- | --- | --- | --- |
| 作答文件契约 | contract | 不存在 -> D3 | hard | P0 | T3：后续 Evidence Collector 的输入边界 |
| 运行前预测与独立推导 | mechanism evidence | unknown -> D4 | corequisite | P0 | T1/T4：防止运行后反向补写 |
| Git 版本冻结 | procedure + contract | unknown -> D3 | hard | P0 | T3：证明证据对应一个稳定版本 |
| 手写附件引用 | procedure | unknown -> D2 | soft | P1 | T2：保留原始推导，不要求 OCR 判分 |
| 分支所有权 | operation | 手动 -> D3 | hard | P1 | T3：答案必须属于学生分支 |
| 文件与 commit hash | contract | 不存在 -> D3 | integration | P1 | T3：连接 artifact、Ledger 与后续评价 |

P0 只保留三个瓶颈：作答契约、独立推导、Git 版本冻结。手写附件服务于证据质量，
不单独决定 Gate PASS。

## 4. 依赖图与范围

```text
学生手动建立个人分支
  -> 分支保护检查
  -> 当前 Gate 模板初始化
  -> Markdown 独立作答
  -> 可选或 Gate 指定的手写附件
  -> 学生手动 Git commit
  -> 结构、链接、tracked 与 clean 检查
  -> artifact + commit hash Evidence Record
  -> attempt_submitted
  -> evidence_pending
```

### 4.1 本次范围

- Week 1 Gate 0–6 作答模板；
- 学生分支检查和命名警告；
- 当前 Gate 文件按需初始化；
- Markdown/frontmatter/必需章节/附件检查；
- 本 Gate 证据文件的 Git tracked、committed 和 clean 检查；
- branch、commit SHA、blob/file hash 和附件 hash 记录；
- CLI 输出作答路径和准确修复提示。

### 4.2 非目标

- Runtime 自动创建、切换、提交或推送分支；
- 自动 OCR 或给手写推导判分；
- 将答案正文复制进 Ledger；
- 要求整个仓库工作区 clean；
- Web 编辑器、富文本编辑器或云端答案存储；
- 在本功能中实现完整 Coach、Diagnostician 或 hidden grader。

## 5. 结构兼容性映射

| 产物角色 | 规范路径 | 现有模式 | 分类 | 决策与迁移影响 |
| --- | --- | --- | --- | --- |
| 周导航 | `weeks/week-01/README.md` | 已存在 | canonical | 增加作答区与分支流程链接 |
| 人类任务链 | `tasks/week-01.md` | 已存在 | canonical | 保持 Gate 真相，不复制题目 |
| 机器 Gate 规则 | `course-manifests/week-01.yaml` | 已存在 | canonical | 增加 submission contract 引用 |
| 作答模板 | `resources/week-01/answer-templates/gate-XX.md` | 尚无 | new required role | 归入现有 resource 角色，不建平行顶层模板目录 |
| 学生正式作答 | `homework_answer/week-01/gate-XX.md` | Week 0 有合并题型文件 | incomplete predecessor | Week 1 采用一 Gate 一文件；Week 0 暂不迁移 |
| 手写附件 | `homework_answer/week-01/attachments/gate-XX/` | 尚无 | justified variation | 只服务当前 Gate，Markdown 必须引用 |
| 本地状态 | `.learning-os/events.jsonl` | 已存在 | canonical private | 只记录引用和 hash，不保存答案正文 |
| Lab | `labs/week-01/` | 已存在 | canonical | 不移动、不由 Workspace 修改 |

`homework_answer/` 不加入 `.gitignore`。它是学生分支中需要版本控制的正式成果。

## 6. 跨阶段产物契约

### 6.1 规范路径与粒度

```text
resources/week-XX/answer-templates/gate-YY.md
homework_answer/week-XX/gate-YY.md
homework_answer/week-XX/attachments/gate-YY/*.{png,jpg,jpeg,pdf}
```

- 一个 Gate 一个 Markdown 文件；
- 文件名使用两位数字，与 Manifest Gate ID 一一对应；
- 附件目录只归属于同号 Gate；
- 后续阶段复用同一粒度，除非规格明确记录 justified variation。

### 6.2 Markdown 必需结构

```markdown
---
course_id: transformer-from-scratch
phase_id: week-01
gate_id: week-01-gate-0
template_version: 1
---

# Gate 0 作答

## 闭卷答案

## 运行前预测

## 推导或机制解释

## 验证过程与结果

## 预测和结果的差异

## 真实错误或当前未知项

## 手写与其他附件

## 提交自检
```

所有 Gate 使用同一基础结构。某一节可以明确写“本 Gate 不适用”并说明原因，不能留空或
保留模板占位符。模板不包含答案、参考数值、hidden inputs 或 expected outputs。

### 6.3 手写附件规则

- Markdown 是所有 Gate 的正式入口；附件不能替代 Markdown 总结；
- 支持 `.png`、`.jpg`、`.jpeg` 和 `.pdf`；
- 附件必须使用仓库相对链接，且位于当前 Gate 附件目录；
- Week 1 Gate 0 要求至少一份手写或平板书写的 shape 推导附件；
- Gate 1–6 默认可选，但 Manifest 可以按知识类型提升为必需；
- MVP 只验证附件存在、路径边界、Git 版本和 hash，不自动评价附件内容；
- 无法手写的可访问性例外必须显式记录为 escalation，由人工确认替代证据。

### 6.4 Manifest 增量契约

顶层新增：

```yaml
learner_workspace:
  answer_root: homework_answer
  template_root: resources/week-01/answer-templates
  protected_branches: [main, master]
  recommended_branch_pattern: '^learner/[^/]+/week-01$'
  commit_required: true
```

每个 Gate 新增：

```yaml
submission:
  template_ref: resources/week-01/answer-templates/gate-00.md
  artifact_path: homework_answer/week-01/gate-00.md
  required_sections:
    - 闭卷答案
    - 运行前预测
    - 推导或机制解释
    - 验证过程与结果
    - 预测和结果的差异
    - 真实错误或当前未知项
    - 手写与其他附件
    - 提交自检
  attachment_policy: at-least-one
```

Manifest Loader 必须验证模板存在、artifact path 不逃逸 `answer_root`、Gate 路径唯一、
required sections 非空以及 attachment policy 是允许值。

## 7. 分支与 Git 边界

### 7.1 学生操作

学生手动创建分支，推荐命名：

```bash
git switch -c learner/<student-name>/week-01
```

Runtime 行为：

- `main`、`master` 或 Manifest 配置的保护分支：拒绝 `start`；
- 符合推荐命名：正常执行；
- 其他非保护分支：允许执行并显示警告；
- session event 记录实际分支名，但不执行 Git 写操作。

### 7.2 commit 前置条件

学生必须先手动冻结本次尝试：

```bash
git add homework_answer/week-01/gate-00.md \
  homework_answer/week-01/attachments/gate-00/
git commit -m "answer: week 01 gate 0 attempt 1"
uv run learning-os submit --gate week-01-gate-0
```

`submit` 只检查当前 Gate 的 Markdown 和被其引用的附件：

- 文件必须被当前 commit 跟踪；
- 工作区文件内容必须与 `HEAD` 中对应 blob 一致；
- 不要求无关文件 clean；
- Git commit 只证明版本存在，不证明内容正确或 Gate 通过；
- Runtime 不自动 stage、commit、amend、reset、checkout 或 push。

## 8. 组件与数据流

### 8.1 Answer Workspace

建议新增：

```text
learning_runtime/workspace/answer_workspace.py
```

职责：

- 依据当前 Gate 定位模板和作答路径；
- 只在目标不存在时复制模板；
- 创建当前 Gate 附件目录；
- 解析 frontmatter、必需章节和 Markdown 附件链接；
- 返回结构化 `AnswerArtifact`，不评价答案正确性。

### 8.2 Git Guard

建议新增：

```text
learning_runtime/workspace/git_guard.py
```

职责：

- 读取当前分支、HEAD commit 和指定路径 tracked 状态；
- 比较工作区文件与 `HEAD` blob；
- 只执行只读 Git 命令；
- 返回逐文件结果，不执行任何修复命令。

### 8.3 Evidence Record

成功提交产生 artifact evidence：

```yaml
evidence_id: evidence-0001
type: committed-answer
source: homework_answer/week-01/gate-00.md
artifact_ref: homework_answer/week-01/gate-00.md
observation:
  gate_id: week-01-gate-0
  branch: learner/jay/week-01
  commit_sha: 40-character SHA
  content_hash: sha256:...
  attachments:
    - path: homework_answer/week-01/attachments/gate-00/shape-derivation.jpg
      content_hash: sha256:...
```

Ledger 事件顺序：

```text
answer_workspace_initialized
artifact_observed
attempt_submitted
transition_applied -> evidence_pending
```

失败检查不得追加 `attempt_submitted` 或改变 Gate 状态。可记录不改变状态的 operation
错误日志，但首版默认只向终端报告，避免噪声事件。

## 9. CLI 体验

`start` 成功后新增输出：

```text
学生分支：learner/jay/week-01
作答文件：homework_answer/week-01/gate-00.md
附件目录：homework_answer/week-01/attachments/gate-00/
提交前：请手动 git add / git commit
```

`next` 始终显示当前 Gate 的作答文件路径。

`submit` 失败时返回精确、可操作但不自动执行的提示，例如：

```text
无法提交：以下证据尚未进入当前 commit
- homework_answer/week-01/gate-00.md
- homework_answer/week-01/attachments/gate-00/shape-derivation.jpg

请手动 git add 和 git commit 后重新提交。
```

## 10. 错误处理

| 情况 | 处理 | 状态影响 |
| --- | --- | --- |
| 位于保护分支 | 拒绝初始化，提示手动建学生分支 | 不创建 session/答案 |
| 非推荐分支名 | 警告并记录实际分支 | 允许继续 |
| 模板或 Manifest 无效 | 报告精确路径/字段 | 不创建 session/答案 |
| 作答已存在 | 保留并复用，不覆盖 | 无 |
| 作答文件缺失 | `insufficient_evidence` | 不追加 attempt |
| frontmatter Gate 错误 | 报告期望与实际 Gate | 不追加 attempt |
| 必需章节空白/占位 | 列出章节 | 不追加 attempt |
| 附件缺失或越界 | 列出链接与原因 | 不追加 attempt |
| 证据未 tracked | 列出文件 | 不追加 attempt |
| 证据与 HEAD 不一致 | 列出 dirty 文件 | 不追加 attempt |
| 无关文件 dirty | 忽略 | 无 |
| commit 检查通过但 Verifier 不可用 | 保存 artifact evidence | 保持 evidence_pending |
| 已有答案与模板版本不同 | 保留答案并报告版本 | 不自动迁移或覆盖 |

## 11. 验证策略

### 11.1 Workspace 单元测试

- 只初始化当前 Gate；
- 已有作答永不覆盖；
- frontmatter、必需章节、占位符和附件链接解析；
- 附件路径不能逃逸当前 Gate 目录；
- Gate 0 缺少附件时拒绝提交；
- Markdown 和附件 hash 稳定。

### 11.2 Git Guard 集成测试

在临时 Git 仓库中覆盖：

- 保护分支拒绝；
- 标准学生分支通过；
- 非标准分支警告但通过；
- untracked、staged-but-uncommitted、modified-after-commit 分别被识别；
- 只检查本 Gate 证据，无关 dirty 文件不阻塞；
- Git Guard 执行前后 `status --porcelain` 完全一致，证明无写操作。

### 11.3 CLI 端到端测试

1. 学生分支 start，创建 Gate 0 作答文件；
2. 空模板 submit 被拒绝，Ledger 无 attempt；
3. 填写 Markdown、添加手写附件但未 commit，submit 被拒绝；
4. 手动 commit 后 submit 成功；
5. Ledger 记录 branch、commit、artifact 和附件 hash；
6. 状态进入 evidence_pending；
7. 修改已提交文件后，旧 commit 不能满足新提交；
8. resume 从 Ledger 恢复同一证据索引。

### 11.4 回归检查

- 现有 `uv run pytest -q` 全部通过；
- 现有四份正式 PDF 继续通过验证；
- `learning-os` 不出现 Git 写命令；
- 课程分支中的模板不含答案；
- `homework_answer/` 不在 `.gitignore`；
- 主仓库已有 Week 0 用户答案不被读取、移动或覆盖。

## 12. 完成门槛

- Week 1 七个模板符合统一格式；
- Manifest submission contract 通过结构和路径验证；
- Runtime 在保护分支拒绝初始化；
- 当前 Gate 作答按需创建且绝不覆盖；
- 未 commit 的作答无法 `submit`；
- 成功提交的 evidence 可追溯到 branch、commit 和文件 hash；
- Markdown/附件/事件三个层次保持分离；
- 失败检查不会改变 Gate 状态；
- Runtime 未执行任何 Git 写操作；
- 端到端测试证明 commit 后才能进入 evidence_pending。

## 13. 下一项解锁能力

Student Answer Workspace 通过后，下一项能力是 Evidence Collector + Verifier：读取
committed-answer evidence、公开测试结果和 grader 分类，为每项 criterion 产生
`passed`、`failed` 或 `insufficient_evidence`，再交给现有 Policy Engine 决定
PASS、REINFORCE、DIAGNOSE 或 ESCALATE。
