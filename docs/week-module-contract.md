# Week Module Contract

每个 Week 是一份可比较、可执行的学习模块。机制内容和任务难度可以不同，
但产物职责、名称、入口与证据格式必须一致。

## 标准路径

```text
weeks/week-XX/README.md
resources/week-XX/pre-class.md
resources/week-XX/materials.md
resources/week-XX/exercises.md
resources/week-XX/homework.md
resources/week-XX/notes-template.md
tasks/week-XX.md
labs/week-XX/README.md
labs/week-XX/run_grade.py
labs/week-XX/src/
labs/week-XX/tests/
```

PDF、正式题集、讲评与学习者自己的答案是可选支持材料；不能代替上面的标准
产物。

## 标准内容接口

| 产物 | 必须回答或提供什么 |
| --- | --- |
| Week README | 为什么现在学、能力问题、前置证据与范围、依赖/重要性视图、入口顺序、完成定义、下一步解锁。 |
| Pre-class | 前置检索或首周准备检查，以及进入条件。 |
| Materials | 精确阅读范围、问题、完成证据。 |
| Exercises | Lab 前 Gate 练习与每关解锁条件。 |
| Homework | Lab 后工程反思、证据要求与提交标准。 |
| Notes template | 知识更新、失败记录、迁移预测与下一步判断。 |
| Task chain | `Gate 0…N` 的跨文件执行顺序。 |
| Lab README | 为什么现在做、关卡、约束/契约、运行与反馈、Lab 后证据。 |

## 一致性检查

创建新周或调整旧周时，必须比较相邻阶段的：路径、文件粒度、名称、必备标题、
链接/命令和证据字段。差异只能是明确记录的机制特例；不得因为“这一周内容
不同”而静默改变课程产物接口。
