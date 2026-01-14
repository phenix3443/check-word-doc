#!/usr/bin/env python3
"""
文档结构检查功能测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'script'))

from structure import run_structure_check, analyze_document_structure
from config_loader import ConfigLoader

def test_basic_structure_check():
    """测试基本结构检查"""
    print("测试基本结构检查...")
    
    test_doc = os.path.join(os.path.dirname(__file__), "basic.docx")
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'base.yaml')
    
    if not os.path.exists(test_doc):
        print(f"  ✗ 测试文档不存在: {test_doc}")
        return
    
    if not os.path.exists(config_path):
        print(f"  ✗ 配置文件不存在: {config_path}")
        return
    
    try:
        # 加载配置
        config_loader = ConfigLoader(config_path)
        config_loader.load()
        
        # 分析文档结构
        structure = analyze_document_structure(test_doc)
        
        # 运行结构检查
        result = run_structure_check(test_doc, config_loader, structure)
        
        print(f"  检查结果: {result['message']}")
        print(f"  发现问题: {'是' if result['found'] else '否'}")
        
        if result.get('details'):
            print("  问题详情:")
            for detail in result['details']:
                print(f"    - {detail['message']}")
        
        print("  ✓ 基本结构检查测试完成")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")

def test_scientific_report_structure():
    """测试科技报告结构检查"""
    print("\n测试科技报告结构检查...")
    
    test_doc = os.path.join(os.path.dirname(__file__), "report.docx")
    config_path = "/Users/liushangliang/github/phenix3443/idea/23年项目/年度报告/2025/task/科技报告/科技报告-2025.yaml"
    
    if not os.path.exists(test_doc):
        print(f"  ✗ 测试文档不存在: {test_doc}")
        return
    
    if not os.path.exists(config_path):
        print(f"  ✗ 配置文件不存在: {config_path}")
        return
    
    try:
        # 加载配置
        config_loader = ConfigLoader(config_path)
        config_loader.load()
        
        # 分析文档结构
        structure = analyze_document_structure(test_doc)
        
        # 运行结构检查
        result = run_structure_check(test_doc, config_loader, structure)
        
        print(f"  检查结果: {result['message']}")
        print(f"  发现问题: {'是' if result['found'] else '否'}")
        
        if result.get('details'):
            print("  问题详情:")
            for detail in result['details']:
                print(f"    - {detail['message']}")
        
        print("  ✓ 科技报告结构检查测试完成")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")

def test_structure_analysis():
    """测试文档结构分析"""
    print("\n测试文档结构分析...")
    
    test_docs = [
        ("basic.docx", "完整结构文档"),
        ("report.docx", "科技报告文档")
    ]
    
    for doc_name, doc_desc in test_docs:
        test_doc = os.path.join(os.path.dirname(__file__), doc_name)
        
        if not os.path.exists(test_doc):
            print(f"  ✗ {doc_desc}不存在: {test_doc}")
            continue
        
        try:
            structure = analyze_document_structure(test_doc)
            
            print(f"  {doc_desc}结构分析:")
            print(f"    总段落数: {structure.get('total_paragraphs', 0)}")
            
            document_parts = structure.get('document_parts', {})
            for part_name, part_info in document_parts.items():
                if part_info.get('paragraphs'):
                    start = min(part_info['paragraphs'])
                    end = max(part_info['paragraphs'])
                    count = len(part_info['paragraphs'])
                    print(f"    {part_name}: 段落{start}-{end} ({count}个)")
            
            print(f"  ✓ {doc_desc}分析完成")
            
        except Exception as e:
            print(f"  ✗ {doc_desc}分析失败: {e}")

if __name__ == "__main__":
    print("文档结构检查功能测试")
    print("=" * 50)
    
    test_structure_analysis()
    test_basic_structure_check()
    test_scientific_report_structure()
    
    print("\n" + "=" * 50)
    print("使用说明:")
    print("1. 生成完整结构测试文档:")
    print("   poetry run python test/struct/create_complete_doc.py")
    print()
    print("2. 生成科技报告测试文档:")
    print("   poetry run python test/struct/create_scientific_report.py")
    print()
    print("3. 运行结构检查:")
    print("   poetry run python script/check.py --check structure --config config/base.yaml test/struct/basic.docx")
    print("   poetry run python script/check.py --check structure --config 2025/task/科技报告/科技报告-2025.yaml test/struct/report.docx")
    print()
    print("✅ 测试完成")