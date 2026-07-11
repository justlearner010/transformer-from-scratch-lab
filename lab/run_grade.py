from pathlib import Path
import runpy


def main() -> None:
    grader = Path(__file__).resolve().parent.parent / ".grader" / "week_01.py"
    if not grader.exists():
        print("隐藏评分器尚未配置：先完成 Week 1 理论题与公开 smoke test。")
        print("评分器存在时将只输出：当前关卡、失败类别、思考提示与解锁状态。")
        return
    runpy.run_path(str(grader), run_name="__main__")


if __name__ == "__main__":
    main()
