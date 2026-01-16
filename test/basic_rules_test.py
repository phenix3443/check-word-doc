#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本规则测试

测试所有文档都要遵守的基本格式规则：
1. 中文不能被英文引号包围
2. 中文之间不能有空格
3. 引号必须成对匹配
"""

import re

def test_chinese_in_english_quotes():
    """测试 r-basic-001: 中文不能被英文引号包围"""
    
    print("=" * 80)
    print("r-basic-001: 中文不能被英文引号包围")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "name": "场景1：中文被英文双引号包围（错误）",
            "text": '这是"中文"内容',
            "expected": False
        },
        {
            "name": "场景2：中文被英文单引号包围（错误）",
            "text": "这是'中文'内容",
            "expected": False
        },
        {
            "name": "场景3：使用中文引号（正确）",
            "text": "这是\u201c中文\u201d内容",  # 使用Unicode
            "expected": True
        },
        {
            "name": "场景4：英文被英文引号包围（正确）",
            "text": '这是"English"内容',
            "expected": True
        },
        {
            "name": "场景5：纯英文引号（正确）",
            "text": 'This is "English" content',
            "expected": True
        },
    ]
    
    # 正则：不包含 英文引号+中文+英文引号
    pattern = r"^(?!.*['\"][\u4e00-\u9fa5]+['\"]).*$"
    
    print(f"正则表达式: {pattern}")
    print()
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        text = test_case['text']
        expected = test_case['expected']
        
        match = re.match(pattern, text) is not None
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {test_case['name']}")
        print(f"   文本: '{text}'")
        print(f"   预期: {'通过' if expected else '不通过'}, 实际: {'通过' if match else '不通过'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    return passed, failed


def test_chinese_spacing():
    """测试 r-basic-002: 中文之间不能有空格"""
    
    print()
    print("=" * 80)
    print("r-basic-002: 中文之间不能有空格")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "name": "场景1：中文之间有空格（错误）",
            "text": "这是 中文",
            "expected": False
        },
        {
            "name": "场景2：中文之间有多个空格（错误）",
            "text": "数据 库",
            "expected": False
        },
        {
            "name": "场景3：中文连续无空格（正确）",
            "text": "这是中文内容",
            "expected": True
        },
        {
            "name": "场景4：中英文之间有空格（正确）",
            "text": "这是 English 内容",
            "expected": True
        },
        {
            "name": "场景5：中文和数字之间有空格（正确）",
            "text": "共有 100 个",
            "expected": True
        },
    ]
    
    # 正则：不包含 中文+空格+中文
    pattern = r"^(?!.*[\u4e00-\u9fa5]\s+[\u4e00-\u9fa5]).*$"
    
    print(f"正则表达式: {pattern}")
    print()
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        text = test_case['text']
        expected = test_case['expected']
        
        match = re.match(pattern, text) is not None
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {test_case['name']}")
        print(f"   文本: '{text}'")
        print(f"   预期: {'通过' if expected else '不通过'}, 实际: {'通过' if match else '不通过'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    return passed, failed


def test_quote_matching():
    """测试引号匹配规则"""
    
    print()
    print("=" * 80)
    print("引号匹配测试")
    print("=" * 80)
    print()
    
    # 测试中文双引号
    print("📋 r-basic-003: 中文双引号匹配")
    print()
    
    test_cases_cn_double = [
        ("正确：成对引号", "\u201c中文内容\u201d", True),
        ("错误：只有左引号", "\u201c中文内容", False),
        ("错误：只有右引号", "中文内容\u201d", False),
        ("正确：多对引号", "\u201c内容1\u201d\u201c内容2\u201d", True),
    ]
    
    passed = 0
    failed = 0
    
    for name, text, expected in test_cases_cn_double:
        # 简单检查：左右引号数量相等
        left_count = text.count('\u201c')
        right_count = text.count('\u201d')
        match = (left_count == right_count and left_count > 0)
        
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {name}: '{text}'")
        print(f"   左引号: {left_count}, 右引号: {right_count}")
        print()
    
    print("=" * 80)
    print(f"中文双引号测试: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    # 测试英文双引号
    print()
    print("📋 r-basic-005: 英文双引号匹配")
    print()
    
    test_cases_en_double = [
        ("正确：成对引号", '"English content"', True),
        ("错误：只有左引号", '"English content', False),
        ("错误：只有右引号", 'English content"', False),
        ("正确：多对引号", '"content1""content2"', True),
    ]
    
    passed2 = 0
    failed2 = 0
    
    for name, text, expected in test_cases_en_double:
        # 检查双引号数量是否为偶数
        count = text.count('"')
        match = (count % 2 == 0 and count > 0)
        
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed2 += 1
        else:
            failed2 += 1
        
        print(f"{result} {name}: '{text}'")
        print(f"   引号数量: {count}")
        print()
    
    print("=" * 80)
    print(f"英文双引号测试: {passed2} 通过, {failed2} 失败")
    print("=" * 80)
    
    return passed + passed2, failed + failed2


def test_bracket_matching():
    """测试括号匹配规则"""
    
    print()
    print("=" * 80)
    print("括号匹配测试")
    print("=" * 80)
    print()
    
    # 测试圆括号
    print("📋 r-basic-007: 圆括号匹配")
    print()
    
    test_cases = [
        ("正确：成对括号", "(内容)", True),
        ("错误：只有左括号", "(内容", False),
        ("错误：只有右括号", "内容)", False),
        ("正确：嵌套括号", "内容(说明(详细))内容", True),
        ("错误：括号不匹配", "(内容))", False),
    ]
    
    passed = 0
    failed = 0
    
    for name, text, expected in test_cases:
        # 简单检查：左右括号数量相等
        left_count = text.count('(')
        right_count = text.count(')')
        match = (left_count == right_count)
        
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {name}: '{text}'")
        print(f"   左括号: {left_count}, 右括号: {right_count}")
        print()
    
    print("=" * 80)
    print(f"圆括号测试: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    # 测试方括号
    print()
    print("📋 r-basic-009: 方括号匹配")
    print()
    
    test_cases2 = [
        ("正确：成对方括号", "[1] 参考文献", True),
        ("错误：只有左方括号", "[1 参考文献", False),
        ("错误：只有右方括号", "1] 参考文献", False),
        ("正确：多对方括号", "[1] [2] [3]", True),
    ]
    
    passed2 = 0
    failed2 = 0
    
    for name, text, expected in test_cases2:
        left_count = text.count('[')
        right_count = text.count(']')
        match = (left_count == right_count)
        
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed2 += 1
        else:
            failed2 += 1
        
        print(f"{result} {name}: '{text}'")
        print(f"   左方括号: {left_count}, 右方括号: {right_count}")
        print()
    
    print("=" * 80)
    print(f"方括号测试: {passed2} 通过, {failed2} 失败")
    print("=" * 80)
    
    return passed + passed2, failed + failed2


def test_punctuation_spacing():
    """测试标点符号空格规则"""
    
    print()
    print("=" * 80)
    print("标点符号空格测试")
    print("=" * 80)
    print()
    
    # 测试中文标点后不应有空格
    print("📋 r-basic-011: 中文标点后不应有空格")
    print()
    
    test_cases = [
        {
            "name": "错误：逗号后有空格",
            "text": "这是内容， 继续",
            "expected": False
        },
        {
            "name": "错误：句号后有空格",
            "text": "这是内容。 继续",
            "expected": False
        },
        {
            "name": "正确：逗号后无空格",
            "text": "这是内容，继续",
            "expected": True
        },
        {
            "name": "正确：中文标点后接英文",
            "text": "这是内容， English",
            "expected": True  # 中文标点后接英文可以有空格
        },
    ]
    
    # 正则：不包含 中文标点+空格+中文
    pattern = r"^(?!.*[，。；：！？]\s+[\u4e00-\u9fa5]).*$"
    
    print(f"正则表达式: {pattern}")
    print()
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        text = test_case['text']
        expected = test_case['expected']
        
        match = re.match(pattern, text) is not None
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {test_case['name']}")
        print(f"   文本: '{text}'")
        print(f"   预期: {'通过' if expected else '不通过'}, 实际: {'通过' if match else '不通过'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    return passed, failed


def main():
    """主函数"""
    print("=" * 80)
    print("基本规则测试")
    print("=" * 80)
    print()
    
    total_passed = 0
    total_failed = 0
    
    # 运行所有测试
    p1, f1 = test_chinese_in_english_quotes()
    total_passed += p1
    total_failed += f1
    
    p2, f2 = test_chinese_spacing()
    total_passed += p2
    total_failed += f2
    
    p3, f3 = test_quote_matching()
    total_passed += p3
    total_failed += f3
    
    p4, f4 = test_bracket_matching()
    total_passed += p4
    total_failed += f4
    
    p5, f5 = test_punctuation_spacing()
    total_passed += p5
    total_failed += f5
    
    # 总结
    print()
    print("=" * 80)
    print("🎉 所有测试完成")
    print("=" * 80)
    print()
    print(f"📊 总计: {total_passed} 通过, {total_failed} 失败")
    print()
    
    print("📋 基本规则总结:")
    print()
    print('1. r-basic-001: 中文不能被英文引号包围')
    print('   ❌ 错误: "中文" 或 \'中文\'')
    print('   ✅ 正确: \u201c中文\u201d 或 \u300c中文\u300d')
    print()
    
    print("2. r-basic-002: 中文之间不能有空格")
    print("   ❌ 错误: 这是 中文")
    print("   ✅ 正确: 这是中文")
    print()
    
    print("3. r-basic-003~010: 引号和括号必须成对匹配")
    print("   - 中文引号: \u201c\u201d \u2018\u2019")
    print('   - 英文引号: "" \'\'')
    print("   - 括号: () （） [] 《》")
    print()
    
    print("4. r-basic-011~012: 中文标点前后不应有空格")
    print("   ❌ 错误: 内容 ，继续 或 内容， 继续")
    print("   ✅ 正确: 内容，继续")
    print()
    
    print("5. r-basic-013: 数字和中文单位之间不应有空格")
    print("   ❌ 错误: 3 个")
    print("   ✅ 正确: 3个")
    print()


if __name__ == "__main__":
    main()
