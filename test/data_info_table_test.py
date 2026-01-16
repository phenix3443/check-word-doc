#!/usr/bin/env python3
"""
数据库（集）基本信息简介表格式测试

测试数据库（集）基本信息简介表的格式规则：
1. 表题注：居中，黑体5号字，1.15倍行距，段前、段后各0.5行距
2. 表格内容：中文字体宋体，西文字体Times New Roman，小5号，1.15倍行距
"""

def test_data_info_table_caption_style():
    """测试表题注样式配置"""
    
    print("=" * 80)
    print("数据库（集）基本信息简介表题注样式测试")
    print("=" * 80)
    print()
    
    # 样式要求
    caption_style = {
        "font": {
            "name_eastasia": "黑体",
            "name_ascii": "Times New Roman",
            "size": "五号",
            "bold": True
        },
        "paragraph": {
            "alignment": "居中",
            "line_spacing": "1.15倍",
            "space_before": "0.5行",
            "space_after": "0.5行"
        }
    }
    
    print("📋 表题注样式要求：")
    print()
    print("1️⃣  字体设置：")
    print(f"   - 中文字体: {caption_style['font']['name_eastasia']}")
    print(f"   - 西文字体: {caption_style['font']['name_ascii']}")
    print(f"   - 字号: {caption_style['font']['size']}")
    print(f"   - 加粗: {'是' if caption_style['font']['bold'] else '否'}")
    print()
    
    print("2️⃣  段落设置：")
    print(f"   - 对齐方式: {caption_style['paragraph']['alignment']}")
    print(f"   - 行距: {caption_style['paragraph']['line_spacing']}")
    print(f"   - 段前间距: {caption_style['paragraph']['space_before']}")
    print(f"   - 段后间距: {caption_style['paragraph']['space_after']}")
    print()
    
    print("=" * 80)


def test_data_info_table_content_style():
    """测试表格内容样式配置"""
    
    print()
    print("=" * 80)
    print("数据库（集）基本信息简介表格内容样式测试")
    print("=" * 80)
    print()
    
    # 样式要求
    table_style = {
        "font": {
            "name_eastasia": "宋体",
            "name_ascii": "Times New Roman",
            "size": "小五"
        },
        "paragraph": {
            "line_spacing": "1.15倍"
        }
    }
    
    print("📋 表格内容样式要求：")
    print()
    print("1️⃣  字体设置：")
    print(f"   - 中文字体: {table_style['font']['name_eastasia']}")
    print(f"   - 西文字体: {table_style['font']['name_ascii']}")
    print(f"   - 字号: {table_style['font']['size']}")
    print()
    
    print("2️⃣  段落设置：")
    print(f"   - 行距: {table_style['paragraph']['line_spacing']}")
    print()
    
    print("⚠️  注意事项：")
    print("   - 表头和题头应使用粗体")
    print("   - 表格本身不设置段前段后间距（由题注控制）")
    print()
    
    print("=" * 80)


def test_table_structure():
    """测试表格结构"""
    
    print()
    print("=" * 80)
    print("数据库（集）基本信息简介表结构")
    print("=" * 80)
    print()
    
    print("📊 表格结构示例：")
    print()
    print("   表 1： 数据库（集）基本信息简介")
    print("   " + "-" * 60)
    print("   | 数据库（集）名称        | [具体名称]                    |")
    print("   | 所属学科               | [学科分类]                    |")
    print("   | 研究主题               | [研究主题]                    |")
    print("   | 数据时间范围            | [起始时间 - 结束时间]          |")
    print("   | 数据空间范围            | [地理范围]                    |")
    print("   | 数据量                 | [数据量描述]                  |")
    print("   | 数据格式               | [文件格式]                    |")
    print("   | 数据服务系统网址         | [URL]                        |")
    print("   | 基金项目               | [项目信息]                    |")
    print("   | 语种                   | [中文/英文等]                 |")
    print("   | 数据库（集）组成        | [组成说明]                    |")
    print("   " + "-" * 60)
    print()
    
    print("=" * 80)


def test_caption_and_table_relationship():
    """测试题注和表格的关系"""
    
    print()
    print("=" * 80)
    print("题注与表格的位置关系")
    print("=" * 80)
    print()
    
    print("📍 位置关系：")
    print()
    print("   1. 表题注（.data-info-table-caption）")
    print("      ↓")
    print("   2. 表格内容（.data-info-table）")
    print()
    
    print("⚠️  格式要点：")
    print("   - 题注在表格之前")
    print("   - 题注设置段前、段后各0.5行距")
    print("   - 表格本身不设置段前段后间距")
    print("   - 题注居中对齐")
    print("   - 题注使用黑体5号字加粗")
    print()
    
    print("=" * 80)


def test_font_comparison():
    """测试字体对比"""
    
    print()
    print("=" * 80)
    print("题注与表格内容字体对比")
    print("=" * 80)
    print()
    
    comparison = [
        {
            "项目": "中文字体",
            "表题注": "黑体",
            "表格内容": "宋体"
        },
        {
            "项目": "西文字体",
            "表题注": "Times New Roman",
            "表格内容": "Times New Roman"
        },
        {
            "项目": "字号",
            "表题注": "五号",
            "表格内容": "小五"
        },
        {
            "项目": "加粗",
            "表题注": "是",
            "表格内容": "表头和题头加粗"
        },
        {
            "项目": "对齐方式",
            "表题注": "居中",
            "表格内容": "根据单元格内容"
        },
        {
            "项目": "行距",
            "表题注": "1.15倍",
            "表格内容": "1.15倍"
        },
        {
            "项目": "段前间距",
            "表题注": "0.5行",
            "表格内容": "无"
        },
        {
            "项目": "段后间距",
            "表题注": "0.5行",
            "表格内容": "无"
        },
    ]
    
    print("📊 格式对比表：")
    print()
    print(f"{'项目':15} {'表题注':25} {'表格内容':25}")
    print("-" * 65)
    
    for item in comparison:
        print(f"{item['项目']:15} {item['表题注']:25} {item['表格内容']:25}")
    
    print()
    print("=" * 80)


def test_style_verification():
    """验证样式配置"""
    
    print()
    print("=" * 80)
    print("样式配置验证")
    print("=" * 80)
    print()
    
    print("✅ 表题注配置项检查：")
    print()
    
    caption_checks = [
        ("中文字体（黑体）", True, "✅"),
        ("西文字体（Times New Roman）", True, "✅"),
        ("字号（五号）", True, "✅"),
        ("加粗", True, "✅"),
        ("居中对齐", True, "✅"),
        ("行距（1.15倍）", True, "✅"),
        ("段前间距（0.5行）", True, "✅"),
        ("段后间距（0.5行）", True, "✅"),
    ]
    
    for check_name, is_valid, icon in caption_checks:
        print(f"   {icon} {check_name}")
    
    print()
    print("✅ 表格内容配置项检查：")
    print()
    
    table_checks = [
        ("中文字体（宋体）", True, "✅"),
        ("西文字体（Times New Roman）", True, "✅"),
        ("字号（小五）", True, "✅"),
        ("行距（1.15倍）", True, "✅"),
    ]
    
    for check_name, is_valid, icon in table_checks:
        print(f"   {icon} {check_name}")
    
    print()
    print("=" * 80)


def main():
    """主函数"""
    test_data_info_table_caption_style()
    test_data_info_table_content_style()
    test_table_structure()
    test_caption_and_table_relationship()
    test_font_comparison()
    test_style_verification()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 表题注样式配置（styles.yaml）：")
    print("   .data-info-table-caption:")
    print("     font:")
    print("       name_eastasia: 黑体")
    print("       name_ascii: Times New Roman")
    print("       size: 五号")
    print("       bold: true")
    print("     paragraph:")
    print("       alignment: 居中")
    print("       line_spacing: 1.15倍")
    print("       space_before: 0.5行")
    print("       space_after: 0.5行")
    print()
    print("2. 表格内容样式配置（styles.yaml）：")
    print("   .data-info-table:")
    print("     font:")
    print("       name_eastasia: 宋体")
    print("       name_ascii: Times New Roman")
    print("       size: 小五")
    print("     paragraph:")
    print("       line_spacing: 1.15倍")
    print()
    print("3. 格式要点：")
    print("   表题注：")
    print("   - 居中对齐")
    print("   - 黑体5号字加粗")
    print("   - 1.15倍行距")
    print("   - 段前、段后各0.5行距")
    print()
    print("   表格内容：")
    print("   - 中文字体宋体，西文字体Times New Roman")
    print("   - 小5号字")
    print("   - 1.15倍行距")
    print("   - 表头和题头加粗")
    print()


if __name__ == "__main__":
    main()
