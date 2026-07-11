from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "problem-sets" / "week-00-problem-set.pdf"
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT_NAME = "ArialUnicode"


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("&", "&amp;"), style)


def add_page_number(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont(FONT_NAME, 9)
    canvas.setFillColor(HexColor("#5B6472"))
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, f"Week 0 Problem Set  |  {document.page}")
    canvas.restoreState()


def main() -> None:
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCN", parent=styles["Title"], fontName=FONT_NAME, fontSize=23,
        leading=31, alignment=TA_CENTER, textColor=HexColor("#172554"), spaceAfter=10,
    )
    subtitle = ParagraphStyle(
        "SubtitleCN", parent=styles["Normal"], fontName=FONT_NAME, fontSize=11,
        leading=18, alignment=TA_CENTER, textColor=HexColor("#475569"), spaceAfter=18,
    )
    heading = ParagraphStyle(
        "HeadingCN", parent=styles["Heading1"], fontName=FONT_NAME, fontSize=15,
        leading=22, textColor=HexColor("#1D4ED8"), spaceBefore=14, spaceAfter=8,
    )
    question = ParagraphStyle(
        "QuestionCN", parent=styles["Heading2"], fontName=FONT_NAME, fontSize=12,
        leading=18, textColor=HexColor("#0F172A"), spaceBefore=10, spaceAfter=5,
    )
    body = ParagraphStyle(
        "BodyCN", parent=styles["BodyText"], fontName=FONT_NAME, fontSize=10.5,
        leading=17, textColor=HexColor("#1E293B"), spaceAfter=7,
    )
    muted = ParagraphStyle(
        "MutedCN", parent=body, textColor=HexColor("#475569"), leftIndent=5 * mm,
    )

    document = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
    )
    story = [
        Spacer(1, 18 * mm),
        paragraph("Transformer From Scratch Lab", subtitle),
        paragraph("Week 0 Problem Set", title),
        paragraph("先看懂信息怎样流动", subtitle),
        paragraph("课程位置", heading),
        paragraph("本题集不要求实现 attention。目标是让你在 Week 1 前，能准确追踪 token 表、矩阵乘法、点积和 stable softmax 的输入、输出与 shape。", body),
        paragraph("提交物：书面解答、Shape Checker Lab、一个真实错误或主动注入错误的诊断记录，以及闭卷信息流图。", muted),
        paragraph("使用规则：Part A 与 Part B 必须在进入 Lab 前独立完成。Part C 必须在 Lab 后引用自己的输入、输出、测试或评分反馈。", muted),
        PageBreak(),
        paragraph("Part A：概念与推导", heading),
        paragraph("A1. Token 表与 shape（推导）", question),
        paragraph("令 X 的 shape 为 (3, 2)，W 的 shape 为 (2, 4)。写出 X @ W 的 shape；说明输出每一行和每一列的含义；再说明 X[1, 0] 增加 1 时哪些输出元素可能变化以及原因。", body),
        Spacer(1, 28 * mm),
        paragraph("A2. 矩阵乘法不是逐元素乘法（推导）", question),
        paragraph("令 A = [[1, 2], [0, 3], [4, 1]]，B = [[2, 1], [1, 0]]。手算 A @ B 的第 1 行与第 3 行；写出一般元素 (A @ B)[i, j] 的计算规则；解释为什么同一权重矩阵能为每个 token 产生新特征。", body),
        Spacer(1, 32 * mm),
        paragraph("A3. Dot product 与匹配分数（推导）", question),
        paragraph("令 u = [1, 2]，v = [3, -1]，w = [1, 1]。计算 u . v 与 u . w；若 u 是 query，v 和 w 是 key，哪个更匹配？解释为什么该分数仍不是读取权重。", body),
        PageBreak(),
        paragraph("Part A：概念与推导（续）", heading),
        paragraph("A4. Stable softmax（推导）", question),
        paragraph("对 z = [2, 1, 0] 写出 softmax 的三个分量并验证和为 1。证明对任意常数 c，softmax(z) = softmax(z + c)。用该结论解释稳定实现为什么可以在 exponentiation 前减去最大 score。", body),
        Spacer(1, 40 * mm),
        paragraph("Part B：使用边界与全局位置", heading),
        paragraph("B1. 不合法的 shape（反例）", question),
        paragraph("构造两个不能相乘的二维 matrix shape。写出不匹配的内维度、你期望 Shape Checker 报告的错误类别与信息，并解释原始 NumPy 异常为何不足以帮助学习。", body),
        Spacer(1, 24 * mm),
        paragraph("B2. Softmax 的错误轴（反例）", question),
        paragraph("设 score matrix 的 shape 为 (3, 3)，每行是一个 query 对三个 key 的分数。解释沿最后一维与沿第 0 维归一化分别意味着谁在竞争权重；构造一个最小矩阵使二者的解释显著不同。", body),
        PageBreak(),
        paragraph("Part B：使用边界与全局位置（续）", heading),
        paragraph("B3. Week 0 在整体中的位置（全局连接）", question),
        paragraph("画出 token table -> Q/K/V projections -> score matrix -> row-wise weights -> weighted values，并为每个箭头标出 Week 0 已掌握的操作。再用 150–200 字解释：为什么 Week 0 还没有实现 attention，却已为 Week 1 的每一步建立前置能力？", body),
        Spacer(1, 38 * mm),
        paragraph("Part C：Lab 后工程问题", heading),
        paragraph("C1. Shape Checker 的契约（工程设计）", question),
        paragraph("为什么 validate_matrix_shape 与 matrix_product_shape 要拆成两个函数？为每个函数写出一个它单独负责的错误场景。", body),
        paragraph("C2. 一个真实错误（工程诊断）", question),
        paragraph("选择一次 Lab 失败或主动注入错误 shape。记录输入、现象、错误类别、原因假设、最小验证测试，以及修复后理解的变化。", body),
        paragraph("C3. 从 Lab 到 Week 1（工程迁移）", question),
        paragraph("说明 Shape Checker 如何预先防止 Q、K、V 三次投影的错误；再说明它无法防止哪一种 shape 正确但机制仍错误的问题。", body),
        PageBreak(),
        paragraph("闭卷自检与提交清单", heading),
        paragraph("不看材料，用 3–5 分钟解释：一个 (3, 2) token 表经过 (2, 4) 投影后发生了什么；dot product、softmax 与加权和在 Week 1 attention 中分别做什么；以及一种 shape 正确但机制错误的 attention 实现。", body),
        Spacer(1, 15 * mm),
        paragraph("□ Part A 与 Part B 已在 Lab 前完成。<br/>□ Shape Checker 的公开与 hidden tests 已通过。<br/>□ Part C 引用了自己的 Lab 证据。<br/>□ 已记录一个真实错误或主动注入错误的诊断过程。<br/>□ 能闭卷画出 Week 0 到 Week 1 的信息流。", body),
        Spacer(1, 18 * mm),
        paragraph("提交说明", heading),
        paragraph("将书面答案、Lab 运行证据与 feedback 分别保存在 Week 0 对应目录。不要在未完成前查看讲评或参考实现；讲评只用于核对推导和复盘真实错误。", body),
    ]
    document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


if __name__ == "__main__":
    main()
