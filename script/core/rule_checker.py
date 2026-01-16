"""
RuleChecker - 内容规则检查器

支持基于 Selector 的内容验证规则，包括：
- 模式匹配（pattern）
- 存在性检查（exists）
- 数量检查（count）
- 跨元素数量比较（count_equals）
"""

import re
from typing import List, Dict, Any, Optional, Union
from script.core.model import ParagraphBlock, TableBlock, Issue, Location, Severity
from script.core.selector import Selector

# 类型别名
Block = Union[ParagraphBlock, TableBlock]


class RuleChecker:
    """内容规则检查器"""
    
    def __init__(self, rules: List[Dict[str, Any]], blocks: List[Block]):
        """
        初始化规则检查器
        
        Args:
            rules: 规则配置列表
            blocks: 已分类的文档块列表
        """
        self.rules = rules
        self.blocks = blocks
        self.selector = Selector(blocks)
        self.issues: List[Issue] = []
    
    def check(self) -> List[Issue]:
        """
        执行所有规则检查
        
        Returns:
            问题列表
        """
        self.issues = []
        
        for rule in self.rules:
            self._check_rule(rule)
        
        return self.issues
    
    def _check_rule(self, rule: Dict[str, Any]) -> None:
        """
        检查单条规则
        
        Args:
            rule: 规则配置
        """
        rule_id = rule.get('id', 'unknown')
        selector_str = rule.get('selector')
        condition = rule.get('condition')
        check = rule.get('check', {})
        severity = rule.get('severity', 'warning')
        message = rule.get('message', f'Rule {rule_id} failed')
        
        if not selector_str:
            return
        
        # 检查条件（如果有）
        if condition and not self._check_condition(condition):
            return
        
        # 选择目标元素
        target_blocks = self.selector.select(selector_str)
        
        # 执行检查
        if 'pattern' in check:
            self._check_pattern(target_blocks, check['pattern'], rule_id, severity, message)
        elif 'exists' in check:
            self._check_exists(target_blocks, check['exists'], rule_id, severity, message)
        elif 'count' in check:
            self._check_count(target_blocks, check['count'], rule_id, severity, message)
        elif 'count_equals' in check:
            self._check_count_equals(target_blocks, check['count_equals'], rule_id, severity, message)
    
    def _check_condition(self, condition: Dict[str, Any]) -> bool:
        """
        检查规则条件
        
        Args:
            condition: 条件配置
            
        Returns:
            条件是否满足
        """
        if 'selector' in condition:
            selector_str = condition['selector']
            blocks = self.selector.select(selector_str)
            
            # 检查模式
            if 'pattern' in condition:
                pattern = condition['pattern']
                for block in blocks:
                    text = self._get_block_text(block)
                    if re.search(pattern, text):
                        return True
                return False
            
            # 检查数量
            if 'count' in condition:
                count_expr = condition['count']
                return self._evaluate_count_expression(len(blocks), count_expr)
        
        return True
    
    def _check_pattern(self, blocks: List[Block], pattern: str, 
                      rule_id: str, severity: str, message: str) -> None:
        """
        检查模式匹配
        
        Args:
            blocks: 目标块列表
            pattern: 正则表达式模式
            rule_id: 规则ID
            severity: 严重程度
            message: 错误消息
        """
        for block in blocks:
            text = self._get_block_text(block)
            if not re.match(pattern, text):
                location = Location(
                    block_index=block.index,
                    kind='paragraph' if isinstance(block, ParagraphBlock) else 'table',
                    hint=text[:50]
                )
                self.issues.append(Issue(
                    code=rule_id,
                    severity=Severity(severity.lower()),
                    message=message,
                    location=location,
                    evidence={'expected': f"Pattern: {pattern}", 'actual': text}
                ))
    
    def _check_exists(self, blocks: List[Block], should_exist: bool,
                     rule_id: str, severity: str, message: str) -> None:
        """
        检查存在性
        
        Args:
            blocks: 目标块列表
            should_exist: 是否应该存在
            rule_id: 规则ID
            severity: 严重程度
            message: 错误消息
        """
        exists = len(blocks) > 0
        if exists != should_exist:
            location = Location(
                block_index=-1,
                kind='document',
                hint='existence check'
            )
            self.issues.append(Issue(
                code=rule_id,
                severity=Severity(severity.lower()),
                message=message,
                location=location,
                evidence={'expected': f"Exists: {should_exist}", 'actual': f"Exists: {exists}"}
            ))
    
    def _check_count(self, blocks: List[Block], count_expr: str,
                    rule_id: str, severity: str, message: str) -> None:
        """
        检查数量
        
        Args:
            blocks: 目标块列表
            count_expr: 数量表达式（如 ">= 2", "== 3"）
            rule_id: 规则ID
            severity: 严重程度
            message: 错误消息
        """
        actual_count = len(blocks)
        if not self._evaluate_count_expression(actual_count, count_expr):
            location = Location(
                block_index=-1,
                kind='document',
                hint='count check'
            )
            self.issues.append(Issue(
                code=rule_id,
                severity=Severity(severity.lower()),
                message=message,
                location=location,
                evidence={'expected': f"Count {count_expr}", 'actual': f"Count: {actual_count}"}
            ))
    
    def _check_count_equals(self, blocks: List[Block], config: Dict[str, Any],
                           rule_id: str, severity: str, message: str) -> None:
        """
        检查跨元素数量比较
        
        Args:
            blocks: 目标块列表
            config: 比较配置
            rule_id: 规则ID
            severity: 严重程度
            message: 错误消息
        """
        # 获取目标元素数量
        target_count = len(blocks)
        
        # 获取参考元素
        ref_selector = config.get('selector')
        if not ref_selector:
            return
        
        ref_blocks = self.selector.select(ref_selector)
        
        # 提取参考数量
        extract_pattern = config.get('extract')
        method = config.get('method', 'count')
        
        if method == 'count':
            # 直接使用元素数量
            ref_count = len(ref_blocks)
        elif method == 'max' and extract_pattern:
            # 从文本中提取数字，取最大值
            ref_count = 0
            for block in ref_blocks:
                text = self._get_block_text(block)
                numbers = re.findall(extract_pattern, text)
                if numbers:
                    max_num = max(int(n) for n in numbers)
                    ref_count = max(ref_count, max_num)
        elif method == 'sum' and extract_pattern:
            # 从文本中提取数字，求和
            ref_count = 0
            for block in ref_blocks:
                text = self._get_block_text(block)
                numbers = re.findall(extract_pattern, text)
                ref_count += len(numbers)
        else:
            return
        
        # 比较数量
        if target_count != ref_count:
            location = Location(
                block_index=-1,
                kind='document',
                hint='count comparison'
            )
            self.issues.append(Issue(
                code=rule_id,
                severity=Severity(severity.lower()),
                message=message,
                location=location,
                evidence={'expected': f"Count: {ref_count}", 'actual': f"Count: {target_count}"}
            ))
    
    def _evaluate_count_expression(self, count: int, expr: str) -> bool:
        """
        评估数量表达式
        
        Args:
            count: 实际数量
            expr: 表达式（如 ">= 2", "== 3", "< 5"）
            
        Returns:
            表达式是否成立
        """
        expr = expr.strip()
        
        # 解析表达式
        if expr.startswith('>='):
            target = int(expr[2:].strip())
            return count >= target
        elif expr.startswith('<='):
            target = int(expr[2:].strip())
            return count <= target
        elif expr.startswith('>'):
            target = int(expr[1:].strip())
            return count > target
        elif expr.startswith('<'):
            target = int(expr[1:].strip())
            return count < target
        elif expr.startswith('=='):
            target = int(expr[2:].strip())
            return count == target
        elif expr.startswith('!='):
            target = int(expr[2:].strip())
            return count != target
        else:
            # 默认为相等比较
            try:
                target = int(expr)
                return count == target
            except ValueError:
                return False
    
    def _get_block_text(self, block: Block) -> str:
        """
        获取块的文本内容
        
        Args:
            block: 文档块
            
        Returns:
            文本内容
        """
        if hasattr(block, 'paragraph') and block.paragraph:
            return block.paragraph.text
        elif hasattr(block, 'table') and block.table:
            # 对于表格，返回所有单元格的文本
            texts = []
            for row in block.table.rows:
                for cell in row.cells:
                    texts.append(cell.text)
            return ' '.join(texts)
        return ''
