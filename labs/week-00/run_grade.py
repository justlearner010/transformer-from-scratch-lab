from pathlib import Path
import runpy


def main() -> None:
    grader = Path(__file__).resolve().parents[2] / ".grader" / "week_00.py"
    if not grader.exists():
        print("隐藏评分器尚未配置：先完成公开 smoke test 和关卡 1。")
        print("评分器配置后只输出失败类别、思考提示和解锁状态。")
        return
    runpy.run_path(str(grader), run_name="__main__")


if __name__ == "__main__":
    main()
