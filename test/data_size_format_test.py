#!/usr/bin/env python3
"""
数据量格式测试

测试规则：
数据信息表中"数据量"字段必须是文件大小格式（如100KB、10MB、1.5GB）
"""

import re

def test_data_size_format():
    """测试数据量格式"""
    
    print("=" * 80)
    print("数据量格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标准格式KB（正确）",
            "text": "100KB",
            "expected": True
        },
        {
            "name": "场景2：标准格式MB（正确）",
            "text": "10MB",
            "expected": True
        },
        {
            "name": "场景3：标准格式GB（正确）",
            "text": "1GB",
            "expected": True
        },
        {
            "name": "场景4：小数格式（正确）",
            "text": "1.5GB",
            "expected": True
        },
        {
            "name": "场景5：带空格（正确）",
            "text": "100 KB",
            "expected": True
        },
        {
            "name": "场景6：TB单位（正确）",
            "text": "2TB",
            "expected": True
        },
        {
            "name": "场景7：PB单位（正确）",
            "text": "5PB",
            "expected": True
        },
        {
            "name": "场景8：字节B（正确）",
            "text": "1024B",
            "expected": True
        },
        {
            "name": "场景9：小数点多位（正确）",
            "text": "3.14159MB",
            "expected": True
        },
        {
            "name": "场景10：多个空格（正确）",
            "text": "100  MB",
            "expected": True
        },
        {
            "name": "场景11：缺少单位（错误）",
            "text": "100",
            "expected": False
        },
        {
            "name": "场景12：小写单位（错误）",
            "text": "100kb",
            "expected": False
        },
        {
            "name": "场景13：错误的单位（错误）",
            "text": "100M",
            "expected": False
        },
        {
            "name": "场景14：包含中文（错误）",
            "text": "100兆字节",
            "expected": False
        },
        {
            "name": "场景15：非数字开头（错误）",
            "text": "约100MB",
            "expected": False
        },
        {
            "name": "场景16：多余内容（错误）",
            "text": "100MB左右",
            "expected": False
        },
        {
            "name": "场景17：逗号分隔（错误）",
            "text": "1,000MB",
            "expected": False
        },
        {
            "name": "场景18：负数（错误）",
            "text": "-100MB",
            "expected": False
        },
    ]
    
    # 正则表达式
    # 格式：数字（可选小数）+ 可选空格 + 单位（B、KB、MB、GB、TB、PB、EB）
    pattern = r"^\d+(\.\d+)?\s*(B|KB|MB|GB|TB|PB|EB)$"
    
    print("📋 测试用例：")
    print()
    print(f"正则表达式: {pattern}")
    print()
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        text = test_case['text']
        expected = test_case['expected']
        
        # 检查是否匹配
        match = re.match(pattern, text) is not None
        
        # 判断结果
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        status = "通过" if is_correct else "失败"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {test_case['name']}")
        print(f"   文本: '{text}'")
        print(f"   预期: {'匹配' if expected else '不匹配'}, 实际: {'匹配' if match else '不匹配'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)


def test_pattern_breakdown():
    """测试正则表达式分解"""
    
    print()
    print("=" * 80)
    print("正则表达式详解")
    print("=" * 80)
    print()
    
    # 完整的正则表达式
    full_pattern = r"^\d+(\.\d+)?\s*(B|KB|MB|GB|TB|PB|EB)$"
    
    print("正则表达式分解：")
    print()
    print("  ^                          - 字符串开头")
    print("  \\d+                        - 一个或多个数字（整数部分）")
    print("  (\\.\\d+)?                  - 可选的小数部分")
    print("                               （点 + 一个或多个数字）")
    print("  \\s*                        - 零个或多个空格")
    print("  (B|KB|MB|GB|TB|PB|EB)      - 单位（必须大写）")
    print("  $                          - 字符串结尾")
    print()
    
    print("💡 支持的单位：")
    print("   - B   : 字节（Byte）")
    print("   - KB  : 千字节（Kilobyte）")
    print("   - MB  : 兆字节（Megabyte）")
    print("   - GB  : 吉字节（Gigabyte）")
    print("   - TB  : 太字节（Terabyte）")
    print("   - PB  : 拍字节（Petabyte）")
    print("   - EB  : 艾字节（Exabyte）")
    print()
    
    print("=" * 80)


def test_unit_examples():
    """测试各种单位示例"""
    
    print()
    print("=" * 80)
    print("各种单位示例")
    print("=" * 80)
    print()
    
    pattern = r"^\d+(\.\d+)?\s*(B|KB|MB|GB|TB|PB|EB)$"
    
    examples = [
        ("1024B", "字节"),
        ("100KB", "千字节"),
        ("10MB", "兆字节"),
        ("1GB", "吉字节"),
        ("2TB", "太字节"),
        ("5PB", "拍字节"),
        ("10EB", "艾字节"),
    ]
    
    print("📊 单位示例：")
    print()
    
    for text, desc in examples:
        match = re.match(pattern, text) is not None
        result = "✅" if match else "❌"
        print(f"   {result} {text:15} - {desc}")
    
    print()
    print("=" * 80)


def test_decimal_formats():
    """测试小数格式"""
    
    print()
    print("=" * 80)
    print("小数格式测试")
    print("=" * 80)
    print()
    
    pattern = r"^\d+(\.\d+)?\s*(B|KB|MB|GB|TB|PB|EB)$"
    
    decimal_tests = [
        ("1.5GB", True, "标准小数"),
        ("10.25MB", True, "两位小数"),
        ("3.14159GB", True, "多位小数"),
        ("0.5MB", True, "零开头的小数"),
        (".5MB", False, "缺少整数部分"),
        ("1.MB", False, "缺少小数部分"),
        ("1..5MB", False, "多个小数点"),
    ]
    
    print("📊 小数格式：")
    print()
    
    for text, expected, desc in decimal_tests:
        match = re.match(pattern, text) is not None
        result = "✅" if match == expected else "❌"
        status = "匹配" if match else "不匹配"
        print(f"   {result} {text:20} {status:10} - {desc}")
    
    print()
    print("=" * 80)


def test_table_structure():
    """测试表格结构"""
    
    print()
    print("=" * 80)
    print("表格结构（Key-Value模式）")
    print("=" * 80)
    print()
    
    print("📊 数据库（集）基本信息简介表结构：")
    print()
    print("   表 1： 数据库（集）基本信息简介")
    print("   " + "-" * 70)
    print("   | Key (第一列)            | Value (第二列)                      |")
    print("   " + "-" * 70)
    print("   | 数据库（集）名称        | 区块链智能合约数据库                |")
    print("   | 数据作者               | 张三、李四、王五                    |")
    print("   | 数据量                 | 10MB ← 必须是文件大小格式           |")
    print("   | 所属学科               | 计算机科学                          |")
    print("   | ...                    | ...                                |")
    print("   " + "-" * 70)
    print()
    
    print("💡 验证逻辑：")
    print("   1. 在第一列中查找 key = '数据量'")
    print("   2. 获取该行第二列的 value")
    print("   3. 检查 value 是否符合文件大小格式")
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
            "错误": "缺少单位",
            "错误示例": "100",
            "正确示例": "100MB",
            "说明": "必须包含单位（B、KB、MB、GB等）"
        },
        {
            "错误": "小写单位",
            "错误示例": "100kb",
            "正确示例": "100KB",
            "说明": "单位必须大写"
        },
        {
            "错误": "错误的单位",
            "错误示例": "100M",
            "正确示例": "100MB",
            "说明": "单位必须完整（MB而不是M）"
        },
        {
            "错误": "使用中文",
            "错误示例": "100兆字节",
            "正确示例": "100MB",
            "说明": "必须使用英文单位"
        },
        {
            "错误": "包含描述性文字",
            "错误示例": "约100MB",
            "正确示例": "100MB",
            "说明": "不能包含额外的文字"
        },
        {
            "错误": "使用千分位逗号",
            "错误示例": "1,000MB",
            "正确示例": "1000MB",
            "说明": "不支持千分位分隔符"
        },
    ]
    
    print("❌ 常见错误：")
    print()
    
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error['错误']}")
        print(f"   ❌ 错误: {error['错误示例']}")
        print(f"   ✅ 正确: {error['正确示例']}")
        print(f"   💡 说明: {error['说明']}")
        print()
    
    print("=" * 80)


def main():
    """主函数"""
    test_data_size_format()
    test_pattern_breakdown()
    test_unit_examples()
    test_decimal_formats()
    test_table_structure()
    test_common_errors()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 规则配置（rules.yaml）：")
    print("   - r-044: 数据量格式检查")
    print()
    print("2. 正则表达式：")
    print("   ^\\d+(\\.\\d+)?\\s*(B|KB|MB|GB|TB|PB|EB)$")
    print()
    print("3. 格式要求：")
    print("   - 数字（整数或小数）")
    print("   - 可选空格")
    print("   - 单位（B、KB、MB、GB、TB、PB、EB）")
    print("   - 单位必须大写")
    print()
    print("4. 正确示例：")
    print("   ✅ 100KB")
    print("   ✅ 10MB")
    print("   ✅ 1.5GB")
    print("   ✅ 2TB")
    print("   ✅ 100 MB（带空格）")
    print()
    print("5. 错误示例：")
    print("   ❌ 100（缺少单位）")
    print("   ❌ 100kb（小写单位）")
    print("   ❌ 100M（单位不完整）")
    print("   ❌ 100兆字节（使用中文）")
    print("   ❌ 约100MB（包含额外文字）")
    print()


if __name__ == "__main__":
    main()
