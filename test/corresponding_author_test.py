#!/usr/bin/env python3
"""
通讯作者格式测试

测试通讯作者的格式规则：
1. 样式：居中，5号，宋体/Times New Roman
2. 格式："* 论文通信作者：作者名（邮箱）"
"""

import re

def test_corresponding_author_pattern():
    """测试通讯作者的正则表达式"""
    
    # 通讯作者格式的正则表达式
    pattern = r"^\*\s*论文通信作者[：:].+（[^）]+）$"
    
    print("=" * 80)
    print("通讯作者格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        # (文本, 是否应该匹配, 说明)
        ("* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）", True, "标准格式（中文冒号）"),
        ("*论文通信作者：王嘉平（wangjiaping@pku.edu.cn）", True, "星号后无空格"),
        ("* 论文通信作者:王嘉平（wangjiaping@pku.edu.cn）", True, "英文冒号"),
        ("* 论文通信作者：张三（zhangsan@tsinghua.edu.cn）", True, "标准格式"),
        ("* 论文通信作者：李四（lisi@cas.cn）", True, "短邮箱"),
        ("* 论文通信作者：王五（wangwu@zju.edu.cn）", True, "标准格式"),
        
        # 错误格式
        ("论文通信作者：王嘉平（wangjiaping@pku.edu.cn）", False, "❌ 缺少星号"),
        ("* 通信作者：王嘉平（wangjiaping@pku.edu.cn）", False, "❌ 缺少'论文'"),
        ("* 论文通信作者 王嘉平（wangjiaping@pku.edu.cn）", False, "❌ 缺少冒号"),
        ("* 论文通信作者：王嘉平", False, "❌ 缺少邮箱"),
        ("* 论文通信作者：王嘉平(wangjiaping@pku.edu.cn)", False, "❌ 使用英文括号"),
        ("* 论文通信作者：（wangjiaping@pku.edu.cn）", False, "❌ 缺少作者名"),
        ("* 论文通信作者：王嘉平（）", False, "❌ 邮箱为空"),
    ]
    
    print("📋 测试用例：")
    print()
    
    passed = 0
    failed = 0
    
    for text, should_match, description in test_cases:
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
        
        print(f"{result} [{status}] {description}")
        print(f"   文本: {text}")
        print(f"   期望: {'匹配' if should_match else '不匹配'}, 实际: {'匹配' if is_match else '不匹配'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    return failed == 0


def test_corresponding_author_examples():
    """测试实际的通讯作者示例"""
    
    print()
    print("=" * 80)
    print("实际示例测试")
    print("=" * 80)
    print()
    
    pattern = r"^\*\s*论文通信作者[：:].+（[^）]+）$"
    
    examples = [
        "* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）",
        "* 论文通信作者：张三（zhangsan@tsinghua.edu.cn）",
        "* 论文通信作者：李四（lisi@cas.cn）",
        "* 论文通信作者：John Smith（john.smith@university.edu）",
    ]
    
    print("📝 实际示例：")
    print()
    
    for example in examples:
        match = re.match(pattern, example)
        result = "✅" if match else "❌"
        print(f"{result} {example}")
        
        if match:
            # 提取信息
            # 尝试提取作者名和邮箱
            info_match = re.match(r'^\*\s*论文通信作者[：:](.+)（([^）]+)）$', example)
            if info_match:
                author_name = info_match.group(1).strip()
                email = info_match.group(2).strip()
                print(f"   作者: {author_name}")
                print(f"   邮箱: {email}")
        print()
    
    print("=" * 80)


def test_email_validation():
    """测试邮箱格式验证"""
    
    print()
    print("=" * 80)
    print("邮箱格式验证（可选增强）")
    print("=" * 80)
    print()
    
    # 更严格的邮箱验证正则表达式
    strict_pattern = r"^\*\s*论文通信作者[：:].+（[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}）$"
    
    print("如果需要更严格的邮箱格式验证，可以使用：")
    print()
    print("正则表达式：")
    print(f"  {strict_pattern}")
    print()
    
    test_cases = [
        ("* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）", True, "有效邮箱"),
        ("* 论文通信作者：张三（zhang.san@tsinghua.edu.cn）", True, "有效邮箱（带点）"),
        ("* 论文通信作者：李四（lisi123@cas.cn）", True, "有效邮箱（带数字）"),
        ("* 论文通信作者：王五（wangwu@invalid）", False, "无效邮箱（缺少域名后缀）"),
        ("* 论文通信作者：赵六（zhaoliu@@pku.edu.cn）", False, "无效邮箱（双@）"),
    ]
    
    print("测试结果：")
    print()
    
    for text, should_match, description in test_cases:
        match = re.match(strict_pattern, text)
        is_match = match is not None
        result = "✅" if is_match == should_match else "❌"
        print(f"{result} {description}: {text}")
    
    print()
    print("=" * 80)


def main():
    """主函数"""
    success = test_corresponding_author_pattern()
    test_corresponding_author_examples()
    test_email_validation()
    
    if success:
        print()
        print("🎉 所有测试通过！")
        print()
        print("📋 配置总结：")
        print()
        print("1. 样式配置（styles.yaml）：")
        print("   .corresponding-author:")
        print("     font:")
        print("       name_eastasia: 宋体")
        print("       name_ascii: Times New Roman")
        print("       size: 五号")
        print("     paragraph:")
        print("       alignment: 居中")
        print()
        print("2. 内容规则（rules.yaml）：")
        print("   - r-003: 通信作者格式检查")
        print()
        print("3. 正则表达式：")
        print("   基础版本: ^\\*\\s*论文通信作者[：:].+（[^）]+）$")
        print("   严格版本: ^\\*\\s*论文通信作者[：:].+（[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}）$")
        print()
        print("4. 格式要点：")
        print("   - 必须以星号（*）开头")
        print("   - 包含'论文通信作者'标识")
        print("   - 冒号后是作者名")
        print("   - 邮箱用中文括号（）括起来")
        print()
    else:
        print()
        print("❌ 部分测试失败，请检查正则表达式")
        print()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
