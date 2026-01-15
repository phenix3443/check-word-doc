"""文档元素分类器

根据配置规则给文档元素添加 class 属性，类似 HTML 的语义标签。
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from script.core.model import Block, ParagraphBlock, TableBlock


class Matcher(ABC):
    """匹配器基类"""

    @abstractmethod
    def match(self, block: Block, context: List[Block]) -> bool:
        """判断元素是否匹配

        Args:
            block: 要匹配的元素
            context: 所有元素列表（用于相对位置匹配）

        Returns:
            True 如果匹配，否则 False
        """
        pass


class PositionMatcher(Matcher):
    """绝对位置匹配器

    匹配文档中固定位置的元素。

    Examples:
        position: 0  # 第一个元素
        position: -1  # 最后一个元素
        position: "first"  # 第一个（字符串形式）
        position: "last"  # 最后一个（字符串形式）
    """

    def __init__(self, position):
        self.position = position

    def match(self, block: Block, context: List[Block]) -> bool:
        # 支持字符串形式的位置
        if isinstance(self.position, str):
            if self.position == "first":
                target_index = 0
            elif self.position == "last":
                target_index = len(context) - 1
            else:
                return False
        # 支持数字索引
        elif self.position < 0:
            target_index = len(context) + self.position
        else:
            target_index = self.position

        return block.index == target_index


class PatternMatcher(Matcher):
    """内容模式匹配器

    根据段落内容匹配（仅支持 ParagraphBlock）。

    Examples:
        pattern: "^摘要[:：]"  # 以"摘要："开头
        pattern: "^\\d+\\."     # 以数字和点开头
    """

    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    def match(self, block: Block, context: List[Block]) -> bool:
        if not isinstance(block, ParagraphBlock):
            return False

        text = block.paragraph.text or ""
        return bool(self.pattern.match(text))


class TypeMatcher(Matcher):
    """类型匹配器

    匹配特定类型的元素。

    Examples:
        type: paragraph
        type: table
    """

    def __init__(self, element_type: str):
        self.element_type = element_type

    def match(self, block: Block, context: List[Block]) -> bool:
        if self.element_type == "paragraph":
            return isinstance(block, ParagraphBlock)
        elif self.element_type == "table":
            return isinstance(block, TableBlock)
        return False


class RelativeMatcher(Matcher):
    """相对位置匹配器

    相对于其他元素定位。

    Examples:
        after: {class: title}
        before: {position: 5}
        offset: 0  # 紧接着（默认）
    """

    def __init__(self, anchor_def: Dict[str, Any], direction: str, offset: int = 0):
        """
        Args:
            anchor_def: 锚点定义（如 {class: 'title'} 或 {position: 0}）
            direction: 方向（'after' 或 'before'）
            offset: 偏移量（0 表示紧接着）
        """
        self.anchor_def = anchor_def
        self.direction = direction
        self.offset = offset

    def match(self, block: Block, context: List[Block]) -> bool:
        # 查找锚点
        anchor = self._find_anchor(context)
        if anchor is None:
            return False

        # 计算目标位置
        if self.direction == "after":
            target_index = anchor.index + 1 + self.offset
        else:  # before
            target_index = anchor.index - 1 - self.offset

        return block.index == target_index

    def _find_anchor(self, context: List[Block]) -> Optional[Block]:
        """查找锚点元素"""
        if "class" in self.anchor_def:
            # 通过 class 查找
            class_name = self.anchor_def["class"]
            for block in context:
                if block.has_class(class_name):
                    return block

        elif "position" in self.anchor_def:
            # 通过绝对位置查找
            position = self.anchor_def["position"]
            if position < 0:
                position = len(context) + position

            for block in context:
                if block.index == position:
                    return block

        elif "pattern" in self.anchor_def:
            # 通过内容模式查找
            pattern = re.compile(self.anchor_def["pattern"])
            for block in context:
                if isinstance(block, ParagraphBlock):
                    text = block.paragraph.text or ""
                    if pattern.match(text):
                        return block

        return None


class RangeMatcher(Matcher):
    """范围匹配器

    匹配两个锚点之间的元素。

    Examples:
        range:
          after: {class: title}
          before: {pattern: "^摘要[:：]"}
    """

    def __init__(self, after_anchor: Dict[str, Any], before_anchor: Dict[str, Any]):
        self.after_anchor = after_anchor
        self.before_anchor = before_anchor

    def match(self, block: Block, context: List[Block]) -> bool:
        # 查找两个锚点
        after_block = self._find_anchor(self.after_anchor, context)
        before_block = self._find_anchor(self.before_anchor, context)

        if after_block is None or before_block is None:
            return False

        # 检查是否在范围内（不包括锚点本身）
        return after_block.index < block.index < before_block.index

    def _find_anchor(self, anchor_def: Dict[str, Any], context: List[Block]) -> Optional[Block]:
        """查找锚点元素"""
        if "class" in anchor_def:
            class_name = anchor_def["class"]
            for block in context:
                if block.has_class(class_name):
                    return block

        elif "position" in anchor_def:
            position = anchor_def["position"]
            if position < 0:
                position = len(context) + position

            for block in context:
                if block.index == position:
                    return block

        elif "pattern" in anchor_def:
            pattern = re.compile(anchor_def["pattern"])
            for block in context:
                if isinstance(block, ParagraphBlock):
                    text = block.paragraph.text or ""
                    if pattern.match(text):
                        return block

        return None


class RelativePositionInRangeMatcher(Matcher):
    """相对于父区域的位置匹配器

    在指定的 parent_range 范围内，匹配相对位置的元素。

    Examples:
        position: first   # 范围内的第一个
        position: last    # 范围内的最后一个
        position: middle  # 范围内的中间元素（不包括首尾）
        position: 0       # 范围内的第 0 个
    """

    def __init__(self, position, parent_range: List[Block]):
        """
        Args:
            position: 相对位置（'first', 'last', 'middle', 或数字索引）
            parent_range: 父区域的块列表
        """
        self.position = position
        self.parent_range = parent_range

    def match(self, block: Block, context: List[Block]) -> bool:
        # 检查 block 是否在 parent_range 中
        if block not in self.parent_range:
            return False

        # 根据位置类型匹配
        if isinstance(self.position, str):
            if self.position == "first":
                return block == self.parent_range[0]
            elif self.position == "last":
                return block == self.parent_range[-1]
            elif self.position == "middle":
                # 中间元素（不包括首尾）
                if len(self.parent_range) <= 2:
                    return False
                return block in self.parent_range[1:-1]
            else:
                return False

        # 数字索引（相对于 parent_range）
        elif isinstance(self.position, int):
            if self.position < 0:
                target_idx = len(self.parent_range) + self.position
            else:
                target_idx = self.position

            if 0 <= target_idx < len(self.parent_range):
                return block == self.parent_range[target_idx]

        return False


class Classifier:
    """文档元素分类器

    根据配置规则给文档元素添加 class 属性。

    工作流程：
    1. 遍历所有规则
    2. 对每条规则，遍历所有元素
    3. 如果元素匹配规则，添加对应的 class

    Examples:
        >>> rules = [
        ...     {
        ...         'class': 'title',
        ...         'match': {'type': 'paragraph', 'position': 0}
        ...     },
        ...     {
        ...         'class': 'abstract',
        ...         'match': {'type': 'paragraph', 'pattern': '^摘要[:：]'}
        ...     }
        ... ]
        >>> classifier = Classifier(rules)
        >>> blocks = classifier.classify(blocks)
    """

    def __init__(self, rules: List[Dict[str, Any]]):
        """
        Args:
            rules: classifiers 配置列表
        
        Raises:
            ValueError: 如果检测到循环依赖
        """
        self.rules = rules
        # 构建规则索引：class_name -> rule
        self.rule_index = {rule["class"]: rule for rule in rules}
        # 记录已处理的规则（避免重复处理）
        self.processed = set()
        
        # 检查循环依赖
        self._check_circular_dependencies()

    def classify(self, blocks: List[Block]) -> List[Block]:
        """给所有元素添加 class 属性

        使用递归依赖解析：
        1. 分析每条规则的依赖（引用的 class）
        2. 递归确保依赖的规则先被处理
        3. 使用记忆化避免重复处理

        Args:
            blocks: 文档元素列表

        Returns:
            添加了 class 的元素列表（原地修改）
        """
        # 清空处理记录
        self.processed.clear()

        # 递归处理每条规则
        for rule in self.rules:
            self._process_rule_with_dependencies(rule, blocks)

        return blocks

    def _process_rule_with_dependencies(self, rule: Dict[str, Any], blocks: List[Block]) -> None:
        """递归处理规则及其依赖

        Args:
            rule: 规则配置
            blocks: 文档元素列表
        """
        class_name = rule["class"]

        # 如果已处理，跳过
        if class_name in self.processed:
            return

        # 提取依赖的 class
        dependencies = self._extract_dependencies(rule)

        # 递归处理依赖
        for dep_class in dependencies:
            if dep_class in self.rule_index and dep_class not in self.processed:
                dep_rule = self.rule_index[dep_class]
                self._process_rule_with_dependencies(dep_rule, blocks)

        # 处理当前规则
        self._apply_rule(rule, blocks)

        # 标记为已处理
        self.processed.add(class_name)

    def _extract_dependencies(self, rule: Dict[str, Any]) -> List[str]:
        """提取规则依赖的 class

        Args:
            rule: 规则配置

        Returns:
            依赖的 class 名称列表
        """
        dependencies = []
        match_config = rule.get("match", {})

        # 检查 after/before 中的 class 引用
        if "after" in match_config and isinstance(match_config["after"], dict):
            if "class" in match_config["after"]:
                dependencies.append(match_config["after"]["class"])

        if "before" in match_config and isinstance(match_config["before"], dict):
            if "class" in match_config["before"]:
                dependencies.append(match_config["before"]["class"])

        # 检查 range 中的 class 引用
        if "range" in match_config:
            range_config = match_config["range"]
            if "after" in range_config and isinstance(range_config["after"], dict):
                if "class" in range_config["after"]:
                    dependencies.append(range_config["after"]["class"])
            if "before" in range_config and isinstance(range_config["before"], dict):
                if "class" in range_config["before"]:
                    dependencies.append(range_config["before"]["class"])

        return dependencies

    def _check_circular_dependencies(self) -> None:
        """检查规则之间是否存在循环依赖
        
        使用 DFS + 三色标记法检测有向图中的环：
        - 白色（未访问）：节点还未被访问
        - 灰色（访问中）：节点正在被访问（在当前 DFS 路径上）
        - 黑色（已完成）：节点及其所有后继节点都已访问完成
        
        如果在 DFS 过程中遇到灰色节点，说明存在环。
        
        Raises:
            ValueError: 如果检测到循环依赖
        """
        # 三种状态
        WHITE = 0  # 未访问
        GRAY = 1   # 访问中（在当前路径上）
        BLACK = 2  # 已完成
        
        # 记录每个节点的状态
        state = {rule["class"]: WHITE for rule in self.rules}
        
        def dfs(class_name: str, path: List[str]) -> None:
            """DFS 访问节点
            
            Args:
                class_name: 当前访问的 class
                path: 当前 DFS 路径（用于报告循环）
            
            Raises:
                ValueError: 如果检测到循环
            """
            # 标记为访问中
            state[class_name] = GRAY
            path.append(class_name)
            
            # 获取依赖
            if class_name in self.rule_index:
                rule = self.rule_index[class_name]
                dependencies = self._extract_dependencies(rule)
                
                for dep_class in dependencies:
                    # 忽略未定义的依赖（可能是外部引用）
                    if dep_class not in state:
                        continue
                    
                    if state[dep_class] == GRAY:
                        # 发现环：dep_class 在当前路径上
                        cycle_start = path.index(dep_class)
                        cycle = path[cycle_start:] + [dep_class]
                        cycle_str = " -> ".join(cycle)
                        raise ValueError(
                            f"检测到循环依赖: {cycle_str}\n"
                            f"规则 '{class_name}' 依赖 '{dep_class}'，但 '{dep_class}' "
                            f"（直接或间接）也依赖 '{class_name}'"
                        )
                    
                    if state[dep_class] == WHITE:
                        # 递归访问未访问的依赖
                        dfs(dep_class, path)
            
            # 标记为已完成
            path.pop()
            state[class_name] = BLACK
        
        # 对所有未访问的节点执行 DFS
        for rule in self.rules:
            class_name = rule["class"]
            if state[class_name] == WHITE:
                dfs(class_name, [])

    def _apply_rule(self, rule: Dict[str, Any], blocks: List[Block]) -> None:
        """应用单条规则"""
        class_name = rule["class"]
        match_config = rule["match"]

        # 构建匹配器列表
        matchers = self._build_matchers(match_config)

        # 查找匹配的块
        matched_blocks = []
        for block in blocks:
            if all(matcher.match(block, blocks) for matcher in matchers):
                block.add_class(class_name)
                matched_blocks.append(block)

        # 如果有 children 配置，处理子元素
        if "children" in rule and matched_blocks:
            self._apply_children_rules(rule["children"], matched_blocks, blocks)

    def _apply_children_rules(
        self,
        children_rules: List[Dict[str, Any]],
        parent_blocks: List[Block],
        all_blocks: List[Block],
    ) -> None:
        """应用子元素规则

        Args:
            children_rules: 子元素规则列表
            parent_blocks: 父区域匹配到的块列表
            all_blocks: 所有块列表
        """
        # 对每个父区域，应用子规则
        for parent_block in parent_blocks:
            # 确定父区域的范围
            # 如果父区域只有一个块，范围就是这个块
            # 如果有多个块，需要根据实际情况确定范围

            # 这里简化处理：假设父区域是连续的块
            # 找到父区域的起始和结束索引
            parent_indices = [b.index for b in parent_blocks]
            start_idx = min(parent_indices)
            end_idx = max(parent_indices)

            # 获取父区域范围内的所有块
            parent_range = [b for b in all_blocks if start_idx <= b.index <= end_idx]

            # 应用每条子规则
            for child_rule in children_rules:
                self._apply_child_rule(child_rule, parent_range, all_blocks)

    def _apply_child_rule(
        self, rule: Dict[str, Any], parent_range: List[Block], all_blocks: List[Block]
    ) -> None:
        """应用单条子元素规则

        Args:
            rule: 子元素规则
            parent_range: 父区域范围内的块
            all_blocks: 所有块列表
        """
        class_name = rule["class"]
        match_config = rule["match"]

        # 构建匹配器（相对于父区域）
        matchers = self._build_matchers_for_children(match_config, parent_range)

        # 在父区域范围内查找匹配的块
        for block in parent_range:
            if all(matcher.match(block, all_blocks) for matcher in matchers):
                block.add_class(class_name)

    def _build_matchers_for_children(
        self, config: Dict[str, Any], parent_range: List[Block]
    ) -> List[Matcher]:
        """为子元素构建匹配器列表

        Args:
            config: 匹配配置
            parent_range: 父区域范围内的块

        Returns:
            匹配器列表
        """
        matchers = []

        # 类型匹配
        if "type" in config:
            matchers.append(TypeMatcher(config["type"]))

        # 相对位置匹配（相对于父区域）
        if "position" in config:
            position = config["position"]
            # 使用相对位置匹配器
            matchers.append(RelativePositionInRangeMatcher(position, parent_range))

        # 内容模式匹配
        if "pattern" in config:
            matchers.append(PatternMatcher(config["pattern"]))

        return matchers

    def _build_matchers(self, config: Dict[str, Any]) -> List[Matcher]:
        """根据配置构建匹配器列表

        多个匹配器之间是 AND 关系（都要满足）。
        """
        matchers = []

        # 类型匹配
        if "type" in config:
            matchers.append(TypeMatcher(config["type"]))

        # 绝对位置匹配
        if "position" in config:
            matchers.append(PositionMatcher(config["position"]))

        # 内容模式匹配
        if "pattern" in config:
            matchers.append(PatternMatcher(config["pattern"]))

        # 相对位置匹配
        if "after" in config:
            offset = config.get("offset", 0)
            matchers.append(RelativeMatcher(config["after"], "after", offset))

        if "before" in config:
            offset = config.get("offset", 0)
            matchers.append(RelativeMatcher(config["before"], "before", offset))

        # 范围匹配
        if "range" in config:
            range_config = config["range"]
            matchers.append(RangeMatcher(range_config["after"], range_config["before"]))

        return matchers
