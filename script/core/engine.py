from __future__ import annotations

from typing import List

from docx import Document

from .model import Issue
from .walker import Walker


class DocxLint:
    def __init__(self, config: dict):
        self.config = config

    def run(self, docx_path: str) -> List[Issue]:
        """运行文档检查
        
        使用 class-based 方式进行检查：
        1. 语义标注（Classifier）：给文档元素添加 class
        2. 样式检查（StyleChecker）：检查每个 class 的样式是否符合要求
        """
        from .classifier import Classifier
        from .style_checker import StyleChecker
        
        doc = Document(docx_path)
        blocks = list(Walker().iter_blocks(doc))
        
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

