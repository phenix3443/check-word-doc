#!/usr/bin/env python3
"""
作者数量与单位数量匹配验证

演示如何通过配置规则来验证作者数量与单位数量的一致性
"""

import re

def extract_author_count(author_list_text):
    """从作者列表中提取作者数量"""
    # 方法1：通过中文逗号分隔
    if '，' in author_list_text:
        authors = author_list_text.split('，')
        return len(authors)
    else:
        # 单个作者
        return 1


def extract_author_numbers(author_list_text):
    """从作者列表中提取所有数字编号"""
    # 提取所有数字（作者后面的编号）
    numbers = re.findall(r'(\d+)[*]?', author_list_text)
    return [int(n) for n in numbers]


def validate_author_affiliation_count(author_list_text, affiliation_texts):
    """验证作者单位数量是否匹配"""
    
    print("=" * 80)
    print("作者数量与单位数量匹配验证")
    print("=" * 80)
    print()
    
    # 提取作者数量
    author_count = extract_author_count(author_list_text)
    print(f"作者列表: {author_list_text}")
    print(f"作者数量: {author_count}")
    print()
    
    # 提取作者编号
    author_numbers = extract_author_numbers(author_list_text)
    print(f"作者编号: {author_numbers}")
    print()
    
    # 检查单位数量
    affiliation_count = len(affiliation_texts)
    print(f"单位数量: {affiliation_count}")
    print()
    
    # 验证数量是否匹配
    if author_count != affiliation_count:
        print(f"❌ 错误：作者数量({author_count})与单位数量({affiliation_count})不匹配")
        return False
    
    # 验证编号的最大值
    if author_numbers:
        max_number = max(author_numbers)
        if max_number != affiliation_count:
            print(f"❌ 错误：最大编号({max_number})与单位数量({affiliation_count})不匹配")
            return False
    
    # 验证单位编号的连续性
    print("单位列表:")
    for i, affiliation in enumerate(affiliation_texts, 1):
        print(f"  {i}. {affiliation}")
        
        # 提取单位编号
        match = re.match(r'^(\d+)\.', affiliation)
        if match:
            unit_number = int(match.group(1))
            if unit_number != i:
                print(f"     ❌ 错误：单位编号({unit_number})与期望编号({i})不匹配")
                return False
        else:
            print(f"     ❌ 错误：单位缺少编号")
            return False
    
    print()
    print("✅ 验证通过：作者数量与单位数量匹配")
    return True


def test_scenarios():
    """测试各种场景"""
    
    print()
    print("=" * 80)
    print("测试场景")
    print("=" * 80)
    print()
    
    scenarios = [
        {
            "name": "场景1：两个作者，两个单位（正确）",
            "author_list": "王嘉平1*，汪浩2",
            "affiliations": [
                "1. 北京大学计算机学院，北京  100871",
                "2. 清华大学软件学院，北京  100084"
            ],
            "expected": True
        },
        {
            "name": "场景2：三个作者，三个单位（正确）",
            "author_list": "张三1*，李四2，王五3",
            "affiliations": [
                "1. 北京大学计算机学院，北京  100871",
                "2. 清华大学软件学院，北京  100084",
                "3. 中国科学院计算技术研究所，北京  100190"
            ],
            "expected": True
        },
        {
            "name": "场景3：两个作者，但只有一个单位（错误）",
            "author_list": "王嘉平1*，汪浩2",
            "affiliations": [
                "1. 北京大学计算机学院，北京  100871"
            ],
            "expected": False
        },
        {
            "name": "场景4：两个作者，但有三个单位（错误）",
            "author_list": "王嘉平1*，汪浩2",
            "affiliations": [
                "1. 北京大学计算机学院，北京  100871",
                "2. 清华大学软件学院，北京  100084",
                "3. 中国科学院计算技术研究所，北京  100190"
            ],
            "expected": False
        },
        {
            "name": "场景5：单位编号不连续（错误）",
            "author_list": "王嘉平1*，汪浩2",
            "affiliations": [
                "1. 北京大学计算机学院，北京  100871",
                "3. 清华大学软件学院，北京  100084"
            ],
            "expected": False
        }
    ]
    
    for scenario in scenarios:
        print(f"📝 {scenario['name']}")
        print()
        result = validate_author_affiliation_count(
            scenario['author_list'],
            scenario['affiliations']
        )
        
        if result == scenario['expected']:
            print(f"✅ 测试通过")
        else:
            print(f"❌ 测试失败：期望 {scenario['expected']}, 实际 {result}")
        
        print()
        print("-" * 80)
        print()


def propose_rule_config():
    """提出规则配置方案"""
    
    print()
    print("=" * 80)
    print("推荐的规则配置方案")
    print("=" * 80)
    print()
    
    print("方案 A：使用条件规则检查特定数量（推荐，可立即实现）")
    print()
    print("```yaml")
    print("# r-013: 两个作者时，必须有两个单位")
    print("- id: r-013")
    print("  name: 两个作者的单位数量检查")
    print("  description: 两个作者时，必须有两个作者单位")
    print("  selector: \".author-affiliation\"")
    print("  condition:")
    print("    # 条件：作者列表包含1个逗号（说明有2个作者）")
    print("    selector: \".author-list\"")
    print("    pattern: \"^[^，]+，[^，]+$\"")
    print("  check:")
    print("    count: \"== 2\"")
    print("  severity: error")
    print("  message: \"两个作者时，必须有两个作者单位\"")
    print()
    print("# r-014: 三个作者时，必须有三个单位")
    print("- id: r-014")
    print("  name: 三个作者的单位数量检查")
    print("  description: 三个作者时，必须有三个作者单位")
    print("  selector: \".author-affiliation\"")
    print("  condition:")
    print("    # 条件：作者列表包含2个逗号（说明有3个作者）")
    print("    selector: \".author-list\"")
    print("    pattern: \"^[^，]+，[^，]+，[^，]+$\"")
    print("  check:")
    print("    count: \"== 3\"")
    print("  severity: error")
    print("  message: \"三个作者时，必须有三个作者单位\"")
    print("```")
    print()
    
    print("方案 B：扩展 RuleChecker 支持跨元素数量比较（需要开发）")
    print()
    print("```yaml")
    print("# r-013: 作者单位数量必须与作者数量一致")
    print("- id: r-013")
    print("  name: 作者单位数量检查")
    print("  description: 作者单位数量必须与作者数量一致")
    print("  selector: \".author-affiliation\"")
    print("  check:")
    print("    count_equals:")
    print("      selector: \".author-list\"")
    print("      extract: \"\\\\d+\"  # 提取所有数字")
    print("      method: \"max\"      # 取最大值")
    print("  severity: error")
    print("  message: \"作者单位数量与作者编号数量不一致\"")
    print("```")
    print()
    
    print("方案 C：使用 Python 脚本进行复杂验证（最灵活）")
    print()
    print("在 RuleChecker 中添加对自定义验证函数的支持：")
    print()
    print("```yaml")
    print("# r-013: 作者单位数量检查（使用自定义函数）")
    print("- id: r-013")
    print("  name: 作者单位数量检查")
    print("  description: 作者单位数量必须与作者数量一致")
    print("  check:")
    print("    custom: \"validate_author_affiliation_count\"")
    print("  severity: error")
    print("  message: \"作者单位数量与作者编号数量不一致\"")
    print("```")
    print()
    
    print("=" * 80)
    print("推荐：方案 A")
    print("=" * 80)
    print()
    print("理由：")
    print("1. ✅ 可以立即实现，无需修改代码")
    print("2. ✅ 使用现有的 Selector 和条件规则系统")
    print("3. ✅ 覆盖常见场景（1-5个作者）")
    print("4. ✅ 清晰易懂，易于维护")
    print()
    print("限制：")
    print("- 需要为每个作者数量编写一条规则")
    print("- 不能动态适应任意数量的作者")
    print()
    print("未来改进：")
    print("- 实现方案 B，支持跨元素数量比较")
    print("- 实现方案 C，支持自定义验证函数")
    print()


def main():
    """主函数"""
    test_scenarios()
    propose_rule_config()


if __name__ == "__main__":
    main()
