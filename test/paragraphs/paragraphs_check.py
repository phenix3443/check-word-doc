#!/usr/bin/env python3
"""
段落检查功能测试
包括基于Word样式的段落检查和完整功能测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'script'))

from paragraphs import run_paragraphs_check, _get_paragraphs_by_styles, _is_target_style
from config_loader import ConfigLoader

def test_style_matching():
    """测试样式匹配逻辑"""
    print("测试样式匹配逻辑...")
    
    # 测试用例
    test_cases = [
        # (style_val, target_styles, expected)
        (None, ["Normal", "正文"], True),  # 无样式匹配Normal
        ("Normal", ["Normal", "正文"], True),  # 直接匹配
        ("正文", ["Normal", "正文"], True),  # 直接匹配
        ("Heading1", ["Normal", "正文"], False),  # 不匹配
        ("normal", ["Normal"], True),  # 忽略大小写
        ("NORMAL", ["normal"], True),  # 忽略大小写
        ("", ["Normal"], True),  # 空字符串匹配Normal
    ]
    
    for i, (style_val, target_styles, expected) in enumerate(test_cases):
        result = _is_target_style(style_val, target_styles)
        status = "✓" if result == expected else "✗"
        print(f"  测试 {i+1}: {status} 样式='{style_val}', 目标={target_styles}, 期望={expected}, 实际={result}")

def test_get_paragraphs_by_styles():
    """测试从文档中获取指定样式的段落"""
    print("\n测试从文档中获取指定样式的段落...")
    
    test_doc = os.path.join(os.path.dirname(__file__), "test.docx")
    if not os.path.exists(test_doc):
        print(f"  ✗ 测试文档不存在: {test_doc}")
        return
    
    # 测试获取正文样式的段落
    target_styles = ["Normal", "正文"]
    paragraphs = _get_paragraphs_by_styles(test_doc, target_styles)
    
    print(f"  找到 {len(paragraphs)} 个使用样式 {target_styles} 的段落")
    print(f"  段落索引: {paragraphs}")
    
    # 测试获取标题样式的段落
    heading_styles = ["Heading 1", "Heading 2", "Heading 3", "标题 1", "标题 2", "标题 3"]
    heading_paragraphs = _get_paragraphs_by_styles(test_doc, heading_styles)
    
    print(f"  找到 {len(heading_paragraphs)} 个使用标题样式的段落")
    print(f"  标题段落索引: {heading_paragraphs}")

def test_paragraphs_functionality():
    """测试段落检查完整功能"""
    print("\n" + "=" * 60)
    print("段落检查功能测试")
    print("=" * 60)
    
    try:
        # 使用 base.yaml 配置文件
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'base.yaml')
        test_doc = os.path.join(os.path.dirname(__file__), "test.docx")
        
        print(f"配置文件: {os.path.relpath(config_path)}")
        print(f"测试文档: {os.path.relpath(test_doc)}")
        
        # 检查文件是否存在
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False
            
        if not os.path.exists(test_doc):
            print(f"❌ 测试文档不存在: {test_doc}")
            print("请先运行 create_test_doc.py 生成测试文档")
            return False
        
        print("\n" + "-" * 60)
        print("开始检查...")
        print("-" * 60)
        
        # 加载配置并执行检查
        config_loader = ConfigLoader(config_path)
        result = run_paragraphs_check(test_doc, config_loader)
        
        print("\n" + "-" * 60)
        print("检查结果分析:")
        print("-" * 60)
        
        print(f"检查状态: {'发现问题' if result.get('found') else '未发现问题'}")
        print(f"检查消息: {result.get('message', 'N/A')}")
        
        details = result.get('details', {})
        
        # 分析中文间距问题
        spacing_issues = details.get('spacing', [])
        print(f"\n中文间距问题: {len(spacing_issues)} 个")
        if spacing_issues:
            print("  预期: 5个问题（段落5、6中的间距问题）")
            print("  实际:")
            for i, issue in enumerate(spacing_issues[:5], 1):
                para = issue.get('paragraph', 'N/A')
                text = issue.get('text', 'N/A')
                print(f"    {i}. 段落 {para}: '{text}'")
        
        # 分析引号问题
        quotes_details = details.get('quotes', {})
        english_quotes = quotes_details.get('english_quotes', [])
        quote_matching = quotes_details.get('quote_matching', [])
        
        print(f"\n英文引号问题: {len(english_quotes)} 个")
        if english_quotes:
            print("  预期: 2个问题（段落7、8中的英文引号）")
            print("  实际:")
            for i, issue in enumerate(english_quotes[:5], 1):
                para = issue.get('paragraph', 'N/A')
                text = issue.get('text', 'N/A')
                print(f"    {i}. 段落 {para}: '{text}'")
        else:
            print("  预期: 2个问题，但未检测到")
        
        print(f"\n引号匹配问题: {len(quote_matching)} 个")
        if quote_matching:
            print("  预期: 2个问题（段落10、11中的不匹配引号）")
            print("  实际:")
            for i, issue in enumerate(quote_matching[:5], 1):
                para = issue.get('paragraph', 'N/A')
                text = issue.get('problem_text', issue.get('text', 'N/A'))
                print(f"    {i}. 段落 {para}: '{text}'")
        else:
            print("  预期: 2个问题，但未检测到")
        
        # 分析空行问题
        empty_lines_issues = details.get('empty_lines', [])
        print(f"\n连续空行问题: {len(empty_lines_issues)} 个")
        if empty_lines_issues:
            print("  预期: 1个问题（段落12、13之间的连续空行）")
            print("  实际:")
            for i, issue in enumerate(empty_lines_issues[:3], 1):
                start = issue.get('start_paragraph', 'N/A')
                end = issue.get('end_paragraph', 'N/A')
                count = issue.get('consecutive_count', 'N/A')
                print(f"    {i}. 段落 {start}-{end}: {count} 个连续空行")
        else:
            print("  预期: 1个问题，但未检测到")
        
        print("\n" + "-" * 60)
        print("测试总结:")
        print("-" * 60)
        
        # 评估测试结果
        total_expected = 5 + 2 + 2 + 1  # 间距 + 英文引号 + 引号匹配 + 空行
        total_found = len(spacing_issues) + len(english_quotes) + len(quote_matching) + len(empty_lines_issues)
        
        print(f"预期问题总数: {total_expected}")
        print(f"实际检测到: {total_found}")
        
        if result.get('found'):
            print("✅ 检查功能正常工作（检测到问题）")
        else:
            print("❌ 检查功能可能有问题（未检测到预期问题）")
        
        # 详细分析
        success_rate = (total_found / total_expected * 100) if total_expected > 0 else 0
        print(f"检测成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 测试通过！检查功能基本正常")
            return True
        elif success_rate >= 50:
            print("⚠️  测试部分通过，需要调试某些检查逻辑")
            return True
        else:
            print("❌ 测试失败，需要检查配置和检查逻辑")
            return False
            
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_usage():
    """显示使用说明"""
    print("\n" + "=" * 60)
    print("使用说明:")
    print("=" * 60)
    print("1. 生成测试文档:")
    print("   poetry run python test/paragraphs/create_test_doc.py")
    print()
    print("2. 运行功能测试:")
    print("   poetry run python test/paragraphs/paragraphs_check.py")
    print()
    print("3. 运行完整检查:")
    print("   poetry run python script/check.py --check paragraphs --config config/base.yaml test/paragraphs/test.docx")

if __name__ == "__main__":
    print("段落检查功能测试")
    print("=" * 50)
    
    # 运行样式测试
    test_style_matching()
    test_get_paragraphs_by_styles()
    
    # 运行功能测试
    success = test_paragraphs_functionality()
    
    # 显示使用说明
    show_usage()
    
    if success:
        print("\n✅ 测试完成")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)