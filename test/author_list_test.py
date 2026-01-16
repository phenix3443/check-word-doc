#!/usr/bin/env python3
"""
作者列表格式测试

测试作者列表的格式规则：
1. 样式：居中，小4号，华文楷体/Times New Roman
2. 内容：多作者用中文逗号分隔，每个作者名后有数字编号
"""

import re

def test_author_list_pattern():
    """测试作者列表的正则表达式"""
    
    # 多作者格式的正则表达式
    # 注意：作者名中不能包含任何分隔符（包括中文逗号）
    multi_author_pattern = r"^[^,;；、，]+\d+[*]?(，[^,;；、，]+\d+[*]?)*$"
    
    # 单作者格式的正则表达式
    single_author_pattern = r"^[^,;；、，]+\d+[*]?$"
    
    print("=" * 80)
    print("作者列表格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        # (文本, 是否应该匹配, 说明)
        ("王嘉平1*", True, "单作者，有星号（通讯作者）"),
        ("王嘉平1", True, "单作者，无星号"),
        ("王嘉平1*，汪浩2", True, "两个作者，第一作者是通讯作者"),
        ("王嘉平1，汪浩2*", True, "两个作者，第二作者是通讯作者"),
        ("王嘉平1*，汪浩2，张三3", True, "三个作者，第一作者是通讯作者"),
        ("王嘉平1*，汪浩2*，张三3", True, "三个作者，两个通讯作者"),
        
        # 错误格式
        ("王嘉平", False, "❌ 缺少数字编号"),
        ("王嘉平*", False, "❌ 缺少数字编号（只有星号）"),
        ("王嘉平1,汪浩2", False, "❌ 使用英文逗号"),
        ("王嘉平1;汪浩2", False, "❌ 使用分号"),
        ("王嘉平1、汪浩2", False, "❌ 使用顿号"),
        ("王嘉平1，汪浩", False, "❌ 第二个作者缺少数字"),
        ("王嘉平，汪浩2", False, "❌ 第一个作者缺少数字"),
    ]
    
    print("📋 测试用例：")
    print()
    
    passed = 0
    failed = 0
    
    for text, should_match, description in test_cases:
        # 判断是单作者还是多作者
        is_multi = "，" in text
        pattern = multi_author_pattern if is_multi else single_author_pattern
        pattern_name = "多作者" if is_multi else "单作者"
        
        # 测试匹配
        match = re.match(pattern, text)
        is_match = match is not None
        
        # 判断结果
        result = "✅" if is_match == should_match else "❌"
        status = "PASS" if is_match == should_match else "FAIL"
        
        if is_match == should_match:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} [{status}] ({pattern_name}) {description}")
        print(f"   文本: {text}")
        print(f"   期望: {'匹配' if should_match else '不匹配'}, 实际: {'匹配' if is_match else '不匹配'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    return failed == 0


def test_author_list_examples():
    """测试实际的作者列表示例"""
    
    print()
    print("=" * 80)
    print("实际示例测试")
    print("=" * 80)
    print()
    
    multi_author_pattern = r"^[^,;；、，]+\d+[*]?(，[^,;；、，]+\d+[*]?)*$"
    
    examples = [
        "王嘉平1*，汪浩2",
        "张三1*，李四2，王五3",
        "John Smith1*，Jane Doe2",  # 英文名字也支持
        "王嘉平1*，John Smith2",  # 中英文混合
    ]
    
    print("📝 实际示例：")
    print()
    
    for example in examples:
        match = re.match(multi_author_pattern, example)
        result = "✅" if match else "❌"
        print(f"{result} {example}")
        
        if match:
            # 提取作者信息
            authors = example.split("，")
            print(f"   作者数量: {len(authors)}")
            for i, author in enumerate(authors, 1):
                # 提取数字和星号
                number_match = re.search(r'(\d+)([*]?)', author)
                if number_match:
                    number = number_match.group(1)
                    is_corresponding = number_match.group(2) == "*"
                    name = author[:number_match.start()].strip()
                    print(f"   作者 {i}: {name} (单位编号: {number}{'，通讯作者' if is_corresponding else ''})")
        print()
    
    print("=" * 80)


def main():
    """主函数"""
    success = test_author_list_pattern()
    test_author_list_examples()
    
    if success:
        print()
        print("🎉 所有测试通过！")
        print()
        print("📋 配置总结：")
        print()
        print("1. 样式配置（styles.yaml）：")
        print("   .author-list:")
        print("     font:")
        print("       name_eastasia: 华文楷体")
        print("       name_ascii: Times New Roman")
        print("       size: 小四")
        print("     paragraph:")
        print("       alignment: 居中")
        print()
        print("2. 内容规则（rules.yaml）：")
        print("   - r-001: 多作者格式规则（中文逗号分隔 + 数字编号）")
        print("   - r-002: 单作者格式规则（数字编号）")
        print("   - r-003: 通讯作者标记规则（星号）")
        print()
        print("3. 正则表达式：")
        print("   多作者: ^[^,;；、，]+\\d+[*]?(，[^,;；、，]+\\d+[*]?)*$")
        print("   单作者: ^[^,;；、，]+\\d+[*]?$")
        print()
    else:
        print()
        print("❌ 部分测试失败，请检查正则表达式")
        print()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
