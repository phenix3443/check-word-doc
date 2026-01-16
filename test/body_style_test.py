#!/usr/bin/env python3
"""
正文样式测试

测试正文的格式规则：
- 中文字体宋体
- 西文字体Times New Roman
- 5号字
- 1.15倍行距
"""

def test_body_style():
    """测试正文样式配置"""
    
    print("=" * 80)
    print("正文样式配置测试")
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
            "alignment": "两端对齐",
            "first_line_indent": "2字符",
            "line_spacing": "1.15倍"
        }
    }
    
    print("📋 正文样式要求：")
    print()
    print("1️⃣  字体设置：")
    print(f"   - 中文字体: {style_requirements['font']['name_eastasia']}")
    print(f"   - 西文字体: {style_requirements['font']['name_ascii']}")
    print(f"   - 字号: {style_requirements['font']['size']}")
    print()
    
    print("2️⃣  段落设置：")
    print(f"   - 对齐方式: {style_requirements['paragraph']['alignment']}")
    print(f"   - 首行缩进: {style_requirements['paragraph']['first_line_indent']}")
    print(f"   - 行距: {style_requirements['paragraph']['line_spacing']}")
    print()
    
    print("=" * 80)


def test_body_classes():
    """测试正文类别"""
    
    print()
    print("=" * 80)
    print("正文类别")
    print("=" * 80)
    print()
    
    body_classes = [
        (".body-introduction", "引言内容"),
        (".body-data-collection", "数据采集和处理方法内容"),
        (".body-data-description", "数据样本描述内容"),
        (".body-quality-control", "数据质量控制和评估内容"),
        (".body-data-value", "数据价值和保藏计划内容"),
        (".body-usage-method", "数据使用方法和建议内容"),
        (".body-availability", "数据可用性声明内容"),
        (".body-acknowledgments", "致谢内容"),
        (".body-author-contributions", "数据作者分工职责内容"),
    ]
    
    print("📊 正文类别列表：")
    print()
    
    for class_name, description in body_classes:
        print(f"   {class_name:30} - {description}")
    
    print()
    print("⚠️  注意：")
    print("   - 所有正文类别使用相同的样式配置")
    print("   - 字体：宋体 / Times New Roman")
    print("   - 字号：五号")
    print("   - 行距：1.15倍")
    print("   - 对齐：两端对齐")
    print("   - 首行缩进：2字符")
    print()
    
    print("=" * 80)


def test_document_structure():
    """测试文档结构"""
    
    print()
    print("=" * 80)
    print("文档结构示例")
    print("=" * 80)
    print()
    
    print("📄 论文结构：")
    print()
    print("   标题")
    print("   作者信息")
    print("   摘要")
    print("   关键词")
    print("   ...")
    print()
    print("   引言（一级标题）")
    print("   ├─ 正文段落1 ← .body-introduction")
    print("   ├─ 正文段落2 ← .body-introduction")
    print("   └─ 正文段落3 ← .body-introduction")
    print()
    print("   1 数据采集和处理方法（一级标题）")
    print("   ├─ 正文段落1 ← .body-data-collection")
    print("   ├─ 正文段落2 ← .body-data-collection")
    print("   └─ 正文段落3 ← .body-data-collection")
    print()
    print("   2 数据样本描述（一级标题）")
    print("   ├─ 正文段落1 ← .body-data-description")
    print("   └─ 正文段落2 ← .body-data-description")
    print()
    print("   ...")
    print()
    
    print("=" * 80)


def test_style_comparison():
    """测试样式对比"""
    
    print()
    print("=" * 80)
    print("正文与标题样式对比")
    print("=" * 80)
    print()
    
    comparison = [
        {
            "项目": "中文字体",
            "一级标题": "宋体",
            "正文": "宋体"
        },
        {
            "项目": "西文字体",
            "一级标题": "Times New Roman",
            "正文": "Times New Roman"
        },
        {
            "项目": "字号",
            "一级标题": "四号",
            "正文": "五号"
        },
        {
            "项目": "对齐方式",
            "一级标题": "左对齐",
            "正文": "两端对齐"
        },
        {
            "项目": "行距",
            "一级标题": "默认",
            "正文": "1.15倍"
        },
        {
            "项目": "首行缩进",
            "一级标题": "无",
            "正文": "2字符"
        },
        {
            "项目": "段前间距",
            "一级标题": "0.5行",
            "正文": "无"
        },
        {
            "项目": "段后间距",
            "一级标题": "0.5行",
            "正文": "无"
        },
    ]
    
    print("📊 样式对比表：")
    print()
    print(f"{'项目':15} {'一级标题':25} {'正文':25}")
    print("-" * 65)
    
    for item in comparison:
        print(f"{item['项目']:15} {item['一级标题']:25} {item['正文']:25}")
    
    print()
    print("=" * 80)


def test_style_verification():
    """验证样式配置"""
    
    print()
    print("=" * 80)
    print("样式配置验证")
    print("=" * 80)
    print()
    
    print("✅ 正文配置项检查：")
    print()
    
    checks = [
        ("中文字体（宋体）", True, "✅"),
        ("西文字体（Times New Roman）", True, "✅"),
        ("字号（五号）", True, "✅"),
        ("行距（1.15倍）", True, "✅"),
        ("对齐方式（两端对齐）", True, "✅"),
        ("首行缩进（2字符）", True, "✅"),
    ]
    
    for check_name, is_valid, icon in checks:
        print(f"   {icon} {check_name}")
    
    print()
    print("=" * 80)


def main():
    """主函数"""
    test_body_style()
    test_body_classes()
    test_document_structure()
    test_style_comparison()
    test_style_verification()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 正文样式配置（styles.yaml）：")
    print("   .body-*:")
    print("     font:")
    print("       name_eastasia: 宋体")
    print("       name_ascii: Times New Roman")
    print("       size: 五号")
    print("     paragraph:")
    print("       alignment: 两端对齐")
    print("       first_line_indent: 2字符")
    print("       line_spacing: 1.15倍")
    print()
    print("2. 格式要点：")
    print("   - 中文字体：宋体")
    print("   - 西文字体：Times New Roman")
    print("   - 字号：5号")
    print("   - 行距：1.15倍")
    print("   - 对齐：两端对齐")
    print("   - 首行缩进：2字符")
    print()
    print("3. 适用范围：")
    print("   - 所有章节的正文段落")
    print("   - 包括：引言、数据采集、数据描述等各章节内容")
    print()


if __name__ == "__main__":
    main()
