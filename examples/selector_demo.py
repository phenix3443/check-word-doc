#!/usr/bin/env python3
"""
Selector 使用示例

演示如何使用 Selector 系统查询和提取文档元素
"""

from docx import Document
from script.core.classifier import Classifier
from script.core.selector import Selector
from script.config_loader import ConfigLoader
import json


def demo_basic_usage():
    """基础用法演示"""
    print("=" * 60)
    print("示例1: 基础用法")
    print("=" * 60)
    
    # 这里使用测试数据
    from test.selector.selector_test import create_test_blocks
    blocks = create_test_blocks()
    selector = Selector(blocks)
    
    # 查询第二个作者的地址
    print("\n1. 查询第二个作者的地址：")
    affiliation = selector.select_one(".author-affiliation:nth(1)")
    if affiliation:
        print(f"   结果: {affiliation.paragraph.text}")
    
    # 查询参考文献的第二条
    print("\n2. 查询参考文献的第二条：")
    ref = selector.select_one(".reference-item:nth(1)")
    if ref:
        print(f"   结果: {ref.paragraph.text}")
    
    # 查询所有参考文献
    print("\n3. 查询所有参考文献：")
    refs = selector.select(".reference-item")
    print(f"   共 {len(refs)} 条参考文献")
    for i, ref in enumerate(refs, 1):
        print(f"   [{i}] {ref.paragraph.text}")
    
    print("\n✅ 基础用法演示完成\n")


def demo_pseudo_selectors():
    """伪类选择器演示"""
    print("=" * 60)
    print("示例2: 伪类选择器")
    print("=" * 60)
    
    from test.selector.selector_test import create_test_blocks
    blocks = create_test_blocks()
    selector = Selector(blocks)
    
    # :first
    print("\n1. 使用 :first 伪类：")
    first_ref = selector.select_one(".reference-item:first")
    if first_ref:
        print(f"   第一条参考文献: {first_ref.paragraph.text}")
    
    # :last
    print("\n2. 使用 :last 伪类：")
    last_ref = selector.select_one(".reference-item:last")
    if last_ref:
        print(f"   最后一条参考文献: {last_ref.paragraph.text}")
    
    # :nth(n)
    print("\n3. 使用 :nth(n) 伪类：")
    second_ref = selector.select_one(".reference-item:nth(1)")
    if second_ref:
        print(f"   第二条参考文献: {second_ref.paragraph.text}")
    
    print("\n✅ 伪类选择器演示完成\n")


def demo_adjacent_selectors():
    """相邻兄弟选择器演示"""
    print("=" * 60)
    print("示例3: 相邻兄弟选择器")
    print("=" * 60)
    
    from test.selector.selector_test import create_test_blocks
    blocks = create_test_blocks()
    selector = Selector(blocks)
    
    # 查询引言标题后的引言内容
    print("\n1. 查询引言标题后的引言内容：")
    intro = selector.select_one(".heading-introduction + .body-introduction")
    if intro:
        print(f"   结果: {intro.paragraph.text}")
    
    # 查询关键词后的引言标题
    print("\n2. 查询关键词后的引言标题：")
    heading = selector.select_one(".keywords + .heading-introduction")
    if heading:
        print(f"   结果: {heading.paragraph.text}")
    
    print("\n✅ 相邻兄弟选择器演示完成\n")


def demo_utility_methods():
    """工具方法演示"""
    print("=" * 60)
    print("示例4: 工具方法")
    print("=" * 60)
    
    from test.selector.selector_test import create_test_blocks
    blocks = create_test_blocks()
    selector = Selector(blocks)
    
    # exists()
    print("\n1. 检查元素是否存在：")
    print(f"   是否有作者单位: {selector.exists('.author-affiliation')}")
    print(f"   是否有英文摘要: {selector.exists('.abstract-en')}")
    print(f"   是否有不存在的类: {selector.exists('.non-existent')}")
    
    # count()
    print("\n2. 统计元素数量：")
    print(f"   参考文献数量: {selector.count('.reference-item')}")
    print(f"   作者单位数量: {selector.count('.author-affiliation')}")
    
    # select_one()
    print("\n3. 选择第一个匹配的元素：")
    first_ref = selector.select_one(".reference-item")
    if first_ref:
        print(f"   第一条参考文献: {first_ref.paragraph.text}")
    
    print("\n✅ 工具方法演示完成\n")


def demo_extract_metadata():
    """提取文档元数据演示"""
    print("=" * 60)
    print("示例5: 提取文档元数据")
    print("=" * 60)
    
    from test.selector.selector_test import create_test_blocks
    blocks = create_test_blocks()
    selector = Selector(blocks)
    
    # 提取元数据
    metadata = {}
    
    # 标题
    title = selector.select_one(".title")
    metadata['title'] = title.paragraph.text if title else None
    
    # 作者
    authors = selector.select(".author-list")
    metadata['authors'] = [a.paragraph.text for a in authors]
    
    # 作者单位
    affiliations = selector.select(".author-affiliation")
    metadata['affiliations'] = [a.paragraph.text for a in affiliations]
    
    # 通讯作者
    corresponding = selector.select_one(".corresponding-author")
    metadata['corresponding'] = corresponding.paragraph.text if corresponding else None
    
    # 摘要
    abstract = selector.select_one(".abstract")
    metadata['abstract'] = abstract.paragraph.text if abstract else None
    
    # 关键词
    keywords = selector.select_one(".keywords")
    metadata['keywords'] = keywords.paragraph.text if keywords else None
    
    # 参考文献数量
    metadata['reference_count'] = selector.count(".reference-item")
    
    # 输出元数据
    print("\n提取的元数据：")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    
    print("\n✅ 元数据提取演示完成\n")


def demo_document_validation():
    """文档结构验证演示"""
    print("=" * 60)
    print("示例6: 文档结构验证")
    print("=" * 60)
    
    from test.selector.selector_test import create_test_blocks
    blocks = create_test_blocks()
    selector = Selector(blocks)
    
    # 检查必需的元素是否存在
    required_elements = [
        (".title", "论文标题"),
        (".author-list", "作者列表"),
        (".abstract", "中文摘要"),
        (".keywords", "关键词"),
        (".heading-references", "参考文献"),
    ]
    
    print("\n文档结构检查：")
    all_present = True
    for selector_str, name in required_elements:
        exists = selector.exists(selector_str)
        status = "✅" if exists else "❌"
        print(f"{status} {name}: {'存在' if exists else '缺失'}")
        if not exists:
            all_present = False
    
    if all_present:
        print("\n✅ 文档结构完整")
    else:
        print("\n❌ 文档结构不完整")
    
    print("\n✅ 文档结构验证演示完成\n")


def demo_conditional_filtering():
    """条件过滤演示"""
    print("=" * 60)
    print("示例7: 条件过滤")
    print("=" * 60)
    
    from test.selector.selector_test import create_test_blocks
    blocks = create_test_blocks()
    selector = Selector(blocks)
    
    # 查询包含特定关键词的参考文献
    print("\n1. 查询2023年的参考文献：")
    refs = selector.select(".reference-item")
    refs_2023 = [r for r in refs if "2023" in r.paragraph.text]
    print(f"   共 {len(refs_2023)} 条")
    for ref in refs_2023:
        print(f"   - {ref.paragraph.text}")
    
    # 查询包含特定内容的作者单位
    print("\n2. 查询北京的作者单位：")
    affiliations = selector.select(".author-affiliation")
    beijing_affiliations = [a for a in affiliations if "北京" in a.paragraph.text]
    print(f"   共 {len(beijing_affiliations)} 个")
    for aff in beijing_affiliations:
        print(f"   - {aff.paragraph.text}")
    
    print("\n✅ 条件过滤演示完成\n")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Selector 使用示例演示")
    print("=" * 60 + "\n")
    
    demo_basic_usage()
    demo_pseudo_selectors()
    demo_adjacent_selectors()
    demo_utility_methods()
    demo_extract_metadata()
    demo_document_validation()
    demo_conditional_filtering()
    
    print("=" * 60)
    print("✅ 所有示例演示完成！")
    print("=" * 60 + "\n")
    
    print("更多详细信息请参考：")
    print("  - doc/SELECTOR.md - Selector 语法规范")
    print("  - doc/SELECTOR_EXAMPLES.md - 详细使用示例")
    print("  - test/selector/selector_test.py - 测试用例")
    print()


if __name__ == "__main__":
    main()
