# Transformer From Scratch Lab

一个以机制理解为中心的 Transformer 自学实验室。

这里不追求尽快调用框架层或训练一个大模型。目标是逐步获得一项可检验的
能力：面对一个 Transformer 组件，能说清它接收什么、计算什么、输出什么、
为什么需要它，并在实现失败时定位问题。

## 从这里开始

当前学习入口是 [Week 1：Attention 如何按内容读取信息？](weeks/week-01/README.md)。
它要求你独立解释并实现单头 scaled dot-product attention。

如果你还不能稳定判断矩阵乘法、dot product、softmax 与 shape，请先完成
[Week 0：先看懂信息怎样流动](weeks/week-00/README.md)。Week 0 不是可跳过的
背景知识；它是 Q/K/V 与 attention 的直接前置。

## 你会建立什么能力

```text
token 矩阵与 shape
  → Q / K / V 投影
  → score、缩放与 stable softmax
  → attention 的内容读取
  → mask 与 Transformer block
  → 训练、诊断与独立重构
```

每一阶段只增加下一个能力所必需的机制。通过标准是证据，而不是读完材料或
经过多少天：能推导最小例子、在受约束 Lab 中实现、解释一次失败，并把机制
迁移到未见过的小场景。

## 如何学习一周

```text
前置检索 → 精确阅读 → 概念推导 → 无答案 Lab
                                  ↓
                    工程反馈 → 故障诊断 → 独立迁移
```

公开仓库只提供题目、函数契约与 smoke tests。隐藏评分器位于本地 `.grader/`，
只返回错误类别与思考提示，不暴露样例或参考实现。它的作用是帮助你定位机制
缺口，而不是替你完成代码。

## 文件地图

| 位置 | 用途 |
| --- | --- |
| [`weeks/`](weeks/) | 每周导航：为什么学、前置条件、完成标准与入口链接。 |
| [`resources/`](resources/) | 阅读材料、练习、作业与笔记模板。 |
| [`tasks/`](tasks/) | 按知识依赖排序的门控任务链。 |
| [`labs/`](labs/) | 可运行的 starter code、公开测试与评分入口。 |
| [`docs/`](docs/) | 课程设计与运行规则；进入具体学习前不必通读。 |

具体的 Week 1 执行顺序与完成门槛见
[Week 1 导航页](weeks/week-01/README.md)；不要把本 README 当作任务清单。

## 本地运行

```bash
uv sync --group dev
uv run pytest -q
uv run python labs/week-01/run_grade.py
```

`pytest` 只运行公开 smoke tests。最后一条命令仅在本地配置 `.grader/` 时运行
隐藏评分；若 Lab 尚未实现，它会停在当前关卡并给出错误类别，这是正常的学习
反馈。

## 适合与不适合什么

适合：想从 shape、数据流、数值稳定性和失败诊断出发理解 Transformer 的学习者。

不适合：想立即训练大模型、复刻完整论文实现，或只需要调用框架现成
`Transformer` API 的项目。本仓库先建立单头、单层机制的可解释实现能力；更大
的模型与工程选择应在这些基础经过验证后再进入。
