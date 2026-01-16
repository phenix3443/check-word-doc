#!/usr/bin/env python3
"""
RuleChecker 测试

测试 RuleChecker 的跨元素数量比较功能
"""

import sys
sys.path.insert(0, '/Users/lsl/github/phenix3443/check-word-doc')

from script.core.model import Block, ParagraphBlock
from script.core.rule_checker import RuleChecker


def create_test_blocks():
    """创建测试用的文档块"""
    blocks = []
    
    # 创建模拟的 Paragraph 对象
    class MockParagraph:
        def __init__(self, text):
            self.text = text
    
    # 1. 作者列表（2个作者）
    author_list = ParagraphBlock(
        index=0,
        paragraph=MockParagraph('王嘉平1*，汪浩2')
    )
    author_list.classes = ['author-list']
    blocks.append(author_list)
    
    # 2. 第一个作者单位
    affiliation1 = ParagraphBlock(
        index=1,
        paragraph=MockParagraph('1. 北京大学计算机学院，北京  100871')
    )
    affiliation1.classes = ['author-affiliation']
    blocks.append(affiliation1)
    
    # 3. 第二个作者单位
    affiliation2 = ParagraphBlock(
        index=2,
        paragraph=MockParagraph('2. 清华大学软件学院，北京  100084')
    )
    affiliation2.classes = ['author-affiliation']
    blocks.append(affiliation2)
    
    return blocks


def test_count_equals():
    """测试 count_equals 功能"""
    
    print("=" * 80)
    print("RuleChecker - count_equals 功能测试")
    print("=" * 80)
    print()
    
    # 测试场景1：数量匹配（应该通过）
    print("📝 场景1：2个作者，2个单位（应该通过）")
    print()
    
    blocks = create_test_blocks()
    
    rule = {
        'id': 'r-008',
        'name': '作者单位数量检查',
        'selector': '.author-affiliation',
        'check': {
            'count_equals': {
                'selector': '.author-list',
                'extract': r'\d+',
                'method': 'max'
            }
        },
        'severity': 'error',
        'message': '作者单位数量与作者编号数量不一致'
    }
    
    checker = RuleChecker([rule], blocks)
    issues = checker.check()
    
    print(f"作者列表: {blocks[0].paragraph.text}")
    print(f"单位1: {blocks[1].paragraph.text}")
    print(f"单位2: {blocks[2].paragraph.text}")
    print()
    print(f"检查结果: {len(issues)} 个问题")
    
    if len(issues) == 0:
        print("✅ 测试通过：数量匹配，没有问题")
    else:
        print("❌ 测试失败：不应该有问题")
        for issue in issues:
            print(f"   - {issue.message}")
            if issue.evidence:
                print(f"     期望: {issue.evidence.get('expected', 'N/A')}")
                print(f"     实际: {issue.evidence.get('actual', 'N/A')}")
    
    print()
    print("-" * 80)
    print()
    
    # 测试场景2：数量不匹配（应该失败）
    print("📝 场景2：2个作者，但只有1个单位（应该失败）")
    print()
    
    # 只保留一个单位
    blocks_mismatch = blocks[:2]  # 只有作者列表和第一个单位
    
    checker = RuleChecker([rule], blocks_mismatch)
    issues = checker.check()
    
    print(f"作者列表: {blocks_mismatch[0].paragraph.text}")
    print(f"单位1: {blocks_mismatch[1].paragraph.text}")
    print()
    print(f"检查结果: {len(issues)} 个问题")
    
    if len(issues) > 0:
        print("✅ 测试通过：检测到数量不匹配")
        for issue in issues:
            print(f"   - {issue.message}")
            if issue.evidence:
                print(f"     期望: {issue.evidence.get('expected', 'N/A')}")
                print(f"     实际: {issue.evidence.get('actual', 'N/A')}")
    else:
        print("❌ 测试失败：应该检测到问题")
    
    print()
    print("-" * 80)
    print()
    
    # 测试场景3：3个作者，3个单位（应该通过）
    print("📝 场景3：3个作者，3个单位（应该通过）")
    print()
    
    # 创建模拟的 Paragraph 对象
    class MockParagraph:
        def __init__(self, text):
            self.text = text
    
    # 创建3个作者的场景
    blocks_three = []
    
    author_list_three = ParagraphBlock(
        index=0,
        paragraph=MockParagraph('张三1*，李四2，王五3')
    )
    author_list_three.classes = ['author-list']
    blocks_three.append(author_list_three)
    
    for i in range(1, 4):
        affiliation = ParagraphBlock(
            index=i,
            paragraph=MockParagraph(f'{i}. 单位{i}，北京  100871')
        )
        affiliation.classes = ['author-affiliation']
        blocks_three.append(affiliation)
    
    checker = RuleChecker([rule], blocks_three)
    issues = checker.check()
    
    print(f"作者列表: {blocks_three[0].paragraph.text}")
    for i in range(1, 4):
        print(f"单位{i}: {blocks_three[i].paragraph.text}")
    print()
    print(f"检查结果: {len(issues)} 个问题")
    
    if len(issues) == 0:
        print("✅ 测试通过：数量匹配，没有问题")
    else:
        print("❌ 测试失败：不应该有问题")
        for issue in issues:
            print(f"   - {issue.message}")
    
    print()
    print("=" * 80)


def test_configuration():
    """测试配置加载"""
    
    print()
    print("=" * 80)
    print("配置验证")
    print("=" * 80)
    print()
    
    print("推荐的规则配置：")
    print()
    print("```yaml")
    print("# r-008: 作者单位数量检查（使用跨元素数量比较）")
    print("- id: r-008")
    print("  name: 作者单位数量检查")
    print("  description: 作者单位数量必须与作者列表中的最大编号一致")
    print("  selector: \".author-affiliation\"")
    print("  check:")
    print("    count_equals:")
    print("      selector: \".author-list\"")
    print("      extract: \"\\\\d+\"      # 提取所有数字编号")
    print("      method: \"max\"        # 取最大值作为期望的单位数量")
    print("  severity: error")
    print("  message: \"作者单位数量与作者编号数量不一致\"")
    print("```")
    print()
    
    print("=" * 80)
    print()
    
    print("优势：")
    print("1. ✅ 自动适应任意数量的作者")
    print("2. ✅ 通过提取最大编号来确定期望的单位数量")
    print("3. ✅ 只需一条规则，简洁明了")
    print("4. ✅ 使用 Selector 系统，功能强大")
    print()
    
    print("工作原理：")
    print("1. 从作者列表中提取所有数字（如：1, 2 from '王嘉平1*，汪浩2'）")
    print("2. 取最大值作为期望的单位数量（max(1, 2) = 2）")
    print("3. 统计实际的作者单位数量")
    print("4. 比较两者是否相等")
    print()


def main():
    """主函数"""
    test_count_equals()
    test_configuration()
    
    print("🎉 所有测试完成！")
    print()


if __name__ == "__main__":
    main()
