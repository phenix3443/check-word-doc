from __future__ import annotations

import argparse
from pathlib import Path

from script.config_loader import ConfigLoader

from script.core.engine import DocxLint
from script.reporters.json_reporter import render_json
from script.reporters.markdown_reporter import render_markdown
from script.rules.registry import build_rules


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Docx lint")
    p.add_argument("docx_path", type=str, help="Path to .docx")
    p.add_argument("--config", "-C", required=True, type=str, help="Path to YAML config")
    p.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    p.add_argument("--out", type=str, default="", help="Output file path (optional)")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    docx_path = Path(args.docx_path)
    if not docx_path.exists():
        raise FileNotFoundError(str(docx_path))

    loader = ConfigLoader(args.config)
    config = loader.load()

    rules = build_rules(config)
    issues = DocxLint(rules=rules, config=config).run(str(docx_path))

    if args.format == "json":
        out_text = render_json(issues)
    else:
        out_text = render_markdown(issues)

    if args.out:
        Path(args.out).write_text(out_text, encoding="utf-8")
    else:
        print(out_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

