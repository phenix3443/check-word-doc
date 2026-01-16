"""
文档元素选择器

类似 CSS 选择器的文档元素查询系统，用于从已标记的文档中筛选特定元素。
"""

import re
from typing import List, Optional, Callable
from dataclasses import dataclass
from script.core.model import Block


@dataclass
class SelectorToken:
    """选择器词法单元"""
    type: str  # class, child, descendant, adjacent, pseudo, attr
    value: str  # 具体的值


class SelectorParser:
    """选择器解析器"""
    
    def __init__(self, selector: str):
        self.selector = selector.strip()
        self.tokens: List[SelectorToken] = []
    
    def parse(self) -> List[SelectorToken]:
        """解析选择器字符串为词法单元列表"""
        # 简化版解析器，支持基本语法
        parts = self.selector.split()
        
        for i, part in enumerate(parts):
            # 子选择器 >
            if part == '>':
                self.tokens.append(SelectorToken('child', '>'))
            # 相邻兄弟选择器 +
            elif part == '+':
                self.tokens.append(SelectorToken('adjacent', '+'))
            # 通用兄弟选择器 ~
            elif part == '~':
                self.tokens.append(SelectorToken('sibling', '~'))
            # 类选择器 .class
            elif part.startswith('.'):
                # 检查是否有伪类
                if ':' in part:
                    class_part, pseudo_part = part.split(':', 1)
                    class_name = class_part[1:]  # 去掉 .
                    self.tokens.append(SelectorToken('class', class_name))
                    self.tokens.append(SelectorToken('pseudo', pseudo_part))
                else:
                    class_name = part[1:]  # 去掉 .
                    self.tokens.append(SelectorToken('class', class_name))
            # 属性选择器 [attr="value"]
            elif part.startswith('[') and part.endswith(']'):
                attr_expr = part[1:-1]  # 去掉 [ ]
                self.tokens.append(SelectorToken('attr', attr_expr))
            # 如果前一个不是操作符，添加后代选择器
            elif i > 0 and self.tokens and self.tokens[-1].type not in ['child', 'adjacent', 'sibling']:
                self.tokens.append(SelectorToken('descendant', ' '))
        
        return self.tokens


class Selector:
    """文档元素选择器"""
    
    def __init__(self, blocks: List[Block]):
        """初始化选择器
        
        Args:
            blocks: 已经被 Classifier 标记的文档元素列表
        """
        self.blocks = blocks
        self._build_relationships()
    
    def _build_relationships(self):
        """构建元素之间的关系（父子、兄弟等）"""
        # 为每个 block 添加索引
        for i, block in enumerate(self.blocks):
            block.index = i
        
        # TODO: 如果需要支持父子关系，需要在 Classifier 阶段记录
        # 目前简化处理，只支持文档级别的扁平结构
    
    def select(self, selector: str) -> List[Block]:
        """选择所有匹配的元素
        
        Args:
            selector: CSS 风格的选择器字符串
            
        Returns:
            匹配的元素列表
        """
        # 解析选择器
        parser = SelectorParser(selector)
        tokens = parser.parse()
        
        if not tokens:
            return []
        
        # 从所有 blocks 开始匹配
        results = self.blocks[:]
        
        # 逐个处理 token
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == 'class':
                # 类选择器：筛选具有指定 class 的元素
                results = [b for b in results if token.value in b.classes]
            
            elif token.type == 'pseudo':
                # 伪类选择器
                results = self._apply_pseudo(results, token.value)
            
            elif token.type == 'child':
                # 子选择器：下一个 token 必须是直接子元素
                # 简化实现：暂不支持真正的父子关系
                i += 1
                if i < len(tokens):
                    next_token = tokens[i]
                    if next_token.type == 'class':
                        results = [b for b in results if next_token.value in b.classes]
            
            elif token.type == 'descendant':
                # 后代选择器：下一个 token 可以是任意后代
                # 简化实现：与子选择器相同
                pass
            
            elif token.type == 'adjacent':
                # 相邻兄弟选择器：下一个 token 必须是紧邻的兄弟
                i += 1
                if i < len(tokens):
                    next_token = tokens[i]
                    if next_token.type == 'class':
                        # 找到每个结果的下一个兄弟
                        adjacent_results = []
                        for block in results:
                            next_block = self._get_next_sibling(block)
                            if next_block and next_token.value in next_block.classes:
                                adjacent_results.append(next_block)
                        results = adjacent_results
            
            elif token.type == 'attr':
                # 属性选择器
                results = self._apply_attr_filter(results, token.value)
            
            i += 1
        
        return results
    
    def select_one(self, selector: str) -> Optional[Block]:
        """选择第一个匹配的元素
        
        Args:
            selector: CSS 风格的选择器字符串
            
        Returns:
            第一个匹配的元素，如果没有则返回 None
        """
        results = self.select(selector)
        return results[0] if results else None
    
    def exists(self, selector: str) -> bool:
        """检查是否存在匹配的元素
        
        Args:
            selector: CSS 风格的选择器字符串
            
        Returns:
            是否存在匹配的元素
        """
        return len(self.select(selector)) > 0
    
    def count(self, selector: str) -> int:
        """统计匹配的元素数量
        
        Args:
            selector: CSS 风格的选择器字符串
            
        Returns:
            匹配的元素数量
        """
        return len(self.select(selector))
    
    def _apply_pseudo(self, blocks: List[Block], pseudo: str) -> List[Block]:
        """应用伪类过滤
        
        Args:
            blocks: 待过滤的元素列表
            pseudo: 伪类字符串（如 "first", "last", "nth(2)"）
            
        Returns:
            过滤后的元素列表
        """
        if not blocks:
            return []
        
        if pseudo == 'first':
            return [blocks[0]]
        
        elif pseudo == 'last':
            return [blocks[-1]]
        
        elif pseudo.startswith('nth(') and pseudo.endswith(')'):
            # 提取索引
            index_str = pseudo[4:-1]
            try:
                index = int(index_str)
                if 0 <= index < len(blocks):
                    return [blocks[index]]
                return []
            except ValueError:
                return []
        
        elif pseudo.startswith('nth-of-type(') and pseudo.endswith(')'):
            # nth-of-type: 按类型分组后取第 n 个
            # 简化实现：与 nth 相同
            index_str = pseudo[12:-1]
            try:
                index = int(index_str)
                if 0 <= index < len(blocks):
                    return [blocks[index]]
                return []
            except ValueError:
                return []
        
        return blocks
    
    def _apply_attr_filter(self, blocks: List[Block], attr_expr: str) -> List[Block]:
        """应用属性过滤
        
        Args:
            blocks: 待过滤的元素列表
            attr_expr: 属性表达式（如 'type="table"'）
            
        Returns:
            过滤后的元素列表
        """
        # 解析属性表达式
        if '=' in attr_expr:
            attr_name, attr_value = attr_expr.split('=', 1)
            attr_name = attr_name.strip()
            attr_value = attr_value.strip().strip('"').strip("'")
            
            # 目前只支持 type 属性
            if attr_name == 'type':
                from script.core.model import ParagraphBlock, TableBlock
                if attr_value == 'table':
                    return [b for b in blocks if isinstance(b, TableBlock)]
                elif attr_value == 'paragraph':
                    return [b for b in blocks if isinstance(b, ParagraphBlock)]
        
        return blocks
    
    def _get_next_sibling(self, block: Block) -> Optional[Block]:
        """获取下一个兄弟元素
        
        Args:
            block: 当前元素
            
        Returns:
            下一个兄弟元素，如果没有则返回 None
        """
        try:
            current_index = self.blocks.index(block)
            if current_index + 1 < len(self.blocks):
                return self.blocks[current_index + 1]
        except ValueError:
            pass
        return None
    
    def _get_prev_sibling(self, block: Block) -> Optional[Block]:
        """获取前一个兄弟元素
        
        Args:
            block: 当前元素
            
        Returns:
            前一个兄弟元素，如果没有则返回 None
        """
        try:
            current_index = self.blocks.index(block)
            if current_index > 0:
                return self.blocks[current_index - 1]
        except ValueError:
            pass
        return None
