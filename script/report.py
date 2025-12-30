#!/usr/bin/env python3
"""
Report generation functions.
"""

from datetime import datetime


def generate_markdown_report(docx_path, structure, headers, footers, header_consistency, footer_consistency, empty_lines_check, figure_check, caption_check):
    """Generate a markdown report of the document format check."""
    docx_name = docx_path.name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    md_content = []
    md_content.append("# 文档格式检查报告\n")
    md_content.append(f"**文档名称**: {docx_name}\n")
    md_content.append(f"**检查时间**: {timestamp}\n")
    md_content.append("\n---\n")

    md_content.append("\n## 1. 文档结构分析\n")
    md_content.append(f"- **页眉文件数量**: {len(structure['headers'])}")
    md_content.append(f"- **页脚文件数量**: {len(structure['footers'])}")

    md_content.append("\n## 2. 页眉检查\n")
    md_content.append("### 2.1 页眉内容详情\n")

    if headers:
        md_content.append(f"共发现 **{len(headers)}** 个有内容的页眉：\n")
        for i, header in enumerate(headers, 1):
            md_content.append(f"#### 页眉 {i}\n")
            md_content.append(f"- **文件**: `{header['file']}`")
            md_content.append(f"- **内容**: {header['text']}")
            if header.get('page_info'):
                page_ranges = []
                for info in header['page_info']:
                    page_ranges.append(f"约第 {info['estimated_start_page']} 页起（节 {info['section']}，段落 {info['start_para']}）")
                if page_ranges:
                    md_content.append(f"- **出现位置**: {', '.join(page_ranges)}")
            md_content.append("")
    else:
        md_content.append("未发现页眉内容。\n")

    md_content.append("\n### 2.2 页眉一致性检查\n")
    if header_consistency['consistent']:
        md_content.append("✅ **状态**: 通过\n")
        md_content.append(f"**结果**: {header_consistency['message']}\n")
    else:
        md_content.append("❌ **状态**: 失败\n")
        md_content.append(f"**结果**: {header_consistency['message']}\n")
        if 'variations' in header_consistency:
            md_content.append("\n**页眉变化情况**:\n")
            for header_text, count in header_consistency['variations'].items():
                md_content.append(f"- `{header_text}` (出现 {count} 次)")

    md_content.append("\n## 3. 页脚检查\n")
    md_content.append("### 3.1 页脚内容详情\n")

    if footers:
        md_content.append(f"共发现 **{len(footers)}** 个有内容的页脚：\n")
        for i, footer in enumerate(footers, 1):
            md_content.append(f"#### 页脚 {i}\n")
            md_content.append(f"- **文件**: `{footer['file']}`")
            md_content.append(f"- **内容**: {footer['text']}")
            if footer.get('page_info'):
                page_ranges = []
                for info in footer['page_info']:
                    page_ranges.append(f"约第 {info['estimated_start_page']} 页起（节 {info['section']}，段落 {info['start_para']}）")
                if page_ranges:
                    md_content.append(f"- **出现位置**: {', '.join(page_ranges)}")
            md_content.append("")
    else:
        md_content.append("未发现页脚内容。\n")

    md_content.append("\n### 3.2 页脚一致性检查\n")
    if footer_consistency['consistent']:
        md_content.append("✅ **状态**: 通过\n")
        md_content.append(f"**结果**: {footer_consistency['message']}\n")
    else:
        md_content.append("❌ **状态**: 失败\n")
        md_content.append(f"**结果**: {footer_consistency['message']}\n")
        if 'variations' in footer_consistency:
            md_content.append("\n**页脚变化情况**:\n")
            for footer_text, count in footer_consistency['variations'].items():
                md_content.append(f"- `{footer_text}` (出现 {count} 次)")

    md_content.append("\n## 4. 连续空行检查\n")
    if empty_lines_check['found']:
        md_content.append("❌ **状态**: 发现问题\n")
        md_content.append(f"**结果**: {empty_lines_check['message']}\n")
        if 'total_paragraphs' in empty_lines_check:
            md_content.append(f"**文档总段落数**: {empty_lines_check['total_paragraphs']}\n")
        if empty_lines_check['details']:
            md_content.append("\n**连续空行位置**:\n")
            md_content.append("| 序号 | 段落范围 | 空行数 | 页码 | 上下文 |")
            md_content.append("|------|----------|--------|------|--------|")

            for idx, detail in enumerate(empty_lines_check['details'], 1):
                para_range = f"{detail['start']}-{detail['end']}"
                count = detail['count']

                page_info = ""
                if 'estimated_start_page' in detail and 'estimated_end_page' in detail:
                    if detail['estimated_start_page'] == detail['estimated_end_page']:
                        page_info = f"第 {detail['estimated_start_page']} 页"
                    else:
                        page_info = f"第 {detail['estimated_start_page']}-{detail['estimated_end_page']} 页"
                else:
                    page_info = "-"

                context_parts = []
                if detail.get('context_before'):
                    before_text = '; '.join(detail['context_before'])
                    if before_text:
                        before_short = before_text[:17] + '...' if len(before_text) > 17 else before_text
                        context_parts.append(f"前: {before_short}")
                if detail.get('context_after'):
                    after_text = '; '.join(detail['context_after'])
                    if after_text:
                        after_short = after_text[:17] + '...' if len(after_text) > 17 else after_text
                        context_parts.append(f"后: {after_short}")

                context_info = ' | '.join(context_parts) if context_parts else "-"

                md_content.append(f"| {idx} | {para_range} | {count} | {page_info} | {context_info} |")
    else:
        md_content.append("✅ **状态**: 通过\n")
        md_content.append(f"**结果**: {empty_lines_check['message']}\n")
        if 'total_paragraphs' in empty_lines_check:
            md_content.append(f"**文档总段落数**: {empty_lines_check['total_paragraphs']}\n")

    md_content.append("\n## 5. 图表前后空行检查\n")
    if figure_check['found']:
        md_content.append("❌ **状态**: 发现问题\n")
        md_content.append(f"**结果**: {figure_check['message']}\n")
        if figure_check['details']:
            md_content.append("\n**图表前后空行位置**:\n")
            md_content.append("| 序号 | 段落 | 页码 | 前有空行 | 后有空行 |")
            md_content.append("|------|------|------|----------|----------|")

            for idx, detail in enumerate(figure_check['details'], 1):
                before_status = "是" if detail['before_empty'] else "否"
                after_status = "是" if detail['after_empty'] else "否"
                md_content.append(f"| {idx} | {detail['paragraph']} | 第 {detail['page']} 页 | {before_status} | {after_status} |")
    else:
        md_content.append("✅ **状态**: 通过\n")
        md_content.append(f"**结果**: {figure_check['message']}\n")

    md_content.append("\n## 6. 题注对齐检查\n")
    if caption_check['found']:
        md_content.append("❌ **状态**: 发现问题\n")
        md_content.append(f"**结果**: {caption_check['message']}\n")
        if caption_check['details']:
            md_content.append("\n**题注对齐问题位置**:\n")
            md_content.append("| 序号 | 段落 | 页码 | 类型 | 对齐方式 | 题注内容 |")
            md_content.append("|------|------|------|------|----------|----------|")

            for idx, detail in enumerate(caption_check['details'], 1):
                alignment_map = {
                    'left': '左对齐',
                    'right': '右对齐',
                    'justify': '两端对齐',
                    'center': '居中'
                }
                alignment_text = alignment_map.get(detail['alignment'], detail['alignment'])
                md_content.append(f"| {idx} | {detail['paragraph']} | 第 {detail['page']} 页 | {detail['type']} | {alignment_text} | {detail['text']} |")
    else:
        md_content.append("✅ **状态**: 通过\n")
        md_content.append(f"**结果**: {caption_check['message']}\n")

    md_content.append("\n---\n")
    md_content.append("\n## 7. 检查总结\n")

    header_status = "✅ 通过" if header_consistency['consistent'] else "❌ 失败"
    footer_status = "✅ 通过" if footer_consistency['consistent'] else "❌ 失败"
    empty_lines_status = "✅ 通过" if not empty_lines_check['found'] else "❌ 失败"
    figure_status = "✅ 通过" if not figure_check['found'] else "❌ 失败"
    caption_status = "✅ 通过" if not caption_check['found'] else "❌ 失败"

    md_content.append("| 检查项 | 状态 |")
    md_content.append("|--------|------|")
    md_content.append(f"| 页眉一致性 | {header_status} |")
    md_content.append(f"| 页脚一致性 | {footer_status} |")
    md_content.append(f"| 连续空行检查 | {empty_lines_status} |")
    md_content.append(f"| 图表前后空行检查 | {figure_status} |")
    md_content.append(f"| 题注对齐检查 | {caption_status} |")

    issues = []
    if not header_consistency['consistent']:
        issues.append(f"**页眉**: {header_consistency['message']}")
    if not footer_consistency['consistent']:
        issues.append(f"**页脚**: {footer_consistency['message']}")
    if empty_lines_check['found']:
        issues.append(f"**连续空行**: {empty_lines_check['message']}")
    if figure_check['found']:
        issues.append(f"**图表前后空行**: {figure_check['message']}")
    if caption_check['found']:
        issues.append(f"**题注对齐**: {caption_check['message']}")

    if issues:
        md_content.append("\n### 发现的问题\n")
        for issue in issues:
            md_content.append(f"- {issue}\n")
    else:
        md_content.append("\n✅ **所有格式检查通过！**\n")

    md_content.append("\n---\n")
    md_content.append("\n*报告由文档格式检查脚本自动生成*\n")

    return '\n'.join(md_content)

