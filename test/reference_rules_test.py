#!/usr/bin/env python3
"""
参考文献规则测试

测试参考文献的格式规则：
- r-024: 参考文献格式（[数字]  内容，序号后空2格）
- r-025: 第一条参考文献编号（必须是[1]）
- r-026: 参考文献编号连续性（第二条必须是[2]）
"""

import re

def test_reference_format_rule():
    """测试 r-024: 参考文献格式"""
    
    print("=" * 80)
    print("r-024: 参考文献格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标准格式（正确）",
            "text": "[1]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020, 43(5): 123-145.",
            "expected": True
        },
        {
            "name": "场景2：标准格式（正确）",
            "text": "[2]  Smith J. Blockchain Technology[J]. Computer Science, 2020.",
            "expected": True
        },
        {
            "name": "场景3：多位数编号（正确）",
            "text": "[10]  王五. 智能合约安全分析[M]. 北京: 科学出版社, 2021.",
            "expected": True
        },
        {
            "name": "场景4：只有1个空格（错误）",
            "text": "[1] 张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景5：3个空格（错误）",
            "text": "[1]   张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景6：缺少空格（错误）",
            "text": "[1]张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景7：缺少方括号（错误）",
            "text": "1  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景8：使用圆括号（错误）",
            "text": "(1)  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
    ]
    
    # r-024 正则表达式
    pattern = r"^\[\d+\]  [^ ].*$"
    
    print("📋 r-024 格式测试用例：")
    print()
    print(f"正则表达式: {pattern}")
    print("说明: [数字] + 恰好2个空格 + 非空格字符 + 内容")
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
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {test_case['name']}")
        print(f"   文本: '{text}'")
        print(f"   预期: {'匹配' if expected else '不匹配'}, 实际: {'匹配' if match else '不匹配'}")
        print()
    
    print("=" * 80)
    print(f"r-024 测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)


def test_first_reference_rule():
    """测试 r-025: 第一条参考文献编号"""
    
    print()
    print("=" * 80)
    print("r-025: 第一条参考文献编号测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：正确的第一条（正确）",
            "text": "[1]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": True
        },
        {
            "name": "场景2：从[2]开始（错误）",
            "text": "[2]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景3：从[0]开始（错误）",
            "text": "[0]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
    ]
    
    # r-025 正则表达式
    pattern = r"^\[1\]  "
    
    print("📋 r-025 第一条编号测试用例：")
    print()
    print(f"正则表达式: {pattern}")
    print("说明: 必须以 '[1]  ' 开头（2个空格）")
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
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {test_case['name']}")
        print(f"   文本: '{text}'")
        print(f"   预期: {'匹配' if expected else '不匹配'}, 实际: {'匹配' if match else '不匹配'}")
        print()
    
    print("=" * 80)
    print(f"r-025 测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)


def test_second_reference_rule():
    """测试 r-026: 参考文献编号连续性"""
    
    print()
    print("=" * 80)
    print("r-026: 参考文献编号连续性测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：正确的第二条（正确）",
            "text": "[2]  Smith J. Blockchain Technology[J]. Computer Science, 2020.",
            "expected": True
        },
        {
            "name": "场景2：跳号到[3]（错误）",
            "text": "[3]  Smith J. Blockchain Technology[J]. Computer Science, 2020.",
            "expected": False
        },
        {
            "name": "场景3：重复[1]（错误）",
            "text": "[1]  Smith J. Blockchain Technology[J]. Computer Science, 2020.",
            "expected": False
        },
    ]
    
    # r-026 正则表达式
    pattern = r"^\[2\]  "
    
    print("📋 r-026 编号连续性测试用例：")
    print()
    print(f"正则表达式: {pattern}")
    print("说明: 第二条必须以 '[2]  ' 开头（2个空格）")
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
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {test_case['name']}")
        print(f"   文本: '{text}'")
        print(f"   预期: {'匹配' if expected else '不匹配'}, 实际: {'匹配' if match else '不匹配'}")
        print()
    
    print("=" * 80)
    print(f"r-026 测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)


def test_reference_examples():
    """测试参考文献示例"""
    
    print()
    print("=" * 80)
    print("参考文献示例")
    print("=" * 80)
    print()
    
    examples = [
        "[1]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020, 43(5): 123-145.",
        "[2]  王五. 数据库系统概论[M]. 第5版. 北京: 高等教育出版社, 2019.",
        "[3]  Chen L. Smart Contract Security[C]//Proceedings of IEEE, 2021: 100-110.",
        "[4]  赵六. 智能合约形式化验证研究[D]. 北京: 清华大学, 2021.",
        "[5]  Ethereum Foundation. Ethereum White Paper[EB/OL]. https://ethereum.org, 2021-05-20.",
    ]
    
    print("📊 正确示例：")
    print()
    
    for example in examples:
        print(f"   ✅ {example}")
    
    print()
    print("=" * 80)


def test_format_requirements():
    """测试格式要求"""
    
    print()
    print("=" * 80)
    print("格式要求总结")
    print("=" * 80)
    print()
    
    print("📋 参考文献格式要求：")
    print()
    print("1. 编号格式：[1]、[2]、[3]……")
    print("   ✅ 正确: [1]、[2]、[3]")
    print("   ❌ 错误: (1)、1.、1)")
    print()
    
    print("2. 序号后空2格")
    print("   ✅ 正确: [1]  文献内容（2个空格）")
    print("   ❌ 错误: [1] 文献内容（1个空格）")
    print("   ❌ 错误: [1]   文献内容（3个空格）")
    print()
    
    print("3. 顶格排（左对齐，无缩进）")
    print("   ✅ 正确: 从行首开始")
    print("   ❌ 错误: 有首行缩进")
    print()
    
    print("4. 编号连续")
    print("   ✅ 正确: [1]、[2]、[3]、[4]……")
    print("   ❌ 错误: [1]、[3]、[5]（跳号）")
    print()
    
    print("5. 从[1]开始")
    print("   ✅ 正确: 第一条是 [1]")
    print("   ❌ 错误: 第一条是 [0] 或 [2]")
    print()
    
    print("=" * 80)


def main():
    """主函数"""
    test_reference_format_rule()
    test_first_reference_rule()
    test_second_reference_rule()
    test_reference_examples()
    test_format_requirements()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 规则总结：")
    print()
    print("r-024: 参考文献格式")
    print("   - 格式: [数字]  内容")
    print("   - 正则: ^\\[\\d+\\]  [^ ].*$")
    print("   - 要求: 序号后恰好2个空格")
    print()
    print("r-025: 第一条参考文献编号")
    print("   - 格式: [1]  内容")
    print("   - 正则: ^\\[1\\]  ")
    print("   - 要求: 第一条必须从[1]开始")
    print()
    print("r-026: 参考文献编号连续性")
    print("   - 格式: [2]  内容")
    print("   - 正则: ^\\[2\\]  ")
    print("   - 要求: 第二条必须是[2]，编号连续")
    print()
    print("正确示例:")
    print("   [1]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020, 43(5): 123-145.")
    print("   [2]  Smith J. Blockchain Technology[J]. Computer Science, 2020.")
    print()


if __name__ == "__main__":
    main()
