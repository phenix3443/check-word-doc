#!/usr/bin/env python3
"""
数据库名称与论文标题一致性测试

测试规则：
数据信息表中的"数据库（集）名称"必须与论文标题一致
"""

def test_title_match_logic():
    """测试标题匹配逻辑"""
    
    print("=" * 80)
    print("数据库名称与论文标题一致性测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标题完全一致（正确）",
            "title": "区块链智能合约数据库",
            "table_name": "区块链智能合约数据库",
            "expected": True
        },
        {
            "name": "场景2：标题不一致（错误）",
            "title": "区块链智能合约数据库",
            "table_name": "智能合约数据库",
            "expected": False
        },
        {
            "name": "场景3：大小写不同（错误）",
            "title": "Blockchain Database",
            "table_name": "blockchain database",
            "expected": False
        },
        {
            "name": "场景4：包含多余空格（错误）",
            "title": "区块链智能合约数据库",
            "table_name": "区块链 智能合约 数据库",
            "expected": False
        },
        {
            "name": "场景5：前后有空格（需要trim后比较）",
            "title": "区块链智能合约数据库",
            "table_name": " 区块链智能合约数据库 ",
            "expected": True  # 如果实现了trim
        },
        {
            "name": "场景6：标题为空（错误）",
            "title": "",
            "table_name": "区块链智能合约数据库",
            "expected": False
        },
        {
            "name": "场景7：表格名称为空（错误）",
            "title": "区块链智能合约数据库",
            "table_name": "",
            "expected": False
        },
    ]
    
    print("📋 测试用例：")
    print()
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        title = test_case['title']
        table_name = test_case['table_name']
        expected = test_case['expected']
        
        # 检查是否匹配（精确匹配，可选trim）
        # 实际实现中可能需要trim
        match = title.strip() == table_name.strip()
        
        # 判断结果
        is_correct = (match == expected)
        result = "✅" if is_correct else "❌"
        status = "通过" if is_correct else "失败"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"{result} {test_case['name']}")
        print(f"   论文标题: '{title}'")
        print(f"   表格名称: '{table_name}'")
        print(f"   预期: {'一致' if expected else '不一致'}, 实际: {'一致' if match else '不一致'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)


def test_cross_validation_concept():
    """测试跨元素验证概念"""
    
    print()
    print("=" * 80)
    print("跨元素验证概念（Key-Value查找）")
    print("=" * 80)
    print()
    
    print("📊 验证流程：")
    print()
    print("   1. 获取论文标题（.title）")
    print("      例如：'区块链智能合约数据库'")
    print("      ↓")
    print("   2. 获取数据信息表（.data-info-table）")
    print("      ↓")
    print("   3. 在表格中查找 key = '数据库（集）名称' 的行")
    print("      遍历第一列，查找匹配的key")
    print("      ↓")
    print("   4. 获取该行第二列的 value")
    print("      例如：'区块链智能合约数据库'")
    print("      ↓")
    print("   5. 比较 value 与论文标题是否完全一致")
    print("      ↓")
    print("   6. 如果不一致，报告错误")
    print()
    
    print("💡 示例：")
    print()
    print("   论文标题: '区块链智能合约数据库'")
    print()
    print("   表格内容:")
    print("   | 数据库（集）名称 | 区块链智能合约数据库 | ← 匹配！✅")
    print("   | 所属学科        | 计算机科学          |")
    print()
    
    print("=" * 80)


def test_table_structure():
    """测试表格结构理解"""
    
    print()
    print("=" * 80)
    print("表格结构理解（Key-Value模式）")
    print("=" * 80)
    print()
    
    print("📊 数据库（集）基本信息简介表结构：")
    print()
    print("   表 1： 数据库（集）基本信息简介")
    print("   " + "-" * 70)
    print("   | Key (第一列)            | Value (第二列)                      |")
    print("   " + "-" * 70)
    print("   | 数据库（集）名称        | 区块链智能合约数据库 ← 必须与标题一致  |")
    print("   | 所属学科               | 计算机科学                          |")
    print("   | 研究主题               | 区块链技术                          |")
    print("   | 数据时间范围            | 2020-2023                          |")
    print("   | ...                    | ...                                |")
    print("   " + "-" * 70)
    print()
    
    print("⚠️  关键点：")
    print("   - 表格是 Key-Value 结构")
    print("   - 第一列（column 0）：Key（项目名称）")
    print("   - 第二列（column 1）：Value（项目值）")
    print()
    
    print("💡 验证逻辑：")
    print("   1. 在第一列中查找 key = '数据库（集）名称'")
    print("   2. 获取该行第二列的 value")
    print("   3. 将该 value 与论文标题比较")
    print()
    
    print("📋 配置参数：")
    print("   - target_key_column: 0        # Key列（第一列）")
    print("   - target_value_column: 1      # Value列（第二列）")
    print("   - target_key: '数据库（集）名称'  # 要查找的key")
    print()
    
    print("=" * 80)


def test_rule_configuration():
    """测试规则配置"""
    
    print()
    print("=" * 80)
    print("规则配置说明（Key-Value查找模式）")
    print("=" * 80)
    print()
    
    print("📋 规则配置（rules.yaml）：")
    print()
    print("   - id: r-042")
    print("     name: 数据库名称与论文标题一致性")
    print("     selector: '.data-info-table'")
    print("     check:")
    print("       cross_validate:")
    print("         source_selector: '.title'")
    print("         target_key_column: 0          # Key列（第一列）")
    print("         target_value_column: 1        # Value列（第二列）")
    print("         target_key: '数据库（集）名称'  # 要查找的key")
    print("         match_type: 'exact'           # 精确匹配")
    print("     severity: error")
    print()
    
    print("🔍 参数说明：")
    print("   - source_selector: 源数据选择器（论文标题）")
    print("   - target_key_column: Key列索引（第一列）")
    print("   - target_value_column: Value列索引（第二列）")
    print("   - target_key: 要查找的key值")
    print("   - match_type: 匹配类型（exact/contains/regex）")
    print()
    
    print("💡 工作流程：")
    print("   1. 遍历表格的每一行")
    print("   2. 检查第一列（key列）是否等于 '数据库（集）名称'")
    print("   3. 如果找到，获取该行第二列（value列）的值")
    print("   4. 将该值与论文标题比较")
    print()
    
    print("=" * 80)


def test_implementation_approaches():
    """测试实现方案"""
    
    print()
    print("=" * 80)
    print("实现方案")
    print("=" * 80)
    print()
    
    print("方案 A：扩展 RuleChecker 支持 cross_validate")
    print()
    print("   优点：")
    print("   - 通用性强，可用于其他跨元素验证")
    print("   - 配置清晰，易于理解")
    print()
    print("   缺点：")
    print("   - 需要扩展 RuleChecker 类")
    print("   - 需要处理表格单元格提取逻辑")
    print()
    
    print("方案 B：使用自定义验证函数")
    print()
    print("   优点：")
    print("   - 灵活性高，可以处理复杂逻辑")
    print("   - 不需要修改 RuleChecker 核心")
    print()
    print("   缺点：")
    print("   - 需要在代码中硬编码验证逻辑")
    print("   - 配置文件无法完全描述规则")
    print()
    
    print("方案 C：使用 Selector 提取 + 条件规则")
    print()
    print("   优点：")
    print("   - 利用现有的 Selector 系统")
    print("   - 可以通过配置实现")
    print()
    print("   缺点：")
    print("   - 需要 Selector 支持表格单元格选择")
    print("   - 语法可能较复杂")
    print()
    
    print("💡 推荐方案：")
    print("   方案 A - 扩展 RuleChecker 支持 cross_validate")
    print("   这是最通用和可维护的方案")
    print()
    
    print("=" * 80)


def test_edge_cases():
    """测试边界情况"""
    
    print()
    print("=" * 80)
    print("边界情况测试")
    print("=" * 80)
    print()
    
    edge_cases = [
        {
            "情况": "论文标题不存在",
            "处理": "报告错误：无法找到论文标题"
        },
        {
            "情况": "数据信息表不存在",
            "处理": "由 r-041 规则处理"
        },
        {
            "情况": "表格为空",
            "处理": "报告错误：表格没有数据行"
        },
        {
            "情况": "表格第一行缺少第二列",
            "处理": "报告错误：表格结构不完整"
        },
        {
            "情况": "标题或表格名称包含特殊字符",
            "处理": "精确匹配，包括特殊字符"
        },
        {
            "情况": "标题或表格名称前后有空格",
            "处理": "建议trim后再比较"
        },
    ]
    
    print("⚠️  边界情况：")
    print()
    
    for i, case in enumerate(edge_cases, 1):
        print(f"{i}. {case['情况']}")
        print(f"   处理方式: {case['处理']}")
        print()
    
    print("=" * 80)


def main():
    """主函数"""
    test_title_match_logic()
    test_cross_validation_concept()
    test_table_structure()
    test_rule_configuration()
    test_implementation_approaches()
    test_edge_cases()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 规则配置（rules.yaml）：")
    print("   - r-042: 数据库名称与论文标题一致性")
    print()
    print("2. 验证逻辑：")
    print("   - 获取论文标题（.title）")
    print("   - 获取数据信息表第一行第二列的值")
    print("   - 精确匹配比较（建议trim）")
    print()
    print("3. 实现方案：")
    print("   - 推荐：扩展 RuleChecker 支持 cross_validate")
    print("   - 配置参数：source_selector, target_column, target_row, match_type")
    print()
    print("4. 注意事项：")
    print("   - 表格列索引：第二列是 column 1（项目值）")
    print("   - 表格行索引：第一行数据是 row 0（不包括表头）")
    print("   - 匹配前建议trim去除前后空格")
    print("   - 需要处理边界情况（元素不存在、表格为空等）")
    print()
    print("5. 错误消息示例：")
    print("   ❌ 数据信息表中的'数据库（集）名称'必须与论文标题一致")
    print("      论文标题: '区块链智能合约数据库'")
    print("      表格名称: '智能合约数据库'")
    print()


if __name__ == "__main__":
    main()
