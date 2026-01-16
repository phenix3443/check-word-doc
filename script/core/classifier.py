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
        position: 0       # 范围内的第一个（0-based）
        position: -1      # 范围内的最后一个
        position: 1       # 范围内的第二个
        position: -2      # 范围内的倒数第二个
    """

    def __init__(self, position: int, parent_range: List[Block]):
        """
        Args:
            position: 数字索引（0表示第一个，-1表示最后一个）
            parent_range: 父区域的块列表
        """
        if not isinstance(position, int):
            raise ValueError(f"position 必须是整数，不支持字符串形式。使用 0 表示第一个，-1 表示最后一个。当前值: {position}")
        
        self.position = position
        self.parent_range = parent_range

    def match(self, block: Block, context: List[Block]) -> bool:
        # 检查 block 是否在 parent_range 中
        if block not in self.parent_range:
            return False

        # 数字索引（相对于 parent_range）
        # 支持负数索引：-1 表示最后一个，-2 表示倒数第二个
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

        # 新的 position 语法
        if "position" in match_config:
            position_config = match_config["position"]
            
            # position 是一个对象 { type, index }
            if isinstance(position_config, dict) and "type" in position_config:
                pos_type = position_config["type"]
                
                if pos_type == "relative":
                    pos_index = position_config["index"]
                    
                    # 如果是区间表达式，提取其中的 class 引用
                    if isinstance(pos_index, str) and any(c in pos_index for c in '()[]'):
                        # 解析区间表达式：(a, b) 或 [a, b]
                        # 注意：类名可以包含连字符，如 abstract-en
                        import re
                        pattern = r'[\[\(]\s*([\w-]+)\s*,\s*([\w-]+)\s*[\]\)]'
                        match = re.search(pattern, pos_index)
                        if match:
                            anchor1, anchor2 = match.groups()
                            dependencies.extend([anchor1, anchor2])
                
                # 新语法：position: {type: next/prev, class: xxx}
                elif pos_type in ["next", "prev"]:
                    if "class" in position_config:
                        dependencies.append(position_config["class"])

        # 旧语法：after/before 中的 class 引用（向后兼容）
        if "after" in match_config and isinstance(match_config["after"], dict):
            if "class" in match_config["after"]:
                dependencies.append(match_config["after"]["class"])

        if "before" in match_config and isinstance(match_config["before"], dict):
            if "class" in match_config["before"]:
                dependencies.append(match_config["before"]["class"])

        # 旧语法：range 中的 class 引用（向后兼容）
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
            position_config = config["position"]
            
            # 新语法：position 是一个对象 { type: relative, index: ... }
            if isinstance(position_config, dict) and "type" in position_config:
                if position_config["type"] == "relative":
                    position_index = position_config["index"]
                    
                    # 检查是否是区间表达式
                    if isinstance(position_index, str) and any(c in position_index for c in '()[]'):
                        # 区间表达式：在 parent_range 中查找引用的 class
                        # 例如：(author-list, corresponding-author)
                        import re
                        pattern = r'[\[\(]\s*(\w+(?:-\w+)*)\s*,\s*(\w+(?:-\w+)*)\s*[\]\)]'
                        match = re.match(pattern, position_index.strip())
                        
                        if match:
                            class1, class2 = match.groups()
                            
                            # 在 parent_range 中查找这两个 class 的块
                            anchor1 = None
                            anchor2 = None
                            
                            for block in parent_range:
                                if block.has_class(class1):
                                    anchor1 = block
                                if block.has_class(class2):
                                    anchor2 = block
                            
                            # 如果找到了两个锚点，创建范围匹配器
                            if anchor1 and anchor2:
                                # 创建一个子范围：anchor1 和 anchor2 之间的块
                                start_idx = parent_range.index(anchor1)
                                end_idx = parent_range.index(anchor2)
                                
                                # 开区间：不包含锚点本身
                                sub_range = parent_range[start_idx + 1:end_idx]
                                
                                # 使用一个简单的匹配器：检查 block 是否在 sub_range 中
                                class SubRangeMatcher(Matcher):
                                    def __init__(self, sub_range):
                                        self.sub_range = sub_range
                                    
                                    def match(self, block, context):
                                        return block in self.sub_range
                                
                                matchers.append(SubRangeMatcher(sub_range))
                            else:
                                # 锚点未找到，这个匹配器永远不会匹配
                                class NeverMatcher(Matcher):
                                    def match(self, block, context):
                                        return False
                                
                                matchers.append(NeverMatcher())
                        else:
                            # 区间表达式格式错误
                            raise ValueError(f"Invalid range expression: {position_index}")
                    else:
                        # 简单位置：first, last, 或数字
                        matchers.append(RelativePositionInRangeMatcher(position_index, parent_range))
            
            # 旧语法：position 是一个简单值（向后兼容）
            else:
                matchers.append(RelativePositionInRangeMatcher(position_config, parent_range))

        # 内容模式匹配
        if "pattern" in config:
            matchers.append(PatternMatcher(config["pattern"]))

        return matchers

    def _build_matchers(self, config: Dict[str, Any]) -> List[Matcher]:
        """根据配置构建匹配器列表

        多个匹配器之间是 AND 关系（都要满足）。
        
        支持新的统一 position 语法：
        - position: { type: absolute, index: 0 }
        - position: { type: range, index: "(title, abstract)" }
        
        同时保持向后兼容旧语法：
        - position: 0
        - range: { after: {...}, before: {...} }
        """
        matchers = []

        # 类型匹配
        if "type" in config:
            matchers.append(TypeMatcher(config["type"]))

        # 新的统一 position 语法
        if "position" in config:
            position_config = config["position"]
            
            # 新语法：position 是一个对象 { type, index/class }
            if isinstance(position_config, dict) and "type" in position_config:
                pos_type = position_config["type"]
                
                if pos_type == "absolute":
                    # 绝对定位：相对于整个文档
                    pos_index = position_config["index"]
                    matchers.append(PositionMatcher(pos_index))
                
                elif pos_type == "relative":
                    # 相对定位：可能是区间表达式或简单位置
                    pos_index = position_config["index"]
                    if isinstance(pos_index, str) and any(c in pos_index for c in '()[]'):
                        # 区间表达式：(a, b) 或 [a, b] 等
                        range_matchers = self._parse_range_expression(pos_index)
                        matchers.extend(range_matchers)
                    else:
                        # 简单位置：first, last, middle, 0, 1, 2...
                        # 这个会在 _build_matchers_for_children 中处理
                        pass
                
                elif pos_type == "next":
                    # 下一个元素：position: {type: next, class: xxx}
                    offset = position_config.get("offset", 0)
                    anchor = {"class": position_config["class"]}
                    matchers.append(RelativeMatcher(anchor, "after", offset))
                
                elif pos_type == "prev":
                    # 上一个元素：position: {type: prev, class: xxx}
                    offset = position_config.get("offset", 0)
                    anchor = {"class": position_config["class"]}
                    matchers.append(RelativeMatcher(anchor, "before", offset))
            
            # 旧语法：position 是一个简单值（向后兼容）
            else:
                matchers.append(PositionMatcher(position_config))

        # 内容模式匹配
        if "pattern" in config:
            matchers.append(PatternMatcher(config["pattern"]))

        # 旧语法：after/before（向后兼容）
        if "after" in config:
            offset = config.get("offset", 0)
            matchers.append(RelativeMatcher(config["after"], "after", offset))

        if "before" in config:
            offset = config.get("offset", 0)
            matchers.append(RelativeMatcher(config["before"], "before", offset))

        # 旧语法：range（向后兼容）
        if "range" in config:
            range_config = config["range"]
            matchers.append(RangeMatcher(range_config["after"], range_config["before"]))

        return matchers
    
    def _parse_range_expression(self, expr: str) -> List[Matcher]:
        """解析范围表达式
        
        支持的格式：
        - (a, b)  : 开区间，不包含 a 和 b
        - [a, b)  : 左闭右开，包含 a，不包含 b
        - (a, b]  : 左开右闭，不包含 a，包含 b
        - [a, b]  : 闭区间，包含 a 和 b
        
        Args:
            expr: 区间表达式字符串
            
        Returns:
            匹配器列表
        """
        import re
        
        # 解析区间表达式：([左括号)(锚点1), (锚点2)(右括号)
        # 注意：类名可以包含连字符，如 abstract-en
        pattern = r'^([\[\(])\s*([\w-]+)\s*,\s*([\w-]+)\s*([\]\)])$'
        match = re.match(pattern, expr.strip())
        
        if not match:
            raise ValueError(f"无效的范围表达式: {expr}")
        
        left_bracket, anchor1, anchor2, right_bracket = match.groups()
        
        # 构建锚点定义
        after_anchor = {"class": anchor1}
        before_anchor = {"class": anchor2}
        
        # 根据括号类型确定是否包含边界
        # 开区间 (a, b): 不包含边界，使用 RangeMatcher（默认不包含）
        # 闭区间 [a, b]: 包含边界，需要特殊处理
        
        # 目前简化处理：都使用 RangeMatcher（不包含边界）
        # TODO: 实现包含边界的逻辑
        return [RangeMatcher(after_anchor, before_anchor)]
