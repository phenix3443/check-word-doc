#!/usr/bin/env python3
"""
英文通讯作者格式测试

测试英文通讯作者的格式规则：
1. 样式：Times New Roman，5号字，居中
2. 内容：必须符合"*Email: author@mail.cn"格式
"""

import re

def test_corresponding_author_en_format():
    """测试英文通讯作者格式"""
    
    print("=" * 80)
    print("英文通讯作者格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标准格式（正确）",
            "text": "*Email: author@mail.cn",
            "expected": True
        },
        {
            "name": "场景2：标准格式（.com域名，正确）",
            "text": "*Email: john.doe@example.com",
            "expected": True
        },
        {
            "name": "场景3：标准格式（.edu域名，正确）",
            "text": "*Email: researcher@university.edu.cn",
            "expected": True
        },
        {
            "name": "场景4：包含数字和下划线（正确）",
            "text": "*Email: user_123@test-domain.org",
            "expected": True
        },
        {
            "name": "场景5：缺少星号（错误）",
            "text": "Email: author@mail.cn",
            "expected": False
        },
        {
            "name": "场景6：Email后缺少冒号（错误）",
            "text": "*Email author@mail.cn",
            "expected": False
        },
        {
            "name": "场景7：冒号后缺少空格（错误）",
            "text": "*Email:author@mail.cn",
            "expected": False
        },
        {
            "name": "场景8：邮箱格式错误（缺少@）",
            "text": "*Email: authormail.cn",
            "expected": False
        },
        {
            "name": "场景9：邮箱格式错误（缺少域名后缀）",
            "text": "*Email: author@mail",
            "expected": False
        },
        {
            "name": "场景10：包含多余内容（错误）",
            "text": "*Email: author@mail.cn (corresponding author)",
            "expected": False
        },
        {
            "name": "场景11：小写email（错误，必须是Email）",
            "text": "*email: author@mail.cn",
            "expected": False
        },
        {
            "name": "场景12：多个空格（正确，\\s+匹配）",
            "text": "*Email:  author@mail.cn",
            "expected": True
        },
    ]
    
    # 正则表达式
    pattern = r"^\*Email:\s+[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
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
        print(f"   文本: {text}")
        print(f"   预期: {'匹配' if expected else '不匹配'}, 实际: {'匹配' if match else '不匹配'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)


def test_email_pattern_details():
    """测试邮箱正则表达式的细节"""
    
    print()
    print("=" * 80)
    print("邮箱格式正则表达式详解")
    print("=" * 80)
    print()
    
    # 完整的正则表达式
    full_pattern = r"^\*Email:\s+[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    # 分解说明
    print("正则表达式分解：")
    print()
    print("  ^                          - 字符串开头")
    print("  \\*                         - 星号（必须转义）")
    print("  Email:                     - 固定文本'Email:'（注意大小写）")
    print("  \\s+                        - 一个或多个空格")
    print("  [a-zA-Z0-9._%+-]+          - 邮箱用户名部分")
    print("                               （字母、数字、点、下划线、百分号、加号、减号）")
    print("  @                          - @符号")
    print("  [a-zA-Z0-9.-]+             - 域名部分")
    print("                               （字母、数字、点、减号）")
    print("  \\.                         - 点（必须转义）")
    print("  [a-zA-Z]{2,}               - 顶级域名（至少2个字母）")
    print("  $                          - 字符串结尾")
    print()
    
    print("=" * 80)


def test_email_validation():
    """测试各种邮箱格式"""
    
    print()
    print("=" * 80)
    print("邮箱地址验证测试")
    print("=" * 80)
    print()
    
    # 邮箱部分的正则表达式
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    
    email_tests = [
        # 有效邮箱
        ("author@mail.cn", True, "标准格式"),
        ("john.doe@example.com", True, "包含点"),
        ("user_123@test.org", True, "包含下划线和数字"),
        ("user+tag@domain.co.uk", True, "包含加号和多级域名"),
        ("first.last@sub.domain.edu.cn", True, "多级子域名"),
        
        # 无效邮箱
        ("authormail.cn", False, "缺少@符号"),
        ("author@mail", False, "缺少顶级域名"),
        ("@mail.cn", False, "缺少用户名"),
        ("author@", False, "缺少域名"),
        ("author @mail.cn", False, "用户名包含空格"),
        ("author@mail .cn", False, "域名包含空格"),
    ]
    
    print("📧 邮箱地址验证：")
    print()
    
    for email, expected, desc in email_tests:
        match = re.match(f"^{email_pattern}$", email) is not None
        result = "✅" if match == expected else "❌"
        status = "有效" if match else "无效"
        
        print(f"   {result} {email:35} {status:6} - {desc}")
    
    print()
    print("=" * 80)


def test_complete_format():
    """测试完整格式的各个组成部分"""
    
    print()
    print("=" * 80)
    print("完整格式组成部分测试")
    print("=" * 80)
    print()
    
    print("格式要求：*Email: author@mail.cn")
    print()
    
    components = [
        {
            "name": "1. 星号（*）",
            "pattern": r"^\*",
            "tests": [
                ("*Email: author@mail.cn", True),
                ("Email: author@mail.cn", False),
            ]
        },
        {
            "name": "2. Email（注意大小写）",
            "pattern": r"^\*Email",
            "tests": [
                ("*Email: author@mail.cn", True),
                ("*email: author@mail.cn", False),
                ("*EMAIL: author@mail.cn", False),
            ]
        },
        {
            "name": "3. 冒号（:）",
            "pattern": r"^\*Email:",
            "tests": [
                ("*Email: author@mail.cn", True),
                ("*Email author@mail.cn", False),
            ]
        },
        {
            "name": "4. 冒号后的空格",
            "pattern": r"^\*Email:\s+",
            "tests": [
                ("*Email: author@mail.cn", True),
                ("*Email:  author@mail.cn", True),  # 多个空格也可以
                ("*Email:author@mail.cn", False),
            ]
        },
        {
            "name": "5. 有效的邮箱地址",
            "pattern": r"^\*Email:\s+[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "tests": [
                ("*Email: author@mail.cn", True),
                ("*Email: john.doe@example.com", True),
                ("*Email: invalid-email", False),
            ]
        },
        {
            "name": "6. 字符串结尾（不能有多余内容）",
            "pattern": r"^\*Email:\s+[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "tests": [
                ("*Email: author@mail.cn", True),
                ("*Email: author@mail.cn (note)", False),
            ]
        },
    ]
    
    for component in components:
        print(f"🔍 {component['name']}")
        print(f"   正则: {component['pattern']}")
        print()
        
        for text, expected in component['tests']:
            match = re.match(component['pattern'], text) is not None
            result = "✅" if match == expected else "❌"
            status = "匹配" if match else "不匹配"
            
            print(f"      {result} {text:40} {status}")
        
        print()
    
    print("=" * 80)


def main():
    """主函数"""
    test_corresponding_author_en_format()
    test_email_pattern_details()
    test_email_validation()
    test_complete_format()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 样式配置（styles.yaml）：")
    print("   .corresponding-author-en:")
    print("     font:")
    print("       name_ascii: Times New Roman")
    print("       size: 五号")
    print("     paragraph:")
    print("       alignment: 居中")
    print()
    print("2. 内容规则（rules.yaml）：")
    print("   - r-014: 英文通讯作者格式检查")
    print()
    print("3. 正则表达式：")
    print("   ^\\*Email:\\s+[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
    print()
    print("4. 格式要点：")
    print("   - 必须以星号（*）开头")
    print("   - 固定文本'Email'（注意大小写）")
    print("   - Email后跟冒号（:）")
    print("   - 冒号后至少一个空格")
    print("   - 有效的邮箱地址格式：用户名@域名.后缀")
    print("   - 不能包含多余内容")
    print()
    print("5. 标准格式示例：")
    print("   *Email: author@mail.cn")
    print("   *Email: john.doe@example.com")
    print("   *Email: researcher@university.edu.cn")
    print()


if __name__ == "__main__":
    main()
