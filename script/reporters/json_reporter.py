from __future__ import annotations

import json
from dataclasses import asdict
from typing import List

from script.core.model import Issue


def render_json(issues: List[Issue]) -> str:
    return json.dumps([asdict(i) for i in issues], ensure_ascii=False, indent=2)

