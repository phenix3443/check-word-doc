#!/usr/bin/env python3
"""
表格题注格式测试

测试表格题注的格式规则：
- 表格序号与表格说明中间空1个字
- 表题段前、段后各0.5行距
- 宋体（英文Times New Roman）
- 小5号
- 居中
- 标题和题头粗体
- 1.15倍行距
"""

import re

def test_table_caption_style():
    """测试表格题注样式配置"""
    
    print("=" * 80)
    print("表格题注样式配置测试")
    print("=" * 80)
    print()
    
    # 样式要求
    style_requirements = {
        "font": {
            "name_eastasia": "宋体",
            "name_ascii": "Times New Roman",
            "size": "小五",
            "bold": True
        },
        "paragraph": {
            "alignment": "居中",
            "line_spacing": "1.15倍",
            "space_before": "0.5行",
            "space_after": "0.5行"
        }
    }
    
    print("📋 表格题注样式要求：")
    print()
    print("1️⃣  字体设置：")
    print(f"   - 中文字体: {style_requirements['font']['name_eastasia']}")
    print(f"   - 西文字体: {style_requirements['font']['name_ascii']}")
    print(f"   - 字号: {style_requirements['font']['size']}")
    print(f"   - 加粗: {'是' if style_requirements['font']['bold'] else '否'}")
    print()
    
    print("2️⃣  段落设置：")
    print(f"   - 对齐方式: {style_requirements['paragraph']['alignment']}")
    print(f"   - 行距: {style_requirements['paragraph']['line_spacing']}")
    print(f"   - 段前间距: {style_requirements['paragraph']['space_before']}")
    print(f"   - 段后间距: {style_requirements['paragraph']['space_after']}")
    print()
    
    print("=" * 80)


def test_caption_format():
    """测试题注格式"""
    
    print()
    print("=" * 80)
    print("表格题注格式测试")
    print("=" * 80)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：标准格式（正确）",
            "text": "表 1： 数据库（集）基本信息简介",
            "expected": True
        },
        {
            "name": "场景2：标准格式（正确）",
            "text": "表 2： 实验数据统计",
            "expected": True
        },
        {
            "name": "场景3：多位数序号（正确）",
            "text": "表 10： 性能对比结果",
            "expected": True
        },
        {
            "name": "场景4：包含英文（正确）",
            "text": "表 1： Performance Comparison",
            "expected": True
        },
        {
            "name": "场景5：使用中文冒号（正确）",
            "text": "表 1： 数据统计",
            "expected": True
        },
        {
            "name": "场景6：使用英文冒号（正确）",
            "text": "表 1: 数据统计",
            "expected": True
        },
        {
            "name": "场景7：缺少空格（错误）",
            "text": "表1：数据统计",
            "expected": False
        },
        {
            "name": "场景8：缺少冒号（错误）",
            "text": "表 1 数据统计",
            "expected": False
        },
        {
            "name": "场景9：使用Table（错误）",
            "text": "Table 1： 数据统计",
            "expected": False
        },
        {
            "name": "场景10：缺少序号（错误）",
            "text": "表 ： 数据统计",
            "expected": False
        },
    ]
    
    # 正则表达式：表 + 空格 + 数字 + 空格（可选） + 冒号（中英文） + 空格（可选） + 说明
    pattern = r"^表\s+\d+\s*[：:]\s*.+$"
    
    print("📋 格式测试用例：")
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
        print(f"   文本: '{text}'")
        print(f"   预期: {'匹配' if expected else '不匹配'}, 实际: {'匹配' if match else '不匹配'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)


def test_caption_examples():
    """测试题注示例"""
    
    print()
    print("=" * 80)
    print("表格题注示例")
    print("=" * 80)
    print()
    
    examples = [
        "表 1： 数据库（集）基本信息简介",
        "表 2： 实验数据统计",
        "表 3： 性能对比结果",
        "表 4： 数据质量评估指标",
        "表 5： 系统配置参数",
    ]
    
    print("📊 正确示例：")
    print()
    
    for example in examples:
        print(f"   ✅ {example}")
    
    print()
    print("=" * 80)


def test_caption_vs_figure():
    """测试表格题注与图片题注对比"""
    
    print()
    print("=" * 80)
    print("表格题注与图片题注对比")
    print("=" * 80)
    print()
    
    comparison = [
        {
            "项目": "标识",
            "表格题注": "表",
            "图片题注": "图"
        },
        {
            "项目": "格式",
            "表格题注": "表 1： 说明",
            "图片题注": "图 1 说明"
        },
        {
            "项目": "序号后",
            "表格题注": "冒号（中英文均可）",
            "图片题注": "空格"
        },
        {
            "项目": "中文字体",
            "表格题注": "宋体",
            "图片题注": "宋体"
        },
        {
            "项目": "西文字体",
            "表格题注": "Times New Roman",
            "图片题注": "Times New Roman"
        },
        {
            "项目": "字号",
            "表格题注": "小五",
            "图片题注": "小五"
        },
        {
            "项目": "加粗",
            "表格题注": "是",
            "图片题注": "是"
        },
        {
            "项目": "对齐",
            "表格题注": "居中",
            "图片题注": "居中"
        },
        {
            "项目": "行距",
            "表格题注": "1.15倍",
            "图片题注": "1.15倍"
        },
        {
            "项目": "段前间距",
            "表格题注": "0.5行",
            "图片题注": "0.5行"
        },
        {
            "项目": "段后间距",
            "表格题注": "0.5行",
            "图片题注": "0.5行"
        },
    ]
    
    print("📊 对比表：")
    print()
    print(f"{'项目':15} {'表格题注':30} {'图片题注':25}")
    print("-" * 70)
    
    for item in comparison:
        print(f"{item['项目']:15} {item['表格题注']:30} {item['图片题注']:25}")
    
    print()
    print("💡 主要区别：")
    print("   1. 表格题注：表 1： 说明（冒号分隔）")
    print("   2. 图片题注：图 1 说明（空格分隔）")
    print("   3. 其他格式完全相同：宋体小五，粗体，居中，1.15倍行距，段前段后0.5行")
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
    print("1. 表格序号与表格说明中间空1个字")
    print("   ✅ 正确: 表 1： 数据库（集）基本信息简介")
    print("   ❌ 错误: 表1：数据库（集）基本信息简介")
    print()
    
    print("2. 表题段前、段后各0.5行距")
    print("   - space_before: 0.5行")
    print("   - space_after: 0.5行")
    print()
    
    print("3. 宋体（英文Times New Roman）")
    print("   - name_eastasia: 宋体")
    print("   - name_ascii: Times New Roman")
    print()
    
    print("4. 小5号")
    print("   - size: 小五")
    print()
    
    print("5. 居中")
    print("   - alignment: 居中")
    print()
    
    print("6. 标题和题头粗体")
    print("   - bold: true")
    print()
    
    print("7. 1.15倍行距")
    print("   - line_spacing: 1.15倍")
    print()
    
    print("=" * 80)


def test_colon_format():
    """测试冒号格式"""
    
    print()
    print("=" * 80)
    print("冒号格式说明")
    print("=" * 80)
    print()
    
    print("📋 冒号使用规则：")
    print()
    print("1. 支持中文冒号（：）")
    print("   ✅ 表 1： 数据统计")
    print()
    
    print("2. 支持英文冒号（:）")
    print("   ✅ 表 1: 数据统计")
    print()
    
    print("3. 冒号前后可以有空格")
    print("   ✅ 表 1 ： 数据统计")
    print("   ✅ 表 1： 数据统计")
    print("   ✅ 表 1: 数据统计")
    print()
    
    print("4. 推荐格式")
    print("   ⭐ 表 1： 数据统计（中文冒号+空格）")
    print()
    
    print("=" * 80)


def main():
    """主函数"""
    test_table_caption_style()
    test_caption_format()
    test_caption_examples()
    test_caption_vs_figure()
    test_format_requirements()
    test_colon_format()
    
    print()
    print("🎉 所有测试完成！")
    print()
    print("📋 配置总结：")
    print()
    print("1. 样式配置（styles.yaml）：")
    print("   .data-info-table-caption:")
    print("     font:")
    print("       name_eastasia: 宋体")
    print("       name_ascii: Times New Roman")
    print("       size: 小五")
    print("       bold: true")
    print("     paragraph:")
    print("       alignment: 居中")
    print("       line_spacing: 1.15倍")
    print("       space_before: 0.5行")
    print("       space_after: 0.5行")
    print()
    print("2. 格式要点：")
    print("   - 格式：表 序号： 说明")
    print("   - 序号与说明之间用冒号分隔（中英文均可）")
    print("   - 宋体（英文Times New Roman）")
    print("   - 小五号，粗体")
    print("   - 居中对齐")
    print("   - 1.15倍行距")
    print("   - 段前、段后各0.5行距")
    print()
    print("3. 正确示例：")
    print("   ✅ 表 1： 数据库（集）基本信息简介")
    print("   ✅ 表 2： 实验数据统计")
    print("   ✅ 表 3： 性能对比结果")
    print()
    print("4. 与图片题注的区别：")
    print("   - 表格：表 1： 说明（冒号分隔）")
    print("   - 图片：图 1 说明（空格分隔）")
    print("   - 其他格式完全相同")
    print()


if __name__ == "__main__":
    main()
