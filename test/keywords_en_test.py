#!/usr/bin/env python3
"""
英文关键词格式测试

测试英文关键词的格式规则：
1. 样式：Times New Roman，5号字
2. 内容：至少3个关键词，关键词之间使用英文分号+空格（; ）分隔
"""

import re

def test_keywords_en_format():
    """测试英文关键词格式"""
    
    print("=" * 80)
    print("英文关键词格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标准格式（3个关键词，正确）",
            "text": "Keywords: blockchain; data management; smart contract",
            "checks": {
                "starts_with": True,
                "has_semicolon_space": True,
                "count": 3
            },
            "expected": True
        },
        {
            "name": "场景2：多个关键词（5个，正确）",
            "text": "Keywords: blockchain; data management; smart contract; distributed system; security",
            "checks": {
                "starts_with": True,
                "has_semicolon_space": True,
                "count": 5
            },
            "expected": True
        },
        {
            "name": "场景3：关键词不足（2个，错误）",
            "text": "Keywords: blockchain; data management",
            "checks": {
                "starts_with": True,
                "has_semicolon_space": True,
                "count": 2
            },
            "expected": False
        },
        {
            "name": "场景4：使用中文分号（错误）",
            "text": "Keywords: blockchain；data management；smart contract",
            "checks": {
                "starts_with": True,
                "has_semicolon_space": False,
                "count": 3
            },
            "expected": False
        },
        {
            "name": "场景5：分号后无空格（错误）",
            "text": "Keywords: blockchain;data management;smart contract",
            "checks": {
                "starts_with": True,
                "has_semicolon_space": False,
                "count": 3
            },
            "expected": False
        },
        {
            "name": "场景6：使用逗号分隔（错误）",
            "text": "Keywords: blockchain, data management, smart contract",
            "checks": {
                "starts_with": True,
                "has_semicolon_space": False,
                "count": 3
            },
            "expected": False
        },
        {
            "name": "场景7：不以'Keywords:'开头（错误）",
            "text": "关键词: blockchain; data management; smart contract",
            "checks": {
                "starts_with": False,
                "has_semicolon_space": True,
                "count": 3
            },
            "expected": False
        },
        {
            "name": "场景8：多个空格（正确）",
            "text": "Keywords: blockchain;  data management;  smart contract",
            "checks": {
                "starts_with": True,
                "has_semicolon_space": True,
                "count": 3
            },
            "expected": True
        },
    ]
    
    print("📋 测试用例：")
    print()
    
    for test_case in test_cases:
        print(f"📝 {test_case['name']}")
        text = test_case['text']
        print(f"   文本: {text}")
        
        checks = test_case['checks']
        
        # 1. 检查是否以"Keywords:"开头
        starts_with_keywords = re.match(r'^Keywords:', text) is not None
        print(f"   ✓ 以'Keywords:'开头: {starts_with_keywords}")
        
        # 2. 检查是否使用英文分号+空格
        has_semicolon_space = re.search(r';\s+', text) is not None
        print(f"   ✓ 包含英文分号+空格: {has_semicolon_space}")
        
        # 3. 统计关键词数量（按英文分号+空格分割）
        content = re.sub(r'^Keywords:\s*', '', text)
        if re.search(r';\s+', content):
            keywords = re.split(r';\s+', content)
            count = len([k for k in keywords if k.strip()])
        else:
            # 如果没有分号+空格，可能只有一个关键词或使用了错误的分隔符
            count = 1 if content.strip() else 0
        
        print(f"   ✓ 关键词数量: {count}")
        
        # 判断结果
        is_valid = (
            starts_with_keywords == checks['starts_with'] and
            has_semicolon_space == checks['has_semicolon_space'] and
            count >= 3  # 至少3个
        )
        
        result = "✅" if is_valid == test_case['expected'] else "❌"
        status = "通过" if is_valid == test_case['expected'] else "失败"
        
        print(f"   {result} {status}")
        print()
    
    print("=" * 80)


def test_keywords_en_patterns():
    """测试英文关键词的正则表达式"""
    
    print()
    print("=" * 80)
    print("英文关键词正则表达式测试")
    print("=" * 80)
    print()
    
    # 1. 开头检查
    start_pattern = r"^Keywords:"
    
    # 2. 分隔符检查（多个关键词必须有分号+空格）
    separator_pattern = r"^Keywords:.+;\s+.+$"
    
    print("1️⃣  开头格式检查：")
    print(f"   正则表达式: {start_pattern}")
    print()
    
    start_tests = [
        ("Keywords: blockchain; data management", True),
        ("Keywords:blockchain; data management", True),
        ("关键词: blockchain; data management", False),
        ("blockchain; data management", False),
    ]
    
    for text, expected in start_tests:
        match = re.match(start_pattern, text) is not None
        result = "✅" if match == expected else "❌"
        print(f"   {result} {text:45} {'匹配' if match else '不匹配'}")
    
    print()
    print("2️⃣  分隔符检查（英文分号+空格）：")
    print(f"   正则表达式: {separator_pattern}")
    print()
    
    separator_tests = [
        ("Keywords: blockchain; data management; smart contract", True, "使用英文分号+空格"),
        ("Keywords: blockchain;data management;smart contract", False, "分号后无空格"),
        ("Keywords: blockchain；data management；smart contract", False, "使用中文分号"),
        ("Keywords: blockchain, data management, smart contract", False, "使用逗号"),
        ("Keywords: blockchain", False, "单个关键词（无分隔符）"),
    ]
    
    for text, expected, desc in separator_tests:
        match = re.match(separator_pattern, text) is not None
        result = "✅" if match == expected else "❌"
        status = "匹配" if match else "不匹配"
        print(f"   {result} {desc:30} {status}")
    
    print()
    print("=" * 80)


def test_keywords_en_count():
    """测试英文关键词数量统计"""
    
    print()
    print("=" * 80)
    print("英文关键词数量统计测试")
    print("=" * 80)
    print()
    
    test_texts = [
        "Keywords: blockchain",
        "Keywords: blockchain; data management",
        "Keywords: blockchain; data management; smart contract",
        "Keywords: blockchain; data management; smart contract; distributed system",
        "Keywords: blockchain; data management; smart contract; distributed system; security",
    ]
    
    print("📊 关键词数量统计：")
    print()
    
    for text in test_texts:
        # 排除"Keywords:"后统计
        content = re.sub(r'^Keywords:\s*', '', text)
        
        # 按英文分号+空格分割
        if re.search(r';\s+', content):
            keywords = [k.strip() for k in re.split(r';\s+', content) if k.strip()]
            count = len(keywords)
        else:
            count = 1 if content.strip() else 0
        
        # 判断是否符合要求
        status = "✅" if count >= 3 else "❌"
        status_text = "符合要求" if count >= 3 else "不足3个"
        
        print(f"   {status} {count}个关键词 ({status_text})")
        print(f"      内容: {content}")
        if count >= 3:
            print(f"      关键词列表: {keywords}")
        print()
    
    print("=" * 80)


def test_separator_comparison():
    """测试分隔符对比"""
    
    print()
    print("=" * 80)
    print("中英文关键词分隔符对比")
    print("=" * 80)
    print()
    
    comparison = [
        {
            "语言": "中文关键词",
            "分隔符": "中文分号（；）",
            "示例": "关键词：区块链；数据管理；智能合约"
        },
        {
            "语言": "英文关键词",
            "分隔符": "英文分号+空格（; ）",
            "示例": "Keywords: blockchain; data management; smart contract"
        },
    ]
    
    print("📊 分隔符对比：")
    print()
    
    for item in comparison:
        print(f"   {item['语言']}:")
        print(f"      分隔符: {item['分隔符']}")
        print(f"      示例: {item['示例']}")
        print()
    
    print("⚠️  注意事项：")
    print("   - 中文关键词使用中文分号（；），无空格")
    print("   - 英文关键词使用英文分号+空格（; ），注意空格")
    print("   - 不要混用分隔符")
    print()
    
    print("=" * 80)


def test_common_errors():
    """测试常见错误"""
    
    print()
    print("=" * 80)
    print("常见错误示例")
    print("=" * 80)
    print()
    
    errors = [
        {
            "错误": "分号后无空格",
            "错误示例": "Keywords: blockchain;data management;smart contract",
            "正确示例": "Keywords: blockchain; data management; smart contract"
        },
        {
            "错误": "使用中文分号",
            "错误示例": "Keywords: blockchain；data management；smart contract",
            "正确示例": "Keywords: blockchain; data management; smart contract"
        },
        {
            "错误": "使用逗号分隔",
            "错误示例": "Keywords: blockchain, data management, smart contract",
            "正确示例": "Keywords: blockchain; data management; smart contract"
        },
        {
            "错误": "关键词不足3个",
            "错误示例": "Keywords: blockchain; data management",
            "正确示例": "Keywords: blockchain; data management; smart contract"
        },
    ]
    
    print("❌ 常见错误：")
    print()
    
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error['错误']}")
        print(f"   ❌ 错误: {error['错误示例']}")
        print(f"   ✅ 正确: {error['正确示例']}")
        print()
    
    print("=" * 80)


def main():
    """主函数"""
    test_keywords_en_format()
    test_keywords_en_patterns()
    test_keywords_en_count()
    test_separator_comparison()
    test_common_errors()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 样式配置（styles.yaml）：")
    print("   .keywords-en:")
    print("     font:")
    print("       name_ascii: Times New Roman")
    print("       size: 五号")
    print("     paragraph:")
    print("       line_spacing: 1.15倍")
    print("       alignment: 两端对齐")
    print()
    print("2. 内容规则（rules.yaml）：")
    print("   - r-021: 英文关键词数量检查（不低于3个）")
    print("   - r-022: 英文关键词分隔符检查（使用英文分号+空格）")
    print("   - r-023: 英文关键词格式检查（以'Keywords:'开头）")
    print()
    print("3. 正则表达式：")
    print("   开头格式: ^Keywords:")
    print("   分隔符: ^Keywords:.+;\\s+.+$")
    print()
    print("4. 格式要点：")
    print("   - 至少3个关键词")
    print("   - Times New Roman字体")
    print("   - 5号字")
    print("   - 关键词之间使用英文分号+空格（; ）分隔")
    print("   - 必须以'Keywords:'开头")
    print()
    print("5. 与中文关键词的区别：")
    print("   - 中文：使用中文分号（；），无空格")
    print("   - 英文：使用英文分号+空格（; ），注意空格")
    print()


if __name__ == "__main__":
    main()
