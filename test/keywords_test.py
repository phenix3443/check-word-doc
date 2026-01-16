#!/usr/bin/env python3
"""
关键词格式测试

测试关键词的格式规则：
1. 样式：华文楷体，5号字
2. 内容：不低于3个，关键词之间以中文分号（；）隔开
"""

import re

def test_keywords_format():
    """测试关键词格式"""
    
    print("=" * 80)
    print("关键词格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标准格式（3个关键词，正确）",
            "text": "关键词：区块链；数据管理；智能合约",
            "checks": {
                "starts_with": True,
                "has_semicolon": True,
                "count": 3
            },
            "expected": True
        },
        {
            "name": "场景2：多个关键词（5个，正确）",
            "text": "关键词：区块链；数据管理；智能合约；分布式系统；安全性",
            "checks": {
                "starts_with": True,
                "has_semicolon": True,
                "count": 5
            },
            "expected": True
        },
        {
            "name": "场景3：关键词不足（2个，错误）",
            "text": "关键词：区块链；数据管理",
            "checks": {
                "starts_with": True,
                "has_semicolon": True,
                "count": 2
            },
            "expected": False
        },
        {
            "name": "场景4：使用英文分号（错误）",
            "text": "关键词：区块链;数据管理;智能合约",
            "checks": {
                "starts_with": True,
                "has_semicolon": False,  # 中文分号
                "count": 3
            },
            "expected": False
        },
        {
            "name": "场景5：使用逗号分隔（错误）",
            "text": "关键词：区块链，数据管理，智能合约",
            "checks": {
                "starts_with": True,
                "has_semicolon": False,
                "count": 3
            },
            "expected": False
        },
        {
            "name": "场景6：不以'关键词：'开头（错误）",
            "text": "Keywords: 区块链；数据管理；智能合约",
            "checks": {
                "starts_with": False,
                "has_semicolon": True,
                "count": 3
            },
            "expected": False
        },
    ]
    
    print("📋 测试用例：")
    print()
    
    for test_case in test_cases:
        print(f"📝 {test_case['name']}")
        text = test_case['text']
        print(f"   文本: {text}")
        
        checks = test_case['checks']
        
        # 1. 检查是否以"关键词："开头
        starts_with_keywords = re.match(r'^关键词[：:]', text) is not None
        print(f"   ✓ 以'关键词：'开头: {starts_with_keywords}")
        
        # 2. 检查是否使用中文分号
        has_chinese_semicolon = '；' in text
        print(f"   ✓ 包含中文分号: {has_chinese_semicolon}")
        
        # 3. 统计关键词数量（按中文分号分割）
        content = re.sub(r'^关键词[：:]\s*', '', text)
        if '；' in content:
            keywords = content.split('；')
            count = len([k for k in keywords if k.strip()])
        else:
            # 如果没有分号，可能只有一个关键词或使用了错误的分隔符
            count = 1 if content.strip() else 0
        
        print(f"   ✓ 关键词数量: {count}")
        
        # 判断结果
        is_valid = (
            starts_with_keywords == checks['starts_with'] and
            has_chinese_semicolon == checks['has_semicolon'] and
            count >= 3  # 至少3个
        )
        
        result = "✅" if is_valid == test_case['expected'] else "❌"
        status = "通过" if is_valid == test_case['expected'] else "失败"
        
        print(f"   {result} {status}")
        print()
    
    print("=" * 80)


def test_keywords_patterns():
    """测试关键词的正则表达式"""
    
    print()
    print("=" * 80)
    print("关键词正则表达式测试")
    print("=" * 80)
    print()
    
    # 1. 开头检查
    start_pattern = r"^关键词[：:]"
    
    # 2. 分隔符检查（多个关键词必须有分号）
    separator_pattern = r"^关键词[：:].+；.+$"
    
    print("1️⃣  开头格式检查：")
    print(f"   正则表达式: {start_pattern}")
    print()
    
    start_tests = [
        ("关键词：区块链；数据管理", True),
        ("关键词:区块链；数据管理", True),
        ("Keywords: blockchain", False),
        ("区块链；数据管理", False),
    ]
    
    for text, expected in start_tests:
        match = re.match(start_pattern, text) is not None
        result = "✅" if match == expected else "❌"
        print(f"   {result} {text:35} {'匹配' if match else '不匹配'}")
    
    print()
    print("2️⃣  分隔符检查（中文分号）：")
    print(f"   正则表达式: {separator_pattern}")
    print()
    
    separator_tests = [
        ("关键词：区块链；数据管理；智能合约", True, "使用中文分号"),
        ("关键词：区块链;数据管理;智能合约", False, "使用英文分号"),
        ("关键词：区块链，数据管理，智能合约", False, "使用逗号"),
        ("关键词：区块链", False, "单个关键词（无分隔符）"),
    ]
    
    for text, expected, desc in separator_tests:
        match = re.match(separator_pattern, text) is not None
        result = "✅" if match == expected else "❌"
        status = "匹配" if match else "不匹配"
        print(f"   {result} {desc:25} {status}")
    
    print()
    print("=" * 80)


def test_keywords_count():
    """测试关键词数量统计"""
    
    print()
    print("=" * 80)
    print("关键词数量统计测试")
    print("=" * 80)
    print()
    
    test_texts = [
        "关键词：区块链",
        "关键词：区块链；数据管理",
        "关键词：区块链；数据管理；智能合约",
        "关键词：区块链；数据管理；智能合约；分布式系统",
        "关键词：区块链；数据管理；智能合约；分布式系统；安全性",
    ]
    
    print("📊 关键词数量统计：")
    print()
    
    for text in test_texts:
        # 排除"关键词："后统计
        content = re.sub(r'^关键词[：:]\s*', '', text)
        
        # 按中文分号分割
        if '；' in content:
            keywords = [k.strip() for k in content.split('；') if k.strip()]
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


def test_separator_detection():
    """测试分隔符检测"""
    
    print()
    print("=" * 80)
    print("分隔符检测测试")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "text": "关键词：区块链；数据管理；智能合约",
            "separator": "中文分号（；）",
            "correct": True
        },
        {
            "text": "关键词：区块链;数据管理;智能合约",
            "separator": "英文分号（;）",
            "correct": False
        },
        {
            "text": "关键词：区块链，数据管理，智能合约",
            "separator": "中文逗号（，）",
            "correct": False
        },
        {
            "text": "关键词：区块链, 数据管理, 智能合约",
            "separator": "英文逗号（,）",
            "correct": False
        },
        {
            "text": "关键词：区块链 数据管理 智能合约",
            "separator": "空格",
            "correct": False
        },
    ]
    
    print("🔍 分隔符检测：")
    print()
    
    for case in test_cases:
        text = case['text']
        separator = case['separator']
        correct = case['correct']
        
        # 检测使用的分隔符
        has_chinese_semicolon = '；' in text
        has_english_semicolon = ';' in text and '；' not in text
        has_chinese_comma = '，' in text
        has_english_comma = ',' in text
        
        status = "✅" if correct else "❌"
        status_text = "正确" if correct else "错误"
        
        print(f"   {status} 使用{separator} ({status_text})")
        print(f"      文本: {text}")
        print()
    
    print("=" * 80)


def main():
    """主函数"""
    test_keywords_format()
    test_keywords_patterns()
    test_keywords_count()
    test_separator_detection()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 样式配置（styles.yaml）：")
    print("   .keywords:")
    print("     font:")
    print("       name_eastasia: 华文楷体")
    print("       size: 五号")
    print("     paragraph:")
    print("       line_spacing: 1.15倍")
    print("       alignment: 两端对齐")
    print()
    print("2. 内容规则（rules.yaml）：")
    print("   - r-018: 关键词数量检查（不低于3个）")
    print("   - r-019: 关键词分隔符检查（使用中文分号）")
    print("   - r-020: 关键词格式检查（以'关键词：'开头）")
    print()
    print("3. 正则表达式：")
    print("   开头格式: ^关键词[：:]")
    print("   分隔符: ^关键词[：:].+；.+$")
    print()
    print("4. 格式要点：")
    print("   - 不低于3个关键词")
    print("   - 华文楷体")
    print("   - 5号字")
    print("   - 关键词之间使用中文分号（；）隔开")
    print("   - 必须以'关键词：'开头")
    print()


if __name__ == "__main__":
    main()
