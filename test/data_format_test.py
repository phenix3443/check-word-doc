#!/usr/bin/env python3
"""
数据格式测试

测试规则：
数据信息表中"数据格式"字段必须是文件后缀名格式（如.txt、.csv、.json）
"""

import re

def test_data_format():
    """测试数据格式"""
    
    print("=" * 80)
    print("数据格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：单个后缀名（正确）",
            "text": ".txt",
            "expected": True
        },
        {
            "name": "场景2：常见格式csv（正确）",
            "text": ".csv",
            "expected": True
        },
        {
            "name": "场景3：JSON格式（正确）",
            "text": ".json",
            "expected": True
        },
        {
            "name": "场景4：Excel格式（正确）",
            "text": ".xlsx",
            "expected": True
        },
        {
            "name": "场景5：多个后缀名，中文顿号（正确）",
            "text": ".txt、.csv、.json",
            "expected": True
        },
        {
            "name": "场景6：多个后缀名，中文逗号（正确）",
            "text": ".txt，.csv，.json",
            "expected": True
        },
        {
            "name": "场景7：多个后缀名，英文逗号（正确）",
            "text": ".txt, .csv, .json",
            "expected": True
        },
        {
            "name": "场景8：多个后缀名，分号（正确）",
            "text": ".txt; .csv; .json",
            "expected": True
        },
        {
            "name": "场景9：大写后缀名（正确）",
            "text": ".TXT",
            "expected": True
        },
        {
            "name": "场景10：包含数字（正确）",
            "text": ".mp3",
            "expected": True
        },
        {
            "name": "场景11：复杂后缀名（正确）",
            "text": ".tar.gz",
            "expected": True
        },
        {
            "name": "场景12：缺少点号（错误）",
            "text": "txt",
            "expected": False
        },
        {
            "name": "场景13：只有点号（错误）",
            "text": ".",
            "expected": False
        },
        {
            "name": "场景14：包含中文（错误）",
            "text": ".文本",
            "expected": False
        },
        {
            "name": "场景15：包含空格（错误）",
            "text": ".txt file",
            "expected": False
        },
        {
            "name": "场景16：包含特殊字符（错误）",
            "text": ".txt@",
            "expected": False
        },
        {
            "name": "场景17：多个后缀，第二个缺少点（错误）",
            "text": ".txt、csv",
            "expected": False
        },
        {
            "name": "场景18：前面有文字（错误）",
            "text": "文本文件.txt",
            "expected": False
        },
    ]
    
    # 正则表达式
    # 格式：点号 + 字母数字，可以有多个（用顿号、逗号或分号分隔）
    pattern = r"^\.[a-zA-Z0-9]+(\s*[、，,;；]\s*\.[a-zA-Z0-9]+)*$"
    
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
    full_pattern = r"^\.[a-zA-Z0-9]+(\s*[、，,;；]\s*\.[a-zA-Z0-9]+)*$"
    
    print("正则表达式分解：")
    print()
    print("  ^                          - 字符串开头")
    print("  \\.                         - 点号（必须转义）")
    print("  [a-zA-Z0-9]+               - 一个或多个字母或数字")
    print("  (                          - 开始捕获组（后续后缀名）")
    print("    \\s*                      - 零个或多个空格")
    print("    [、，,;；]                - 分隔符（顿号、逗号、分号）")
    print("    \\s*                      - 零个或多个空格")
    print("    \\.                       - 点号")
    print("    [a-zA-Z0-9]+             - 一个或多个字母或数字")
    print("  )*                         - 零次或多次重复")
    print("  $                          - 字符串结尾")
    print()
    
    print("💡 匹配逻辑：")
    print("   1. 第一个后缀名：点号 + 字母数字")
    print("   2. 后续后缀名：分隔符 + 点号 + 字母数字")
    print("   3. 可以有零个或多个后续后缀名")
    print()
    
    print("=" * 80)


def test_common_formats():
    """测试常见文件格式"""
    
    print()
    print("=" * 80)
    print("常见文件格式示例")
    print("=" * 80)
    print()
    
    pattern = r"^\.[a-zA-Z0-9]+(\s*[、，,;；]\s*\.[a-zA-Z0-9]+)*$"
    
    formats = [
        # 文本格式
        (".txt", "纯文本"),
        (".doc", "Word文档"),
        (".docx", "Word文档（新版）"),
        (".pdf", "PDF文档"),
        
        # 数据格式
        (".csv", "逗号分隔值"),
        (".json", "JSON数据"),
        (".xml", "XML数据"),
        (".xlsx", "Excel表格"),
        
        # 图像格式
        (".jpg", "JPEG图像"),
        (".png", "PNG图像"),
        (".gif", "GIF图像"),
        (".svg", "矢量图"),
        
        # 压缩格式
        (".zip", "ZIP压缩"),
        (".rar", "RAR压缩"),
        (".tar", "TAR归档"),
        (".gz", "GZIP压缩"),
    ]
    
    print("📊 常见文件格式：")
    print()
    
    for text, desc in formats:
        match = re.match(pattern, text) is not None
        result = "✅" if match else "❌"
        print(f"   {result} {text:10} - {desc}")
    
    print()
    print("=" * 80)


def test_separator_formats():
    """测试不同分隔符"""
    
    print()
    print("=" * 80)
    print("分隔符格式测试")
    print("=" * 80)
    print()
    
    pattern = r"^\.[a-zA-Z0-9]+(\s*[、，,;；]\s*\.[a-zA-Z0-9]+)*$"
    
    separator_tests = [
        (".txt、.csv、.json", "中文顿号", True),
        (".txt，.csv，.json", "中文逗号", True),
        (".txt, .csv, .json", "英文逗号+空格", True),
        (".txt; .csv; .json", "分号+空格", True),
        (".txt；.csv；.json", "中文分号", True),
        (".txt  、  .csv", "多个空格", True),
        (".txt .csv", "只有空格（错误）", False),
        (".txt|.csv", "竖线（错误）", False),
    ]
    
    print("📊 分隔符测试：")
    print()
    
    for text, desc, expected in separator_tests:
        match = re.match(pattern, text) is not None
        result = "✅" if match == expected else "❌"
        status = "匹配" if match else "不匹配"
        print(f"   {result} {desc:25} {status:10} - {text}")
    
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
    print("   | 数据量                 | 10MB                               |")
    print("   | 数据格式               | .json、.csv ← 必须是文件后缀名      |")
    print("   | 所属学科               | 计算机科学                          |")
    print("   | ...                    | ...                                |")
    print("   " + "-" * 70)
    print()
    
    print("💡 验证逻辑：")
    print("   1. 在第一列中查找 key = '数据格式'")
    print("   2. 获取该行第二列的 value")
    print("   3. 检查 value 是否是文件后缀名格式")
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
            "错误": "缺少点号",
            "错误示例": "txt",
            "正确示例": ".txt",
            "说明": "后缀名必须以点号开头"
        },
        {
            "错误": "只有点号",
            "错误示例": ".",
            "正确示例": ".txt",
            "说明": "点号后必须有字母或数字"
        },
        {
            "错误": "使用中文",
            "错误示例": ".文本",
            "正确示例": ".txt",
            "说明": "后缀名只能包含字母和数字"
        },
        {
            "错误": "包含空格",
            "错误示例": ".txt file",
            "正确示例": ".txt",
            "说明": "后缀名中不能包含空格"
        },
        {
            "错误": "包含特殊字符",
            "错误示例": ".txt@",
            "正确示例": ".txt",
            "说明": "后缀名只能包含字母和数字"
        },
        {
            "错误": "多个后缀第二个缺少点",
            "错误示例": ".txt、csv",
            "正确示例": ".txt、.csv",
            "说明": "每个后缀名都必须以点号开头"
        },
        {
            "错误": "前面有描述文字",
            "错误示例": "文本文件.txt",
            "正确示例": ".txt",
            "说明": "不能包含额外的描述文字"
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
    test_data_format()
    test_pattern_breakdown()
    test_common_formats()
    test_separator_formats()
    test_table_structure()
    test_common_errors()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 规则配置（rules.yaml）：")
    print("   - r-045: 数据格式检查")
    print()
    print("2. 正则表达式：")
    print("   ^\\.[a-zA-Z0-9]+(\\s*[、，,;；]\\s*\\.[a-zA-Z0-9]+)*$")
    print()
    print("3. 格式要求：")
    print("   - 必须以点号（.）开头")
    print("   - 点号后跟字母或数字")
    print("   - 可以有多个后缀名，用分隔符分开")
    print("   - 支持的分隔符：顿号、逗号、分号")
    print()
    print("4. 正确示例：")
    print("   ✅ .txt（单个后缀）")
    print("   ✅ .csv（单个后缀）")
    print("   ✅ .txt、.csv、.json（多个后缀，顿号）")
    print("   ✅ .txt, .csv, .json（多个后缀，逗号）")
    print("   ✅ .xlsx（大小写混合）")
    print()
    print("5. 错误示例：")
    print("   ❌ txt（缺少点号）")
    print("   ❌ .（只有点号）")
    print("   ❌ .文本（包含中文）")
    print("   ❌ .txt file（包含空格）")
    print("   ❌ .txt、csv（第二个缺少点号）")
    print()


if __name__ == "__main__":
    main()
