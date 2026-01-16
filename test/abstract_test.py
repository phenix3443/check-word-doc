#!/usr/bin/env python3
"""
摘要格式测试

测试摘要的格式规则：
1. 样式：左对齐，5号，华文楷体/Times New Roman，1.15倍行距
2. 内容：限长500字，无引用，不分段
"""

import re

def test_abstract_format():
    """测试摘要格式"""
    
    print("=" * 80)
    print("摘要格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标准格式（正确）",
            "text": "摘要：本文研究了区块链技术在数据管理中的应用，提出了一种新的数据存储方法。",
            "checks": {
                "starts_with": True,
                "has_reference": False,
                "length": 35
            },
            "expected": True
        },
        {
            "name": "场景2：包含引用（错误）",
            "text": "摘要：本文基于前人研究[1]，提出了新的方法。",
            "checks": {
                "starts_with": True,
                "has_reference": True,
                "length": 20
            },
            "expected": False
        },
        {
            "name": "场景3：不以'摘要：'开头（错误）",
            "text": "本文研究了区块链技术。",
            "checks": {
                "starts_with": False,
                "has_reference": False,
                "length": 12
            },
            "expected": False
        },
        {
            "name": "场景4：超过500字（警告）",
            "text": "摘要：" + "这是一个很长的摘要。" * 60,  # 约600字
            "checks": {
                "starts_with": True,
                "has_reference": False,
                "length": 600
            },
            "expected": "warning"
        },
    ]
    
    print("📋 测试用例：")
    print()
    
    for test_case in test_cases:
        print(f"📝 {test_case['name']}")
        text = test_case['text']
        if len(text) > 50:
            print(f"   文本: {text[:50]}...")
        else:
            print(f"   文本: {text}")
        
        checks = test_case['checks']
        
        # 1. 检查是否以"摘要："开头
        starts_with_abstract = re.match(r'^摘要[：:]', text) is not None
        print(f"   ✓ 以'摘要：'开头: {starts_with_abstract}")
        
        # 2. 检查是否包含引用
        has_reference = re.search(r'\[\d+\]', text) is not None
        print(f"   ✓ 包含引用: {has_reference}")
        
        # 3. 检查字数（排除"摘要："）
        content = re.sub(r'^摘要[：:]\s*', '', text)
        length = len(content)
        print(f"   ✓ 字数: {length} 字")
        
        # 判断结果
        if test_case['expected'] == "warning":
            result = "⚠️" if length > 500 else "✅"
            status = "警告" if length > 500 else "通过"
        else:
            is_valid = (
                starts_with_abstract == checks['starts_with'] and
                has_reference == checks['has_reference']
            )
            result = "✅" if is_valid == test_case['expected'] else "❌"
            status = "通过" if is_valid == test_case['expected'] else "失败"
        
        print(f"   {result} {status}")
        print()
    
    print("=" * 80)


def test_abstract_patterns():
    """测试摘要的正则表达式"""
    
    print()
    print("=" * 80)
    print("摘要正则表达式测试")
    print("=" * 80)
    print()
    
    # 1. 开头检查
    start_pattern = r"^摘要[：:]"
    
    # 2. 无引用检查
    no_reference_pattern = r"^(?!.*\[\d+\]).*$"
    
    print("1️⃣  开头格式检查：")
    print(f"   正则表达式: {start_pattern}")
    print()
    
    start_tests = [
        ("摘要：本文研究...", True),
        ("摘要:本文研究...", True),
        ("Abstract: ...", False),
        ("本文研究...", False),
    ]
    
    for text, expected in start_tests:
        match = re.match(start_pattern, text) is not None
        result = "✅" if match == expected else "❌"
        print(f"   {result} {text[:20]:30} {'匹配' if match else '不匹配'}")
    
    print()
    print("2️⃣  无引用检查：")
    print(f"   正则表达式: {no_reference_pattern}")
    print()
    
    reference_tests = [
        ("摘要：本文研究了新方法。", True, "无引用"),
        ("摘要：基于前人研究[1]提出新方法。", False, "包含引用[1]"),
        ("摘要：参考文献[2][3]显示...", False, "包含多个引用"),
    ]
    
    for text, expected, desc in reference_tests:
        match = re.match(no_reference_pattern, text) is not None
        result = "✅" if match == expected else "❌"
        print(f"   {result} {desc:20} {'通过' if match else '失败'}")
    
    print()
    print("=" * 80)


def test_length_check():
    """测试字数统计"""
    
    print()
    print("=" * 80)
    print("摘要字数统计测试")
    print("=" * 80)
    print()
    
    test_texts = [
        "摘要：这是一个简短的摘要。",
        "摘要：" + "这是一个测试文本。" * 10,  # 约100字
        "摘要：" + "这是一个很长的摘要内容。" * 50,  # 约500字
        "摘要：" + "这是一个超长的摘要内容。" * 60,  # 约600字
    ]
    
    print("📊 字数统计：")
    print()
    
    for text in test_texts:
        # 排除"摘要："后统计字数
        content = re.sub(r'^摘要[：:]\s*', '', text)
        length = len(content)
        
        # 判断是否超长
        status = "✅" if length <= 500 else "⚠️"
        status_text = "符合要求" if length <= 500 else "超过限制"
        
        preview = content[:30] + "..." if len(content) > 30 else content
        print(f"   {status} {length:4}字 ({status_text}) - {preview}")
    
    print()
    print("=" * 80)


def main():
    """主函数"""
    test_abstract_format()
    test_abstract_patterns()
    test_length_check()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 样式配置（styles.yaml）：")
    print("   .abstract:")
    print("     font:")
    print("       name_eastasia: 华文楷体")
    print("       name_ascii: Times New Roman")
    print("       size: 五号")
    print("     paragraph:")
    print("       alignment: 左对齐")
    print("       line_spacing: 1.15倍")
    print()
    print("2. 内容规则（rules.yaml）：")
    print("   - r-015: 摘要长度检查（限长500字）")
    print("   - r-016: 摘要无引用检查")
    print("   - r-017: 摘要格式检查（以'摘要：'开头）")
    print()
    print("3. 正则表达式：")
    print("   开头格式: ^摘要[：:]")
    print("   无引用: ^(?!.*\\[\\d+\\]).*$")
    print()
    print("4. 格式要点：")
    print("   - 限长500字（不包括'摘要：'）")
    print("   - 不能包含引用标记（如 [1], [2]）")
    print("   - 必须以'摘要：'开头")
    print("   - 不分段（单段落）")
    print("   - 左对齐")
    print()


if __name__ == "__main__":
    main()
