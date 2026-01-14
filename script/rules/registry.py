from __future__ import annotations

from typing import Any, Dict, List, Type

from core.rule import Rule
from rules.base_rules import (
    AttachmentsRule,
    CaptionsRule,
    ChineseQuoteMatchingRule,
    ChineseSpacingRule,
    ConsecutiveEmptyLinesRule,
    CoverRule,
    EmptyLinesRule,
    EnglishQuotesRule,
    FigureListRule,
    FigureListPageContinuityRule,
    FigureListPageAccuracyRule,
    FootersRule,
    HeadingNumberingRule,
    HeadingsRule,
    HeadersRule,
    PageNumbersRule,
    ParagraphsRule,
    ParagraphPunctuationRule,
    ReferencesHeadingRule,
    ReferencesCitationRule,
    ReferencesHeadingLevelRule,
    StructureMinBodyRule,
    TableListRule,
    TableListPageAccuracyRule,
    TocPresenceRule,
    TocPageContinuityRule,
    TocPageAccuracyRule,
)
from .smoke import SmokeRule
from .table import KeyValueTableRule, TableCaptionPairRule, TableDimensionsRule


_RULES: Dict[str, Type[Rule]] = {
    SmokeRule.id: SmokeRule,
    TableDimensionsRule.id: TableDimensionsRule,
    TableCaptionPairRule.id: TableCaptionPairRule,
    KeyValueTableRule.id: KeyValueTableRule,
    StructureMinBodyRule.id: StructureMinBodyRule,
    TocPresenceRule.id: TocPresenceRule,
    TocPageContinuityRule.id: TocPageContinuityRule,
    TocPageAccuracyRule.id: TocPageAccuracyRule,
    FigureListPageContinuityRule.id: FigureListPageContinuityRule,
    FigureListPageAccuracyRule.id: FigureListPageAccuracyRule,
    TableListPageAccuracyRule.id: TableListPageAccuracyRule,
    ReferencesHeadingRule.id: ReferencesHeadingRule,
    ReferencesCitationRule.id: ReferencesCitationRule,
    ReferencesHeadingLevelRule.id: ReferencesHeadingLevelRule,
    EmptyLinesRule.id: EmptyLinesRule,
    ParagraphPunctuationRule.id: ParagraphPunctuationRule,
    ChineseSpacingRule.id: ChineseSpacingRule,
    EnglishQuotesRule.id: EnglishQuotesRule,
    ChineseQuoteMatchingRule.id: ChineseQuoteMatchingRule,
    ConsecutiveEmptyLinesRule.id: ConsecutiveEmptyLinesRule,
    HeadingNumberingRule.id: HeadingNumberingRule,
    CoverRule.id: CoverRule,
    FigureListRule.id: FigureListRule,
    TableListRule.id: TableListRule,
    ParagraphsRule.id: ParagraphsRule,
    HeadingsRule.id: HeadingsRule,
    CaptionsRule.id: CaptionsRule,
    AttachmentsRule.id: AttachmentsRule,
    HeadersRule.id: HeadersRule,
    FootersRule.id: FootersRule,
    PageNumbersRule.id: PageNumbersRule,
}


def build_rules(config: dict) -> List[Rule]:
    rules_cfg = config.get("rules", [])
    if not isinstance(rules_cfg, list):
        return []

    rules: List[Rule] = []
    for item in rules_cfg:
        if not isinstance(item, dict):
            continue
        rule_id = item.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            continue
        enabled = item.get("enabled", True)
        if enabled is False:
            continue
        params = item.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            params = {}

        cls = _RULES.get(rule_id)
        if cls is None:
            continue

        rules.append(cls(**_filter_kwargs(cls, params)))

    return rules


def _filter_kwargs(cls: Type[Any], params: dict) -> dict:
    allowed = set(getattr(cls, "__init__").__code__.co_varnames)
    allowed.discard("self")
    return {k: v for k, v in params.items() if k in allowed}

