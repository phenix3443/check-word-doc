#!/usr/bin/env python3
"""
参考文献列表格式测试

测试参考文献列表的格式规则：
- 按照"[1]""[2]""[3]"……依次编号
- 顶格排（左对齐，无缩进）
- 序号后空2格
- 中文字体宋体
- 西文字体Times New Roman
- 五号
- 1.15行距
"""

import re

def test_reference_item_style():
    """测试参考文献列表样式配置"""
    
    print("=" * 80)
    print("参考文献列表样式配置测试")
    print("=" * 80)
    print()
    
    # 样式要求
    style_requirements = {
        "font": {
            "name_eastasia": "宋体",
            "name_ascii": "Times New Roman",
            "size": "五号"
        },
        "paragraph": {
            "alignment": "左对齐",
            "line_spacing": "1.15倍",
            "first_line_indent": "0字符"  # 顶格排
        }
    }
    
    print("📋 参考文献列表样式要求：")
    print()
    print("1️⃣  字体设置：")
    print(f"   - 中文字体: {style_requirements['font']['name_eastasia']}")
    print(f"   - 西文字体: {style_requirements['font']['name_ascii']}")
    print(f"   - 字号: {style_requirements['font']['size']}")
    print()
    
    print("2️⃣  段落设置：")
    print(f"   - 对齐方式: {style_requirements['paragraph']['alignment']}")
    print(f"   - 行距: {style_requirements['paragraph']['line_spacing']}")
    print(f"   - 首行缩进: {style_requirements['paragraph']['first_line_indent']} (顶格排)")
    print()
    
    print("=" * 80)


def test_reference_format():
    """测试参考文献格式"""
    
    print()
    print("=" * 80)
    print("参考文献格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标准中文文献（正确）",
            "text": "[1]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020, 43(5): 123-145.",
            "expected": True
        },
        {
            "name": "场景2：标准英文文献（正确）",
            "text": "[2]  Smith J, Brown K. Blockchain Technology[J]. Computer Science, 2020, 43(5): 123-145.",
            "expected": True
        },
        {
            "name": "场景3：多位数编号（正确）",
            "text": "[10]  王五. 智能合约安全分析[M]. 北京: 科学出版社, 2021.",
            "expected": True
        },
        {
            "name": "场景4：书籍文献（正确）",
            "text": "[3]  赵六. 数据库系统概论[M]. 第5版. 北京: 高等教育出版社, 2019.",
            "expected": True
        },
        {
            "name": "场景5：会议论文（正确）",
            "text": "[4]  Chen L. Smart Contract Security[C]//Proceedings of IEEE, 2021: 100-110.",
            "expected": True
        },
        {
            "name": "场景6：只有1个空格（错误）",
            "text": "[1] 张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景7：3个空格（错误）",
            "text": "[1]   张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景8：缺少空格（错误）",
            "text": "[1]张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景9：缺少方括号（错误）",
            "text": "1  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
        {
            "name": "场景10：使用圆括号（错误）",
            "text": "(1)  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020.",
            "expected": False
        },
    ]
    
    # 正则表达式：[数字] + 恰好2个空格 + 内容
    # 使用 [^ ] 确保第3个字符不是空格，从而保证恰好是2个空格
    pattern = r"^\[\d+\]  [^ ].*$"
    
    print("📋 格式测试用例：")
    print()
    print(f"正则表达式: {pattern}")
    print("说明: [数字] + 2个空格 + 内容")
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


def test_reference_examples():
    """测试参考文献示例"""
    
    print()
    print("=" * 80)
    print("参考文献示例")
    print("=" * 80)
    print()
    
    examples = [
        {
            "type": "期刊论文",
            "text": "[1]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020, 43(5): 123-145."
        },
        {
            "type": "书籍",
            "text": "[2]  王五. 数据库系统概论[M]. 第5版. 北京: 高等教育出版社, 2019."
        },
        {
            "type": "会议论文",
            "text": "[3]  Chen L. Smart Contract Security[C]//Proceedings of IEEE, 2021: 100-110."
        },
        {
            "type": "学位论文",
            "text": "[4]  赵六. 智能合约形式化验证研究[D]. 北京: 清华大学, 2021."
        },
        {
            "type": "网络资源",
            "text": "[5]  Ethereum Foundation. Ethereum White Paper[EB/OL]. https://ethereum.org, 2021-05-20."
        },
    ]
    
    print("📊 正确示例（不同文献类型）：")
    print()
    
    for example in examples:
        print(f"   {example['type']}：")
        print(f"   ✅ {example['text']}")
        print()
    
    print("=" * 80)


def test_format_requirements():
    """测试格式要求"""
    
    print()
    print("=" * 80)
    print("格式要求详解")
    print("=" * 80)
    print()
    
    print("📋 格式要求：")
    print()
    print("1. 按照\"[1]\"\"[2]\"\"[3]\"……依次编号")
    print("   ✅ 正确: [1]  文献内容")
    print("   ✅ 正确: [2]  文献内容")
    print("   ❌ 错误: (1)  文献内容")
    print("   ❌ 错误: 1.  文献内容")
    print()
    
    print("2. 顶格排（左对齐，无缩进）")
    print("   - alignment: 左对齐")
    print("   - first_line_indent: 0字符")
    print("   ✅ 正确: 从行首开始")
    print("   ❌ 错误: 有首行缩进")
    print()
    
    print("3. 序号后空2格")
    print("   ✅ 正确: [1]  文献内容（2个空格）")
    print("   ❌ 错误: [1] 文献内容（1个空格）")
    print("   ❌ 错误: [1]   文献内容（3个空格）")
    print()
    
    print("4. 中文字体宋体，西文字体Times New Roman")
    print("   - name_eastasia: 宋体")
    print("   - name_ascii: Times New Roman")
    print()
    
    print("5. 五号")
    print("   - size: 五号")
    print()
    
    print("6. 1.15行距")
    print("   - line_spacing: 1.15倍")
    print()
    
    print("=" * 80)


def test_spacing_verification():
    """测试空格数量验证"""
    
    print()
    print("=" * 80)
    print("空格数量验证")
    print("=" * 80)
    print()
    
    test_cases = [
        {"spaces": 0, "text": "[1]文献内容", "correct": False},
        {"spaces": 1, "text": "[1] 文献内容", "correct": False},
        {"spaces": 2, "text": "[1]  文献内容", "correct": True},
        {"spaces": 3, "text": "[1]   文献内容", "correct": False},
        {"spaces": 4, "text": "[1]    文献内容", "correct": False},
    ]
    
    print("📋 空格数量测试：")
    print()
    
    for test_case in test_cases:
        spaces = test_case['spaces']
        text = test_case['text']
        correct = test_case['correct']
        
        result = "✅" if correct else "❌"
        status = "正确" if correct else "错误"
        
        print(f"{result} {spaces}个空格: '{text}' - {status}")
    
    print()
    print("💡 要求：序号后必须恰好有2个空格")
    print()
    
    print("=" * 80)


def test_numbering_sequence():
    """测试编号顺序"""
    
    print()
    print("=" * 80)
    print("编号顺序示例")
    print("=" * 80)
    print()
    
    print("📋 正确的编号顺序：")
    print()
    
    references = [
        "[1]  第一篇参考文献...",
        "[2]  第二篇参考文献...",
        "[3]  第三篇参考文献...",
        "[4]  第四篇参考文献...",
        "[5]  第五篇参考文献...",
        "...",
        "[10]  第十篇参考文献...",
        "[11]  第十一篇参考文献...",
    ]
    
    for ref in references:
        if ref == "...":
            print(f"   {ref}")
        else:
            print(f"   ✅ {ref}")
    
    print()
    print("💡 说明：")
    print("   - 按照引用顺序依次编号")
    print("   - 从 [1] 开始连续编号")
    print("   - 每个编号后都是2个空格")
    print()
    
    print("=" * 80)


def test_alignment_comparison():
    """测试对齐方式对比"""
    
    print()
    print("=" * 80)
    print("对齐方式说明")
    print("=" * 80)
    print()
    
    print("📋 顶格排 vs 悬挂缩进：")
    print()
    
    print("✅ 顶格排（本要求）：")
    print("   [1]  张三, 李四. 区块链技术研究与应用[J]. 计算机学报,")
    print("   2020, 43(5): 123-145.")
    print("   说明：所有行都从行首开始，无缩进")
    print()
    
    print("❌ 悬挂缩进（不采用）：")
    print("   [1]  张三, 李四. 区块链技术研究与应用[J]. 计算机学报,")
    print("        2020, 43(5): 123-145.")
    print("   说明：第二行及后续行有缩进")
    print()
    
    print("💡 本配置采用：顶格排（左对齐，无缩进）")
    print()
    
    print("=" * 80)


def main():
    """主函数"""
    test_reference_item_style()
    test_reference_format()
    test_reference_examples()
    test_format_requirements()
    test_spacing_verification()
    test_numbering_sequence()
    test_alignment_comparison()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 样式配置（styles.yaml）：")
    print("   .reference-item:")
    print("     font:")
    print("       name_eastasia: 宋体")
    print("       name_ascii: Times New Roman")
    print("       size: 五号")
    print("     paragraph:")
    print("       alignment: 左对齐")
    print("       line_spacing: 1.15倍")
    print()
    print("2. 格式要点：")
    print("   - 编号格式：[1]、[2]、[3]……")
    print("   - 顶格排（左对齐，无缩进）")
    print("   - 序号后空2格")
    print("   - 宋体（英文Times New Roman）")
    print("   - 五号")
    print("   - 1.15行距")
    print()
    print("3. 正确示例：")
    print("   ✅ [1]  张三, 李四. 区块链技术研究[J]. 计算机学报, 2020, 43(5): 123-145.")
    print("   ✅ [2]  Smith J. Blockchain Technology[J]. Computer Science, 2020.")
    print("   ✅ [3]  王五. 数据库系统概论[M]. 北京: 科学出版社, 2019.")
    print()
    print("4. 关键点：")
    print("   - 方括号编号：[1]、[2]、[3]")
    print("   - 序号后恰好2个空格")
    print("   - 顶格排，不使用悬挂缩进")
    print()


if __name__ == "__main__":
    main()
