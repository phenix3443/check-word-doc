#!/usr/bin/env python3
"""测试声明式配置系统"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from script.config_loader import ConfigLoader
from script.rules.registry import build_rules


def test_declarative_config():
    """测试声明式配置的加载和规则生成"""
    
    # 配置文件路径
    config_path = project_root / "config" / "data_paper_declarative.yaml"
    
    print(f"📁 加载配置文件: {config_path}")
    print("=" * 80)
    
    # 加载配置
    try:
        loader = ConfigLoader(str(config_path))
        config = loader.load()
        print("✅ 配置加载成功")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 检查配置
    print(f"\n📝 配置格式: 声明式")
    
    # 生成规则
    print("\n🔧 生成规则...")
    print("=" * 80)
    try:
        rules = build_rules(config)
        print(f"✅ 成功生成 {len(rules)} 条规则\n")
        
        # 按类型分组显示
        rule_types = {}
        for rule in rules:
            rule_type = type(rule).__name__
            if rule_type not in rule_types:
                rule_types[rule_type] = []
            rule_types[rule_type].append(rule)
        
        print("📊 规则类型统计:")
        for rule_type, type_rules in sorted(rule_types.items()):
            print(f"  • {rule_type}: {len(type_rules)} 条")
        
        print("\n📋 规则详情:")
        for rule in rules:
            print(f"  [{rule.id}] {rule.description or type(rule).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ 规则生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unit_converter():
    """测试单元转换器"""
    from script.utils.unit_converter import UnitConverter
    
    print("\n\n🧪 测试单元转换器")
    print("=" * 80)
    
    test_cases = [
        ("字体大小", [
            ("16pt", UnitConverter.parse_font_size),
            ("三号", UnitConverter.parse_font_size),
            ("小四", UnitConverter.parse_font_size),
            (16, UnitConverter.parse_font_size),
        ]),
        ("间距", [
            ("12pt", lambda x: UnitConverter.parse_spacing(x)),
            ("0.5行", lambda x: UnitConverter.parse_spacing(x, 12)),
            ("2字符", lambda x: UnitConverter.parse_spacing(x, 12)),
        ]),
        ("行距", [
            (1.5, UnitConverter.parse_line_spacing),
            ("1.5倍", UnitConverter.parse_line_spacing),
            ("20pt", UnitConverter.parse_line_spacing),
            ("单倍", UnitConverter.parse_line_spacing),
        ]),
    ]
    
    for category, cases in test_cases:
        print(f"\n{category}:")
        for input_val, func in cases:
            try:
                result = func(input_val)
                print(f"  ✓ {input_val} -> {result}")
            except Exception as e:
                print(f"  ✗ {input_val} -> 错误: {e}")


def main():
    """主函数"""
    print("🚀 开始测试声明式配置系统")
    print("=" * 80)
    print()
    
    # 测试单元转换
    test_unit_converter()
    
    # 测试声明式配置
    success = test_declarative_config()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 测试失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
