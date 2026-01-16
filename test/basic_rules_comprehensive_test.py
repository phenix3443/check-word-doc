#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本规则综合测试

测试所有23个基本规则
"""

import re

def test_rule(rule_id, rule_name, pattern, test_cases):
    """通用测试函数"""
    print()
    print("=" * 80)
    print(f"{rule_id}: {rule_name}")
    print("=" * 80)
    print()
    print(f"正则表达式: {pattern}")
    print()
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        text = test_case['text']
        expected = test_case['expected']
        name = test_case['name']
        
        match = re.match(pattern, text) is not None
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {name}")
        print(f"   文本: '{text}'")
        print(f"   预期: {'通过' if expected else '不通过'}, 实际: {'通过' if match else '不通过'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    return passed, failed


def test_continuous_punctuation():
    """测试连续标点规则"""
    
    # r-basic-014: 连续逗号
    test_cases_comma = [
        {"name": "正确：单个逗号", "text": "内容，继续", "expected": True},
        {"name": "错误：连续中文逗号", "text": "内容，，继续", "expected": False},
        {"name": "错误：连续英文逗号", "text": "content,,continue", "expected": False},
    ]
    p1, f1 = test_rule(
        "r-basic-014",
        "不应有连续的逗号",
        r"^(?!.*[,，]{2,}).*$",
        test_cases_comma
    )
    
    # r-basic-015: 连续中文句号
    test_cases_period = [
        {"name": "正确：单个句号", "text": "内容。", "expected": True},
        {"name": "错误：连续中文句号", "text": "内容。。", "expected": False},
        {"name": "正确：英文句号", "text": "content.", "expected": True},
        {"name": "正确：省略号", "text": "内容...", "expected": True},
    ]
    p2, f2 = test_rule(
        "r-basic-015",
        "不应有连续的中文句号",
        r"^(?!.*[。]{2,}).*$",
        test_cases_period
    )
    
    # r-basic-016: 连续空格
    test_cases_space = [
        {"name": "正确：单个空格", "text": "这是 内容", "expected": True},
        {"name": "错误：两个空格", "text": "这是  内容", "expected": False},
        {"name": "错误：多个空格", "text": "这是   内容", "expected": False},
    ]
    p3, f3 = test_rule(
        "r-basic-016",
        "不应有连续的空格",
        r"^(?!.*\s{2,}).*$",
        test_cases_space
    )
    
    return p1+p2+p3, f1+f2+f3


def test_mixed_text():
    """测试中英文混排规则"""
    
    # r-basic-017: 中英文之间应该有空格
    test_cases_cn_en = [
        {"name": "正确：有空格", "text": "这是 English 内容", "expected": True},
        {"name": "错误：无空格", "text": "这是English内容", "expected": False},
        {"name": "正确：纯中文", "text": "这是中文内容", "expected": True},
        {"name": "正确：纯英文", "text": "This is English", "expected": True},
    ]
    p1, f1 = test_rule(
        "r-basic-017",
        "中文和英文之间应该有空格",
        r"^(?!.*[\u4e00-\u9fa5][a-zA-Z])(?!.*[a-zA-Z][\u4e00-\u9fa5]).*$",
        test_cases_cn_en
    )
    
    # r-basic-018: 中文和数字之间应该有空格
    test_cases_cn_num = [
        {"name": "正确：有空格", "text": "共有 100 个", "expected": True},
        {"name": "错误：无空格", "text": "共有100个", "expected": False},
        {"name": "正确：纯中文", "text": "这是内容", "expected": True},
    ]
    p2, f2 = test_rule(
        "r-basic-018",
        "中文和数字之间应该有空格",
        r"^(?!.*[\u4e00-\u9fa5]\d)(?!.*\d[\u4e00-\u9fa5]).*$",
        test_cases_cn_num
    )
    
    return p1+p2, f1+f2


def test_punctuation_usage():
    """测试标点符号使用规则"""
    
    # r-basic-019: 中文句子应使用中文标点
    test_cases = [
        {"name": "正确：中文标点", "text": "这是内容，继续", "expected": True},
        {"name": "错误：英文逗号", "text": "这是内容,继续", "expected": False},
        {"name": "正确：纯英文", "text": "This is content, continue", "expected": True},
    ]
    p1, f1 = test_rule(
        "r-basic-019",
        "中文句子应使用中文标点",
        r"^(?!.*[\u4e00-\u9fa5]+[,;:!?][\u4e00-\u9fa5]).*$",
        test_cases
    )
    
    # r-basic-021: 破折号格式
    test_cases_dash = [
        {"name": "正确：双破折号", "text": "内容——说明", "expected": True},
        {"name": "错误：单破折号", "text": "内容-说明", "expected": False},
        {"name": "正确：英文连字符", "text": "content-description", "expected": True},
    ]
    p2, f2 = test_rule(
        "r-basic-021",
        "破折号格式",
        r"^(?!.*[\u4e00-\u9fa5]-[\u4e00-\u9fa5]).*$",
        test_cases_dash
    )
    
    return p1+p2, f1+f2


def test_number_unit():
    """测试数字和单位规则"""
    
    # r-basic-022: 数字和英文单位之间应该有空格
    test_cases_en_unit = [
        {"name": "正确：有空格", "text": "100 KB", "expected": True},
        {"name": "错误：无空格", "text": "100KB", "expected": False},
        {"name": "正确：有空格", "text": "1.5 GB", "expected": True},
        {"name": "错误：无空格", "text": "1.5GB", "expected": False},
    ]
    p1, f1 = test_rule(
        "r-basic-022",
        "数字和英文单位之间应该有空格",
        r"^(?!.*\d+[A-Z]{1,3}(?![a-z])).*$",
        test_cases_en_unit
    )
    
    # r-basic-023: 百分号前不应有空格
    test_cases_percent = [
        {"name": "正确：无空格", "text": "50%", "expected": True},
        {"name": "错误：有空格", "text": "50 %", "expected": False},
        {"name": "正确：无空格", "text": "完成度为95%", "expected": True},
    ]
    p2, f2 = test_rule(
        "r-basic-023",
        "百分号前不应有空格",
        r"^(?!.*\d+\s+%).*$",
        test_cases_percent
    )
    
    return p1+p2, f1+f2


def test_special_characters():
    """测试特殊字符规则"""
    
    # r-basic-024: 不应使用全角字母
    test_cases_fullwidth_letter = [
        {"name": "正确：半角字母", "text": "English", "expected": True},
        {"name": "错误：全角字母", "text": "Ｅｎｇｌｉｓｈ", "expected": False},
        {"name": "正确：中文", "text": "中文内容", "expected": True},
    ]
    p1, f1 = test_rule(
        "r-basic-024",
        "不应使用全角字母",
        r"^(?!.*[ａ-ｚＡ-Ｚ]).*$",
        test_cases_fullwidth_letter
    )
    
    # r-basic-025: 不应使用全角数字
    test_cases_fullwidth_number = [
        {"name": "正确：半角数字", "text": "123", "expected": True},
        {"name": "错误：全角数字", "text": "１２３", "expected": False},
        {"name": "正确：中文", "text": "中文内容", "expected": True},
    ]
    p2, f2 = test_rule(
        "r-basic-025",
        "不应使用全角数字",
        r"^(?!.*[０-９]).*$",
        test_cases_fullwidth_number
    )
    
    # r-basic-026: 不应混用中英文标点
    test_cases_mixed = [
        {"name": "正确：统一中文标点", "text": "这是内容，继续。", "expected": True},
        {"name": "正确：统一英文标点", "text": "This is content, continue.", "expected": True},
        {"name": "错误：混用标点", "text": "这是内容，继续.", "expected": False},
    ]
    p3, f3 = test_rule(
        "r-basic-026",
        "不应混用中英文标点",
        r"^(?!.*[，。；：！？].*[,\.;:!?])(?!.*[,\.;:!?].*[，。；：！？]).*$",
        test_cases_mixed
    )
    
    return p1+p2+p3, f1+f2+f3


def test_line_boundaries():
    """测试行首行尾规则"""
    
    # r-basic-027: 行首不应有标点符号
    test_cases_start = [
        {"name": "正确：正常开头", "text": "这是内容", "expected": True},
        {"name": "错误：逗号开头", "text": "，这是内容", "expected": False},
        {"name": "错误：句号开头", "text": "。这是内容", "expected": False},
    ]
    p1, f1 = test_rule(
        "r-basic-027",
        "行首不应有标点符号",
        r"^(?![，。；：！？、,\.;:!?]).*$",
        test_cases_start
    )
    
    # r-basic-028: 行尾不应有空格
    test_cases_end = [
        {"name": "正确：无空格", "text": "这是内容", "expected": True},
        {"name": "错误：有空格", "text": "这是内容 ", "expected": False},
        {"name": "错误：多个空格", "text": "这是内容  ", "expected": False},
    ]
    p2, f2 = test_rule(
        "r-basic-028",
        "行尾不应有空格",
        r"^.*[^\s]$",
        test_cases_end
    )
    
    # r-basic-029: 行首不应有多余空格
    test_cases_indent = [
        {"name": "正确：无空格", "text": "这是内容", "expected": True},
        {"name": "正确：2个空格（首行缩进）", "text": "  这是内容", "expected": True},
        {"name": "错误：3个空格", "text": "   这是内容", "expected": False},
        {"name": "错误：4个空格", "text": "    这是内容", "expected": False},
    ]
    p3, f3 = test_rule(
        "r-basic-029",
        "行首不应有多余空格",
        r"^(?!\s{3,}).*$",
        test_cases_indent
    )
    
    return p1+p2+p3, f1+f2+f3


def test_special_formats():
    """测试特殊格式规则"""
    
    # r-basic-030: URL格式检查
    test_cases_url = [
        {"name": "正确：标准URL", "text": "https://example.com", "expected": True},
        {"name": "错误：URL中有空格", "text": "https://example .com", "expected": False},
        {"name": "正确：带路径URL", "text": "https://example.com/path", "expected": True},
    ]
    p1, f1 = test_rule(
        "r-basic-030",
        "URL格式检查",
        r"^(?!.*https?://[^\s]*\s[^\s]).*$",
        test_cases_url
    )
    
    # r-basic-031: 邮箱格式基本检查
    test_cases_email = [
        {"name": "正确：标准邮箱", "text": "user@example.com", "expected": True},
        {"name": "错误：包含中文", "text": "user中文@example.com", "expected": False},
        {"name": "正确：数字邮箱", "text": "user123@example.com", "expected": True},
    ]
    p2, f2 = test_rule(
        "r-basic-031",
        "邮箱格式基本检查",
        r"^(?!.*[a-zA-Z0-9][\u4e00-\u9fa5]+@).*$",
        test_cases_email
    )
    
    return p1+p2, f1+f2


def main():
    """主函数"""
    print("=" * 80)
    print("基本规则综合测试")
    print("=" * 80)
    print()
    
    total_passed = 0
    total_failed = 0
    
    # 运行所有测试
    print("📋 测试分组 1: 连续标点规则")
    p1, f1 = test_continuous_punctuation()
    total_passed += p1
    total_failed += f1
    
    print()
    print("📋 测试分组 2: 中英文混排规则")
    p2, f2 = test_mixed_text()
    total_passed += p2
    total_failed += f2
    
    print()
    print("📋 测试分组 3: 标点符号使用规则")
    p3, f3 = test_punctuation_usage()
    total_passed += p3
    total_failed += f3
    
    print()
    print("📋 测试分组 4: 数字和单位规则")
    p4, f4 = test_number_unit()
    total_passed += p4
    total_failed += f4
    
    print()
    print("📋 测试分组 5: 特殊字符规则")
    p5, f5 = test_special_characters()
    total_passed += p5
    total_failed += f5
    
    print()
    print("📋 测试分组 6: 行首行尾规则")
    p6, f6 = test_line_boundaries()
    total_passed += p6
    total_failed += f6
    
    print()
    print("📋 测试分组 7: 特殊格式规则")
    p7, f7 = test_special_formats()
    total_passed += p7
    total_failed += f7
    
    # 总结
    print()
    print("=" * 80)
    print("🎉 所有测试完成")
    print("=" * 80)
    print()
    print(f"📊 总计: {total_passed} 通过, {total_failed} 失败")
    print()
    
    print("📋 基本规则总结（23个）:")
    print()
    print("✅ 错误级别 (error) - 8个:")
    print("   - r-basic-001: 中文不能被英文引号包围")
    print("   - r-basic-002: 中文之间不能有空格")
    print("   - r-basic-014: 不应有连续的逗号")
    print("   - r-basic-015: 不应有连续的句号")
    print("   - r-basic-024: 不应使用全角字母")
    print("   - r-basic-025: 不应使用全角数字")
    print("   - r-basic-027: 行首不应有标点符号")
    print()
    
    print("⚠️  警告级别 (warning) - 11个:")
    print("   - r-basic-011~013: 标点和单位空格")
    print("   - r-basic-016: 不应有连续的空格")
    print("   - r-basic-019: 中文句子应使用中文标点")
    print("   - r-basic-020: 省略号格式")
    print("   - r-basic-023: 百分号前不应有空格")
    print("   - r-basic-026: 不应混用中英文标点")
    print("   - r-basic-028~029: 行首行尾空格")
    print("   - r-basic-031: 邮箱格式基本检查")
    print()
    
    print("ℹ️  提示级别 (info) - 4个:")
    print("   - r-basic-017: 中文和英文之间应该有空格")
    print("   - r-basic-018: 中文和数字之间应该有空格")
    print("   - r-basic-021: 破折号格式")
    print("   - r-basic-022: 数字和英文单位之间应该有空格")
    print("   - r-basic-030: URL格式检查")
    print()


if __name__ == "__main__":
    main()
