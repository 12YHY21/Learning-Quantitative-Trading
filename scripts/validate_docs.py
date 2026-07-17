from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPOSITORY_ROOT / "docs"
ALLOWED_ALERTS = {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}


def outside_code_blocks(text: str) -> str:
    return re.sub(r"```[\s\S]*?```", "", text)


def validate() -> list[str]:
    errors: list[str] = []
    chapters = sorted(DOCS_ROOT.glob("[0-9][0-9]-*.md"))
    expected_prefixes = [f"{number:02d}-" for number in range(19)]
    actual_prefixes = [path.name[:3] for path in chapters]

    if actual_prefixes != expected_prefixes:
        errors.append(
            f"章节应为 00～18 各一篇，实际前缀为: {actual_prefixes}"
        )

    for path in sorted(DOCS_ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        visible = outside_code_blocks(text)

        if not text.startswith("# "):
            errors.append(f"{path.name}: 第一行必须是 H1 标题")
        if text.count("```") % 2:
            errors.append(f"{path.name}: 代码围栏数量不成对")
        if "[[" in visible:
            errors.append(f"{path.name}: 仍包含 GitHub 不支持的 Obsidian 双链")
        if re.search(r"[A-Za-z]:\\", text):
            errors.append(f"{path.name}: 仍包含本机绝对 Windows 路径")

        for alert in re.findall(r"(?m)^> \[!([A-Za-z-]+)\]", visible):
            if alert not in ALLOWED_ALERTS:
                errors.append(f"{path.name}: GitHub 不支持提示框 {alert}")

        for target in re.findall(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]+)?\)", visible):
            if target.startswith(("http://", "https://")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{path.name}: 相对链接不存在: {target}")

    return errors


if __name__ == "__main__":
    validation_errors = validate()
    if validation_errors:
        for validation_error in validation_errors:
            print(f"ERROR: {validation_error}")
        raise SystemExit(1)
    print("Documentation validation passed.")
