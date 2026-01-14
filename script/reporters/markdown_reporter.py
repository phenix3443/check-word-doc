from __future__ import annotations

from dataclasses import asdict
from typing import List

from script.core.model import Issue


def render_markdown(issues: List[Issue]) -> str:
    if not issues:
        return "# Docx Lint Report\n\nNo issues found.\n"

    lines = ["# Docx Lint Report", ""]
    for i in issues:
        loc = i.location
        lines.append(f"## {i.code} ({i.severity})")
        lines.append(f"- Location: block_index={loc.block_index}, kind={loc.kind}")
        lines.append(f"- Hint: {loc.hint}")
        lines.append(f"- Message: {i.message}")
        if i.evidence:
            lines.append("- Evidence:")
            for k, v in asdict(i).get("evidence", {}).items():
                lines.append(f"  - {k}: {v}")
        lines.append("")
    return "\n".join(lines)

