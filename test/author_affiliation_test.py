#!/usr/bin/env python3
"""
作者单位格式测试

测试作者单位的格式规则：
1. 样式：居中，5号，宋体/Times New Roman
2. 内容：单位/机构，城市  邮编（注意：城市和邮编之间有两个空格）
3. 多作者时：编号. 单位/机构，城市  邮编
"""

import re

def test_author_affiliation_pattern():
    """测试作者单位的正则表达式"""
    
    # 多作者格式的正则表达式（有编号）
    multi_author_pattern = r"^\d+\.\s+.+，.+\s{2,}\d{6}$"
    
    # 单作者格式的正则表达式（无编号）
    single_author_pattern = r"^[^\d].+，.+\s{2,}\d{6}$"
    
    print("=" * 80)
    print("作者单位格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        # (文本, 是单作者, 是否应该匹配, 说明)
        ("1. 北京大学计算机学院，北京  100871", False, True, "多作者，标准格式"),
        ("2. 清华大学软件学院，北京  100084", False, True, "多作者，第二个单位"),
        ("1. 中国科学院计算技术研究所，北京  100190", False, True, "多作者，长单位名"),
        ("北京大学计算机学院，北京  100871", True, True, "单作者，无编号"),
        ("清华大学软件学院，北京  100084", True, True, "单作者，无编号"),
        
        # 错误格式
        ("1.北京大学计算机学院，北京  100871", False, False, "❌ 编号后缺少空格"),
        ("1. 北京大学计算机学院,北京  100871", False, False, "❌ 使用英文逗号"),
        ("1. 北京大学计算机学院，北京 100871", False, False, "❌ 城市和邮编之间只有一个空格"),
        ("1. 北京大学计算机学院，北京100871", False, False, "❌ 城市和邮编之间没有空格"),
        ("1. 北京大学计算机学院，北京  10087", False, False, "❌ 邮编不是6位"),
        ("北京大学计算机学院 北京  100871", True, False, "❌ 缺少逗号"),
        ("1. 北京大学计算机学院，北京  100871", True, False, "❌ 单作者不应有编号"),
    ]
    
    print("📋 测试用例：")
    print()
    
    passed = 0
    failed = 0
    
    for text, is_single, should_match, description in test_cases:
        # 选择对应的正则表达式
        pattern = single_author_pattern if is_single else multi_author_pattern
        pattern_name = "单作者" if is_single else "多作者"
        
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


def test_author_affiliation_examples():
    """测试实际的作者单位示例"""
    
    print()
    print("=" * 80)
    print("实际示例测试")
    print("=" * 80)
    print()
    
    multi_author_pattern = r"^\d+\.\s+.+，.+\s{2,}\d{6}$"
    single_author_pattern = r"^[^\d].+，.+\s{2,}\d{6}$"
    
    print("📝 多作者示例：")
    print()
    
    multi_examples = [
        "1. 北京大学计算机学院，北京  100871",
        "2. 清华大学软件学院，北京  100084",
        "3. 中国科学院计算技术研究所，北京  100190",
        "1. 浙江大学计算机科学与技术学院，杭州  310027",
    ]
    
    for example in multi_examples:
        match = re.match(multi_author_pattern, example)
        result = "✅" if match else "❌"
        print(f"{result} {example}")
        
        if match:
            # 提取信息
            parts = example.split('，')
            if len(parts) == 2:
                affiliation_part = parts[0]
                location_part = parts[1]
                
                # 提取编号和单位
                number_match = re.match(r'^(\d+)\.\s+(.+)$', affiliation_part)
                if number_match:
                    number = number_match.group(1)
                    affiliation = number_match.group(2)
                    
                    # 提取城市和邮编
                    location_match = re.match(r'^(.+?)\s{2,}(\d{6})$', location_part)
                    if location_match:
                        city = location_match.group(1)
                        zipcode = location_match.group(2)
                        
                        print(f"   编号: {number}")
                        print(f"   单位: {affiliation}")
                        print(f"   城市: {city}")
                        print(f"   邮编: {zipcode}")
        print()
    
    print("📝 单作者示例：")
    print()
    
    single_examples = [
        "北京大学计算机学院，北京  100871",
        "清华大学软件学院，北京  100084",
        "中国科学院计算技术研究所，北京  100190",
    ]
    
    for example in single_examples:
        match = re.match(single_author_pattern, example)
        result = "✅" if match else "❌"
        print(f"{result} {example}")
        
        if match:
            # 提取信息
            parts = example.split('，')
            if len(parts) == 2:
                affiliation = parts[0]
                location_part = parts[1]
                
                # 提取城市和邮编
                location_match = re.match(r'^(.+?)\s{2,}(\d{6})$', location_part)
                if location_match:
                    city = location_match.group(1)
                    zipcode = location_match.group(2)
                    
                    print(f"   单位: {affiliation}")
                    print(f"   城市: {city}")
                    print(f"   邮编: {zipcode}")
        print()
    
    print("=" * 80)


def main():
    """主函数"""
    success = test_author_affiliation_pattern()
    test_author_affiliation_examples()
    
    if success:
        print()
        print("🎉 所有测试通过！")
        print()
        print("📋 配置总结：")
        print()
        print("1. 样式配置（styles.yaml）：")
        print("   .author-affiliation:")
        print("     font:")
        print("       name_eastasia: 宋体")
        print("       name_ascii: Times New Roman")
        print("       size: 五号")
        print("     paragraph:")
        print("       alignment: 居中")
        print()
        print("2. 内容规则（rules.yaml）：")
        print("   - r-004: 第一个作者单位编号（必须以 '1.' 开头）")
        print("   - r-005: 第二个作者单位编号（必须以 '2.' 开头）")
        print("   - r-006: 多作者单位格式（编号. 单位/机构，城市  邮编）")
        print("   - r-007: 单作者单位格式（单位/机构，城市  邮编）")
        print()
        print("3. 正则表达式：")
        print("   多作者: ^\\d+\\.\\s+.+，.+\\s{2,}\\d{6}$")
        print("   单作者: ^[^\\d].+，.+\\s{2,}\\d{6}$")
        print()
        print("4. 格式要点：")
        print("   - 使用中文逗号（，）分隔单位和城市")
        print("   - 城市和邮编之间有两个空格")
        print("   - 邮编必须是6位数字")
        print("   - 多作者时，编号后有一个空格")
        print()
    else:
        print()
        print("❌ 部分测试失败，请检查正则表达式")
        print()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
