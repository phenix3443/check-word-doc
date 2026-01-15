from __future__ import annotations

from typing import List, Optional

from docx import Document

from .context import Context
from .model import Issue
from .rule import FinalizeRule, Rule
from .walker import Walker


class DocxLint:
    def __init__(self, rules: List[Rule], config: dict):
        self.rules = rules
        self.config = config

    def run(self, docx_path: str) -> List[Issue]:
        """运行文档检查
        
        根据配置格式自动选择检查方式：
        - 如果配置包含 classifiers/styles，使用 class-based 检查
        - 否则使用传统的 rules 检查
        """
        doc = Document(docx_path)
        blocks = list(Walker().iter_blocks(doc))
        
        # 检查是否使用 class-based 格式
        if self._is_class_based_config():
            return self._run_class_based(doc, blocks)
        else:
            return self._run_rule_based(doc, blocks)
    
    def _is_class_based_config(self) -> bool:
        """检查是否使用 class-based 配置格式"""
        document_config = self.config.get('document', {})
        return 'classifiers' in document_config or 'styles' in document_config
    
    def _run_class_based(self, doc: Document, blocks: list) -> List[Issue]:
        """使用 class-based 方式进行检查"""
        from .classifier import Classifier
        from .style_checker import StyleChecker
        
        document_config = self.config.get('document', {})
        
        # 阶段 1: 语义标注（给元素添加 class）
        if 'classifiers' in document_config:
            classifier = Classifier(document_config['classifiers'])
            blocks = classifier.classify(blocks)
        
        # 阶段 2: 样式检查
        issues = []
        if 'styles' in document_config:
            defaults = document_config.get('defaults')
            style_checker = StyleChecker(document_config['styles'], defaults)
            issues = style_checker.check(blocks)
        
        return issues
    
    def _run_rule_based(self, doc: Document, blocks: list) -> List[Issue]:
        """使用传统 rule-based 方式进行检查"""
        ctx = Context(doc=doc, config=self.config, blocks=blocks)

        issues: List[Issue] = []

        for block in blocks:
            for rule in self.rules:
                if rule.applies_to(block, ctx):
                    issues.extend(rule.check(block, ctx))

        for rule in self.rules:
            if isinstance(rule, FinalizeRule):
                issues.extend(rule.finalize(ctx))

        return issues

