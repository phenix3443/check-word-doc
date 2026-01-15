from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Union

from docx.table import Table
from docx.text.paragraph import Paragraph


class Severity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class Location:
    block_index: int
    kind: str
    hint: str


@dataclass(frozen=True)
class Issue:
    code: str
    severity: Severity
    message: str
    location: Location
    evidence: Optional[dict[str, Any]] = None


@dataclass
class ParagraphBlock:
    """段落元素
    
    Attributes:
        index: 元素在文档中的索引位置
        paragraph: python-docx 的 Paragraph 对象
        classes: 元素的 class 列表（用于语义标注）
    """
    index: int
    paragraph: Paragraph
    classes: List[str] = field(default_factory=list)
    
    def add_class(self, class_name: str) -> None:
        """添加 class
        
        Args:
            class_name: 要添加的 class 名称
        """
        if class_name not in self.classes:
            self.classes.append(class_name)
    
    def has_class(self, class_name: str) -> bool:
        """检查是否有指定 class
        
        Args:
            class_name: class 名称
            
        Returns:
            True 如果有该 class，否则 False
        """
        return class_name in self.classes
    
    def get_classes(self) -> List[str]:
        """获取所有 class
        
        Returns:
            class 列表的副本
        """
        return self.classes.copy()


@dataclass
class TableBlock:
    """表格元素
    
    Attributes:
        index: 元素在文档中的索引位置
        table: python-docx 的 Table 对象
        classes: 元素的 class 列表（用于语义标注）
    """
    index: int
    table: Table
    classes: List[str] = field(default_factory=list)
    
    def add_class(self, class_name: str) -> None:
        """添加 class
        
        Args:
            class_name: 要添加的 class 名称
        """
        if class_name not in self.classes:
            self.classes.append(class_name)
    
    def has_class(self, class_name: str) -> bool:
        """检查是否有指定 class
        
        Args:
            class_name: class 名称
            
        Returns:
            True 如果有该 class，否则 False
        """
        return class_name in self.classes
    
    def get_classes(self) -> List[str]:
        """获取所有 class
        
        Returns:
            class 列表的副本
        """
        return self.classes.copy()


Block = Union[ParagraphBlock, TableBlock]

