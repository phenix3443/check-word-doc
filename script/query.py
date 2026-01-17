#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档查询工具

使用 Selector 语法查询文档元素，类似于 CSS 选择器。
"""

import argparse
from pathlib import Path
from typing import List

from script.config_loader import ConfigLoader
from script.core.engine import DocxLint
from script.core.model import Block, ParagraphBlock, TableBlock
from script.core.selector import Selector


def format_block_content(block: Block, max_length: int = 100) -> str:
    """格式化 block 内容用于显示
    
    Args:
        block: 文档块
        max_length: 最大显示长度
        
    Returns:
        格式化后的内容字符串
    """
    if isinstance(block, ParagraphBlock):
        content = block.paragraph.text.strip()
        if len(content) > max_length:
            content = content[:max_length] + "..."
        return content
    elif isinstance(block, TableBlock):
        rows = block.table.rows
        cols = len(rows[0].cells) if rows else 0
        return f"<表格: {len(rows)}行 x {cols}列>"
    else:
        return f"<{type(block).__name__}>"


def print_blocks(blocks: List[Block], show_classes: bool = True, show_index: bool = True):
    """打印 block 列表
    
    Args:
        blocks: 文档块列表
        show_classes: 是否显示类名
        show_index: 是否显示索引
    """
    if not blocks:
        print("❌ 未找到匹配的元素")
        return
    
    print(f"✅ 找到 {len(blocks)} 个匹配的元素:")
    print()
    
    for i, block in enumerate(blocks, 1):
        # 索引
        if show_index:
            print(f"[{i}]", end=" ")
        
        # 类名
        if show_classes and block.classes:
            classes_str = ", ".join(block.classes)
            print(f"({classes_str})", end=" ")
        
        # 内容
        content = format_block_content(block)
        print(f"{content}")
        print()


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="文档查询工具 - 使用 CSS 风格的选择器查询文档元素",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查询所有标题
  %(prog)s document.docx --config config.yaml --selector ".heading"
  
  # 查询第一个作者
  %(prog)s document.docx --config config.yaml --selector ".author-list:first"
  
  # 查询第二个作者（索引从0开始）
  %(prog)s document.docx --config config.yaml --selector ".author-list:nth(1)"
  
  # 查询所有表格
  %(prog)s document.docx --config config.yaml --selector "[type='table']"
  
  # 查询参考文献列表
  %(prog)s document.docx --config config.yaml --selector ".reference-item"
  
  # 统计匹配元素数量
  %(prog)s document.docx --config config.yaml --selector ".heading" --count
  
  # 只显示第一个匹配元素
  %(prog)s document.docx --config config.yaml --selector ".abstract" --first
        """
    )
    
    parser.add_argument(
        "docx_path",
        type=str,
        help="Word 文档路径"
    )
    
    parser.add_argument(
        "--config", "-c",
        required=True,
        type=str,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--selector", "-s",
        required=True,
        type=str,
        help="CSS 风格的选择器（如 '.author-list:first'）"
    )
    
    parser.add_argument(
        "--count",
        action="store_true",
        help="只显示匹配元素的数量"
    )
    
    parser.add_argument(
        "--first",
        action="store_true",
        help="只显示第一个匹配的元素"
    )
    
    parser.add_argument(
        "--no-classes",
        action="store_true",
        help="不显示元素的类名"
    )
    
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="不显示元素的索引"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="显示完整内容（不截断）"
    )
    
    return parser.parse_args()


def main() -> int:
    """主函数"""
    args = parse_args()
    
    # 检查文档路径
    docx_path = Path(args.docx_path)
    if not docx_path.exists():
        print(f"❌ 文档不存在: {docx_path}")
        return 1
    
    # 加载配置
    print(f"📋 加载配置: {args.config}")
    try:
        loader = ConfigLoader(args.config)
        config = loader.load()
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 分析文档
    print(f"📄 分析文档: {docx_path}")
    try:
        from docx import Document
        from script.core.walker import Walker
        from script.core.classifier import Classifier
        
        # 读取文档
        doc = Document(str(docx_path))
        blocks = list(Walker().iter_blocks(doc))
        
        # 运行分类器
        document_config = config.get('document', {})
        if 'classifiers' in document_config:
            classifier = Classifier(document_config['classifiers'])
            blocks = classifier.classify(blocks)
        else:
            print("⚠️  配置中没有 classifiers，将无法使用类选择器")
    except Exception as e:
        print(f"❌ 文档分析失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print(f"✅ 文档共有 {len(blocks)} 个元素")
    print()
    
    # 创建选择器
    selector = Selector(blocks)
    
    # 执行查询
    print(f"🔍 查询选择器: {args.selector}")
    print()
    
    try:
        if args.count:
            # 只统计数量
            count = selector.count(args.selector)
            print(f"✅ 匹配元素数量: {count}")
        elif args.first:
            # 只显示第一个
            block = selector.select_one(args.selector)
            if block:
                print_blocks(
                    [block],
                    show_classes=not args.no_classes,
                    show_index=not args.no_index
                )
            else:
                print("❌ 未找到匹配的元素")
        else:
            # 显示所有匹配元素
            results = selector.select(args.selector)
            print_blocks(
                results,
                show_classes=not args.no_classes,
                show_index=not args.no_index
            )
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
