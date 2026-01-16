#!/usr/bin/env python3
"""
英文作者列表格式测试

测试英文作者列表的格式规则：
1. 样式：居中，小4号，Times New Roman
2. 内容：多作者用英文逗号+空格分隔，每个作者名后可以有数字编号
"""

import re

def test_author_list_en_pattern():
    """测试英文作者列表的正则表达式"""
    
    # 多作者格式的正则表达式（英文逗号+空格）
    multi_author_pattern = r"^[^,，；;]+\d*[*]?(,\s+[^,，；;]+\d*[*]?)*$"
    
    # 单作者格式的正则表达式
    single_author_pattern = r"^[^,，；;]+\d*[*]?$"
    
    print("=" * 80)
    print("英文作者列表格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        # (文本, 是否应该匹配, 说明)
        ("WANG Jiaping1*", True, "单作者，有编号和星号"),
        ("WANG Jiaping", True, "单作者，无编号"),
        ("WANG Jiaping1*, WANG Hao2", True, "两个作者，第一作者是通讯作者"),
        ("WANG Jiaping1, WANG Hao2*", True, "两个作者，第二作者是通讯作者"),
        ("WANG Jiaping1*, WANG Hao2, ZHANG San3", True, "三个作者"),
        ("WANG Jiaping1*, WANG Hao2*, ZHANG San3", True, "三个作者，两个通讯作者"),
        ("John Smith1*, Jane Doe2", True, "英文名字"),
        ("WANG Jiaping, WANG Hao", True, "两个作者，无编号"),
        ("WANG Jiaping1*, WANG Hao", True, "第一作者有编号，第二作者无编号"),
        
        # 错误格式
        ("WANG Jiaping1*,WANG Hao2", False, "❌ 逗号后缺少空格"),
        ("WANG Jiaping1*， WANG Hao2", False, "❌ 使用中文逗号"),
        ("WANG Jiaping1*;WANG Hao2", False, "❌ 使用分号"),
        ("WANG Jiaping1*, WANG Hao2,", False, "❌ 末尾有逗号"),
        (", WANG Hao2", False, "❌ 开头有逗号"),
    ]
    
    print("📋 测试用例：")
    print()
    
    passed = 0
    failed = 0
    
    for text, should_match, description in test_cases:
        # 判断是单作者还是多作者
        is_multi = "," in text
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


def test_author_list_en_examples():
    """测试实际的英文作者列表示例"""
    
    print()
    print("=" * 80)
    print("实际示例测试")
    print("=" * 80)
    print()
    
    multi_author_pattern = r"^[^,，；;]+\d*[*]?(,\s+[^,，；;]+\d*[*]?)*$"
    
    examples = [
        "WANG Jiaping1*, WANG Hao2",
        "John Smith1*, Jane Doe2, Bob Wilson3",
        "WANG Jiaping, WANG Hao",  # 无编号也可以
        "WANG Jiaping1*, WANG Hao",  # 混合：有编号和无编号
        "LI Ming1*, ZHANG Wei2*, WANG Qiang3",  # 多个通讯作者
    ]
    
    print("📝 实际示例：")
    print()
    
    for example in examples:
        match = re.match(multi_author_pattern, example)
        result = "✅" if match else "❌"
        print(f"{result} {example}")
        
        if match:
            # 提取作者信息
            authors = re.split(r',\s+', example)
            print(f"   作者数量: {len(authors)}")
            for i, author in enumerate(authors, 1):
                # 提取数字和星号
                number_match = re.search(r'(\d+)([*]?)', author)
                if number_match and number_match.group(1):
                    number = number_match.group(1)
                    is_corresponding = number_match.group(2) == "*"
                    name = author[:number_match.start()].strip()
                    print(f"   作者 {i}: {name} (单位编号: {number}{'，通讯作者' if is_corresponding else ''})")
                else:
                    print(f"   作者 {i}: {author.strip()} (无单位编号)")
        print()
    
    print("=" * 80)


def test_comparison():
    """对比中英文作者列表的差异"""
    
    print()
    print("=" * 80)
    print("中英文作者列表对比")
    print("=" * 80)
    print()
    
    print("📊 格式对比：")
    print()
    print("| 项目 | 中文作者列表 | 英文作者列表 |")
    print("|------|-------------|-------------|")
    print("| 字体 | 华文楷体 / Times New Roman | Times New Roman |")
    print("| 字号 | 小四 | 小四 |")
    print("| 对齐 | 居中 | 居中 |")
    print("| 分隔符 | 中文逗号（，） | 英文逗号+空格（, ） |")
    print("| 编号 | 必须有 | 可选 |")
    print("| 通讯作者 | 星号（*） | 星号（*） |")
    print()
    
    print("📝 示例对比：")
    print()
    print("中文：王嘉平1*，汪浩2")
    print("英文：WANG Jiaping1*, WANG Hao2")
    print()
    print("中文：张三1*，李四2，王五3")
    print("英文：ZHANG San1*, LI Si2, WANG Wu3")
    print()
    
    print("=" * 80)


def main():
    """主函数"""
    success = test_author_list_en_pattern()
    test_author_list_en_examples()
    test_comparison()
    
    if success:
        print()
        print("🎉 所有测试通过！")
        print()
        print("📋 配置总结：")
        print()
        print("1. 样式配置（styles.yaml）：")
        print("   .author-list-en:")
        print("     font:")
        print("       name_ascii: Times New Roman")
        print("       size: 小四")
        print("     paragraph:")
        print("       alignment: 居中")
        print()
        print("2. 内容规则（rules.yaml）：")
        print("   - r-009: 多作者格式规则（英文逗号+空格分隔）")
        print("   - r-010: 单作者格式规则")
        print("   - r-011: 通讯作者标记规则（星号）")
        print()
        print("3. 正则表达式：")
        print("   多作者: ^[^,，；;]+\\d*[*]?(,\\s+[^,，；;]+\\d*[*]?)*$")
        print("   单作者: ^[^,，；;]+\\d*[*]?$")
        print()
        print("4. 与中文作者列表的主要区别：")
        print("   - 分隔符：英文逗号+空格（, ）vs 中文逗号（，）")
        print("   - 编号：可选 vs 必须")
        print()
    else:
        print()
        print("❌ 部分测试失败，请检查正则表达式")
        print()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
