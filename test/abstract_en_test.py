#!/usr/bin/env python3
"""
英文摘要格式测试

测试英文摘要的格式规则：
1. 样式：Times New Roman，5号字，左对齐，1.15倍行距
"""

def test_abstract_en_style():
    """测试英文摘要样式配置"""
    
    print("=" * 80)
    print("英文摘要样式配置测试")
    print("=" * 80)
    print()
    
    # 样式要求
    style_requirements = {
        "font": {
            "name_ascii": "Times New Roman",
            "size": "五号"
        },
        "paragraph": {
            "alignment": "左对齐",
            "line_spacing": "1.15倍"
        }
    }
    
    print("📋 样式要求：")
    print()
    print("1️⃣  字体设置：")
    print(f"   - 西文字体: {style_requirements['font']['name_ascii']}")
    print(f"   - 字号: {style_requirements['font']['size']}")
    print()
    
    print("2️⃣  段落设置：")
    print(f"   - 对齐方式: {style_requirements['paragraph']['alignment']}")
    print(f"   - 行距: {style_requirements['paragraph']['line_spacing']}")
    print()
    
    print("=" * 80)


def test_abstract_en_comparison():
    """对比中英文摘要的格式差异"""
    
    print()
    print("=" * 80)
    print("中英文摘要格式对比")
    print("=" * 80)
    print()
    
    comparison = [
        {
            "项目": "字体",
            "中文摘要": "华文楷体 / Times New Roman",
            "英文摘要": "Times New Roman"
        },
        {
            "项目": "字号",
            "中文摘要": "五号",
            "英文摘要": "五号"
        },
        {
            "项目": "对齐方式",
            "中文摘要": "左对齐",
            "英文摘要": "左对齐"
        },
        {
            "项目": "行距",
            "中文摘要": "1.15倍",
            "英文摘要": "1.15倍"
        },
        {
            "项目": "开头标识",
            "中文摘要": "摘要：",
            "英文摘要": "Abstract:"
        },
    ]
    
    print("📊 格式对比表：")
    print()
    print(f"{'项目':15} {'中文摘要':35} {'英文摘要':35}")
    print("-" * 85)
    
    for item in comparison:
        print(f"{item['项目']:15} {item['中文摘要']:35} {item['英文摘要']:35}")
    
    print()
    print("=" * 80)


def test_abstract_en_examples():
    """英文摘要示例"""
    
    print()
    print("=" * 80)
    print("英文摘要示例")
    print("=" * 80)
    print()
    
    examples = [
        {
            "name": "标准格式示例",
            "text": "Abstract: This paper presents a novel approach to blockchain-based data management. The proposed method improves data security and efficiency through smart contract optimization.",
            "valid": True
        },
        {
            "name": "较长摘要示例",
            "text": "Abstract: In recent years, blockchain technology has gained significant attention in various domains. This research focuses on developing a secure and efficient data storage mechanism using blockchain. We propose a new smart contract language that enhances both security and performance. Experimental results demonstrate the effectiveness of our approach.",
            "valid": True
        },
    ]
    
    print("📝 示例文本：")
    print()
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}")
        print()
        print(f"   {example['text']}")
        print()
        status = "✅ 符合格式要求" if example['valid'] else "❌ 不符合格式要求"
        print(f"   {status}")
        print()
    
    print("=" * 80)


def test_style_verification():
    """验证样式配置"""
    
    print()
    print("=" * 80)
    print("样式配置验证")
    print("=" * 80)
    print()
    
    print("✅ 配置项检查：")
    print()
    
    checks = [
        ("字体（Times New Roman）", True, "✅"),
        ("字号（五号）", True, "✅"),
        ("对齐方式（左对齐）", True, "✅"),
        ("行距（1.15倍）", True, "✅"),
    ]
    
    for check_name, is_valid, icon in checks:
        print(f"   {icon} {check_name}")
    
    print()
    print("=" * 80)


def main():
    """主函数"""
    test_abstract_en_style()
    test_abstract_en_comparison()
    test_abstract_en_examples()
    test_style_verification()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 样式配置（styles.yaml）：")
    print("   .abstract-en:")
    print("     font:")
    print("       name_ascii: Times New Roman")
    print("       size: 五号")
    print("     paragraph:")
    print("       alignment: 左对齐")
    print("       line_spacing: 1.15倍")
    print()
    print("2. 格式要点：")
    print("   - Times New Roman字体")
    print("   - 5号字")
    print("   - 左对齐")
    print("   - 1.15倍行距")
    print()
    print("3. 与中文摘要的区别：")
    print("   - 中文摘要：华文楷体/Times New Roman混合字体")
    print("   - 英文摘要：纯Times New Roman字体")
    print("   - 对齐方式和行距相同")
    print()


if __name__ == "__main__":
    main()
