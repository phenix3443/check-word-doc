#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考文献分析脚本测试

用于测试 generate_reference_analysis.py 的功能
"""

import os
import sys
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

def test_with_sample_data():
    """使用示例数据测试脚本"""

    # 设置测试路径
    main_report = "/Users/liushangliang/github/phenix3443/idea/23年项目/年度报告/2025/项目报告/2025年度-23 年项目-科技报告-202512241156.docx"
    subject_reports = "/Users/liushangliang/github/phenix3443/idea/23年项目/年度报告/2025/课题报告/"
    output_file = "test_reference_analysis.md"

    # 检查文件是否存在
    if not os.path.exists(main_report):
        print(f"警告: 主报告文件不存在: {main_report}")
        return False

    if not os.path.exists(subject_reports):
        print(f"警告: 课题报告目录不存在: {subject_reports}")
        return False

    try:
        from generate_reference_analysis import ReferenceAnalyzer

        print("开始测试参考文献分析脚本...")

        # 创建分析器
        analyzer = ReferenceAnalyzer()

        # 分析主报告
        print("1. 分析主报告...")
        main_data = analyzer.analyze_main_report(main_report)
        if main_data:
            print(f"   ✓ 主报告分析成功: {main_data['total_references']} 条参考文献")
        else:
            print("   ✗ 主报告分析失败")
            return False

        # 分析课题报告
        print("2. 分析课题报告...")
        subject_data = analyzer.analyze_subject_reports(subject_reports)
        if subject_data:
            success_count = len([s for s in subject_data.values() if s.get('status') == 'success'])
            print(f"   ✓ 课题报告分析成功: {success_count} 个课题")
        else:
            print("   ✗ 课题报告分析失败")
            return False

        # 生成报告
        print("3. 生成分析报告...")
        output_path = analyzer.generate_analysis_report(output_file)
        if os.path.exists(output_path):
            print(f"   ✓ 报告生成成功: {output_path}")

            # 显示报告文件大小
            file_size = os.path.getsize(output_path)
            print(f"   报告文件大小: {file_size} 字节")

            return True
        else:
            print("   ✗ 报告生成失败")
            return False

    except ImportError as e:
        print(f"导入错误: {e}")
        return False
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_line():
    """测试命令行接口"""

    print("\n测试命令行接口...")

    # 构建命令
    main_report = "/Users/liushangliang/github/phenix3443/idea/23年项目/年度报告/2025/项目报告/2025年度-23 年项目-科技报告-202512241156.docx"
    subject_reports = "/Users/liushangliang/github/phenix3443/idea/23年项目/年度报告/2025/课题报告/"
    output_file = "test_cli_reference_analysis.md"

    cmd = f'python generate_reference_analysis.py --main-report "{main_report}" --subject-reports "{subject_reports}" --output "{output_file}" --verbose'

    print(f"执行命令: {cmd}")

    # 执行命令
    result = os.system(cmd)

    if result == 0:
        print("✓ 命令行测试成功")
        if os.path.exists(output_file):
            print(f"✓ 输出文件生成成功: {output_file}")
            return True
        else:
            print("✗ 输出文件未生成")
            return False
    else:
        print(f"✗ 命令行测试失败，返回码: {result}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("参考文献分析脚本测试")
    print("=" * 60)

    # 测试1: 直接调用API
    test1_result = test_with_sample_data()

    # 测试2: 命令行接口
    test2_result = test_command_line()

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print(f"API调用测试: {'✓ 通过' if test1_result else '✗ 失败'}")
    print(f"命令行测试: {'✓ 通过' if test2_result else '✗ 失败'}")

    if test1_result and test2_result:
        print("\n🎉 所有测试通过！脚本可以正常使用。")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
