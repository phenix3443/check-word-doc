"""单元转换工具

将人类可读的单位（如 "16pt", "0.5行", "2字符"）转换为 python-docx 使用的内部单位。

内部单位说明：
- EMU (English Metric Unit): 用于尺寸，914400 EMU = 1 英寸
- Twip (Twentieth of a point): 用于间距，20 twip = 1 point
- Pt (Point): 字体大小，2 pt = 1 半磅

中文字号映射：
- 基于中国国家标准 GB/T 9704-2012
- 支持"三号"、"小四"等中文字号名称
- 如需支持其他字号体系，可以通过继承此类并覆盖相关方法实现

对齐方式：
- 支持中英文双语（"居中"/"CENTER"等）
- 映射到 python-docx 的标准对齐方式枚举
"""

import re
from typing import Union, Optional


class UnitConverter:
    """单元转换器
    
    提供人类可读单位到 python-docx 内部单位的转换。
    所有转换常量都基于国际标准或 Microsoft Word 的标准实现。
    
    支持自定义扩展：
    - 可以通过 register_font_size_alias() 添加自定义字号别名
    - 可以通过 set_char_width_ratio() 调整字符宽度比例
    - 可以通过 set_line_height_ratio() 调整行高比例
    """
    
    # ========== 标准单位转换常量 ==========
    # 这些是固定的国际标准，不应修改
    
    EMU_PER_INCH = 914400  # 1英寸 = 914400 EMU（Office Open XML 标准）
    EMU_PER_CM = 360000    # 1厘米 = 360000 EMU
    TWIP_PER_PT = 20       # 1点 = 20 twip（传统排版单位）
    PT_PER_INCH = 72       # 1英寸 = 72点（PostScript 标准）
    
    # ========== 估算常量 ==========
    # 这些是基于常见字体的估算值，可能因字体而异
    
    # 中文字符宽度（磅）- 基于常见字体
    # 说明：宋体、黑体等中文字体，五号字（10.5pt）时一个字符约等于 10.5pt 宽
    # 实际宽度可能因字体而异，此处使用 1:1 的比例作为估算
    CHAR_WIDTH_RATIO = 1.0  # 字符宽度与字号的比例
    
    # 行高（基于 Word 默认）
    # 说明：Word 中"行"通常指行距，单倍行距约为字号的 1.2 倍
    # 这是 Word 的默认行高计算方式
    LINE_HEIGHT_RATIO = 1.2
    
    # ========== 自定义扩展 ==========
    # 用于存储用户自定义的字号别名
    _custom_font_sizes = {}
    
    @classmethod
    def register_font_size_alias(cls, alias: str, pt: float):
        """注册自定义字号别名
        
        Args:
            alias: 字号别名，如 "特大号"
            pt: 对应的磅数，如 48
            
        Examples:
            >>> UnitConverter.register_font_size_alias("特大号", 48)
            >>> UnitConverter.parse_font_size("特大号")
            96  # 48pt * 2
        """
        cls._custom_font_sizes[alias] = pt
    
    @classmethod
    def set_char_width_ratio(cls, ratio: float):
        """设置字符宽度比例
        
        Args:
            ratio: 字符宽度与字号的比例，默认 1.0
        """
        cls.CHAR_WIDTH_RATIO = ratio
    
    @classmethod
    def set_line_height_ratio(cls, ratio: float):
        """设置行高比例
        
        Args:
            ratio: 行高与字号的比例，默认 1.2
        """
        cls.LINE_HEIGHT_RATIO = ratio
    
    @classmethod
    def parse_font_size(cls, value: Union[str, int, float]) -> Optional[int]:
        """解析字体大小，返回半磅数（Pt的两倍）
        
        Args:
            value: 字体大小，支持：
                - 数字: 直接的磅数，如 16 或 "16"
                - 带单位: "16pt", "5号" 等
                - 自定义别名: 通过 register_font_size_alias() 注册的别名
                
        Returns:
            半磅数，如 16pt -> 32
            
        Examples:
            >>> UnitConverter.parse_font_size("16pt")
            32
            >>> UnitConverter.parse_font_size(16)
            32
            >>> UnitConverter.parse_font_size("三号")
            32
        """
        if value is None:
            return None
            
        # 如果是数字，直接转换
        if isinstance(value, (int, float)):
            return int(value * 2)
            
        value_str = str(value).strip()
        
        # 先查找自定义字号别名
        if value_str in cls._custom_font_sizes:
            return int(cls._custom_font_sizes[value_str] * 2)
        
        # 处理中文字号（基于 GB/T 9704-2012 国家标准）
        # 这是中国广泛使用的字号标准，对应关系如下：
        # 初号(42pt) > 小初(36pt) > 一号(26pt) > 小一(24pt) > 二号(22pt) > 小二(18pt)
        # > 三号(16pt) > 小三(15pt) > 四号(14pt) > 小四(12pt) > 五号(10.5pt) > 小五(9pt)
        # > 六号(7.5pt) > 小六(6.5pt) > 七号(5.5pt) > 八号(5pt)
        chinese_sizes = {
            "初号": 42, "小初": 36,
            "一号": 26, "小一": 24,
            "二号": 22, "小二": 18,
            "三号": 16, "小三": 15,
            "四号": 14, "小四": 12,
            "五号": 10.5, "小五": 9,
            "六号": 7.5, "小六": 6.5,
            "七号": 5.5, "八号": 5,
        }
        
        if value_str in chinese_sizes:
            return int(chinese_sizes[value_str] * 2)
        
        # 处理带单位的字号
        # 匹配数字（整数或小数）+ 可选的单位
        match = re.match(r'^([\d.]+)\s*(pt|磅|号)?$', value_str, re.IGNORECASE)
        if match:
            number = float(match.group(1))
            unit = match.group(2) or "pt"  # 默认单位是磅
            
            if unit.lower() in ["pt", "磅"]:
                return int(number * 2)
            elif unit == "号":
                # "3号" 表示三号字
                if number in chinese_sizes.values():
                    return int(number * 2)
        
        # 无法解析
        return None
    
    @classmethod
    def parse_spacing(cls, value: Union[str, int, float], font_size: Optional[float] = None) -> Optional[int]:
        """解析间距，返回 twip
        
        Args:
            value: 间距值，支持：
                - 数字: 直接的磅数，如 12 或 "12"
                - "Npt": N 磅，如 "12pt"
                - "N行": N 倍行距，如 "0.5行", "1行"
                - "N字符": N 个字符宽度，如 "2字符"
            font_size: 当前字体大小（磅），用于计算相对单位
                
        Returns:
            twip 值
            
        Examples:
            >>> UnitConverter.parse_spacing("12pt")
            240
            >>> UnitConverter.parse_spacing("0.5行", font_size=12)
            144
            >>> UnitConverter.parse_spacing("2字符", font_size=12)
            480
        """
        if value is None:
            return None
            
        # 如果是数字，按磅处理
        if isinstance(value, (int, float)):
            return int(value * cls.TWIP_PER_PT)
            
        value_str = str(value).strip()
        
        # 匹配数字（整数或小数）+ 单位
        match = re.match(r'^([\d.]+)\s*(\S+)$', value_str)
        if not match:
            # 尝试纯数字
            try:
                number = float(value_str)
                return int(number * cls.TWIP_PER_PT)
            except ValueError:
                return None
        
        number = float(match.group(1))
        unit = match.group(2)
        
        # 磅
        if unit.lower() in ["pt", "磅", "点"]:
            return int(number * cls.TWIP_PER_PT)
        
        # 行
        if unit in ["行", "line", "lines"]:
            if font_size is None:
                # 如果没有提供字体大小，使用默认值（五号，10.5pt）
                font_size = 10.5
            line_height = font_size * cls.LINE_HEIGHT_RATIO
            return int(number * line_height * cls.TWIP_PER_PT)
        
        # 字符
        if unit in ["字符", "字", "char", "chars", "character", "characters"]:
            if font_size is None:
                font_size = 10.5
            char_width = font_size * cls.CHAR_WIDTH_RATIO
            return int(number * char_width * cls.TWIP_PER_PT)
        
        # 厘米
        if unit.lower() in ["cm", "厘米"]:
            # 1cm = 28.35pt
            pt = number * 28.35
            return int(pt * cls.TWIP_PER_PT)
        
        # 英寸
        if unit.lower() in ["in", "inch", "inches", "英寸"]:
            pt = number * cls.PT_PER_INCH
            return int(pt * cls.TWIP_PER_PT)
        
        return None
    
    @classmethod
    def parse_indent(cls, value: Union[str, int, float], font_size: Optional[float] = None) -> Optional[int]:
        """解析缩进，返回 twip（与 parse_spacing 相同）
        
        Args:
            value: 缩进值
            font_size: 字体大小（磅）
                
        Returns:
            twip 值
        """
        return cls.parse_spacing(value, font_size)
    
    @classmethod
    def parse_line_spacing(cls, value: Union[str, int, float]) -> tuple[Optional[float], Optional[str]]:
        """解析行距，返回 (行距值, 行距规则)
        
        Args:
            value: 行距值，支持：
                - 数字: 倍数，如 1.5, 2
                - "N倍": N 倍行距，如 "1.5倍"
                - "单倍", "1.5倍", "2倍": 预设值
                - "Npt": 固定值，如 "20pt"
                
        Returns:
            (行距值, 行距规则)
            行距规则可以是: "multiple"(倍数), "exact"(固定值), "atLeast"(最小值)
            
        Examples:
            >>> UnitConverter.parse_line_spacing(1.5)
            (1.5, 'multiple')
            >>> UnitConverter.parse_line_spacing("20pt")
            (400, 'exact')
            >>> UnitConverter.parse_line_spacing("单倍")
            (1.0, 'multiple')
        """
        if value is None:
            return None, None
            
        # 数字 -> 倍数
        if isinstance(value, (int, float)):
            return float(value), "multiple"
            
        value_str = str(value).strip()
        
        # 预设值
        presets = {
            "单倍": (1.0, "multiple"),
            "1.5倍": (1.5, "multiple"),
            "2倍": (2.0, "multiple"),
            "双倍": (2.0, "multiple"),
        }
        
        if value_str in presets:
            return presets[value_str]
        
        # 匹配数字 + 单位
        match = re.match(r'^([\d.]+)\s*(\S+)?$', value_str)
        if not match:
            return None, None
        
        number = float(match.group(1))
        unit = match.group(2) or "倍"  # 默认单位是倍数
        
        # 倍数
        if unit in ["倍", "x", "times"]:
            return number, "multiple"
        
        # 固定值（磅 -> twip）
        if unit.lower() in ["pt", "磅", "点"]:
            twip = int(number * cls.TWIP_PER_PT)
            return twip, "exact"
        
        # 最小值
        if unit in ["最少", "atleast"]:
            twip = int(number * cls.TWIP_PER_PT)
            return twip, "atLeast"
        
        # 默认按倍数处理
        return number, "multiple"
    
    @classmethod
    def format_emu_to_human(cls, emu: int) -> str:
        """将 EMU 转换为人类可读的字符串（用于调试/报告）
        
        Args:
            emu: EMU 值
            
        Returns:
            人类可读的字符串，如 "16pt"
        """
        # EMU -> 半磅 -> 磅
        half_pt = emu / (cls.EMU_PER_INCH / cls.PT_PER_INCH / 2)
        pt = half_pt / 2
        return f"{pt:.1f}pt"
    
    @classmethod
    def format_twip_to_human(cls, twip: int, context: str = "spacing") -> str:
        """将 twip 转换为人类可读的字符串
        
        Args:
            twip: twip 值
            context: 上下文，"spacing" 或 "indent"
            
        Returns:
            人类可读的字符串
        """
        pt = twip / cls.TWIP_PER_PT
        return f"{pt:.1f}pt"


# 便捷函数
def font_size_to_half_pt(value: Union[str, int, float]) -> Optional[int]:
    """字体大小 -> 半磅"""
    return UnitConverter.parse_font_size(value)


def spacing_to_twip(value: Union[str, int, float], font_size: Optional[float] = None) -> Optional[int]:
    """间距 -> twip"""
    return UnitConverter.parse_spacing(value, font_size)


def indent_to_twip(value: Union[str, int, float], font_size: Optional[float] = None) -> Optional[int]:
    """缩进 -> twip"""
    return UnitConverter.parse_indent(value, font_size)
