#!/usr/bin/env python3
"""
Report generation functions.
每个检查项都有独立的报告生成函数，互不影响。
"""

from datetime import datetime


def generate_structure_report(structure):
    """生成文档结构分析报告部分。"""
    md_content = []
    md_content.append("\n## 1. 文档结构分析\n")
    md_content.append(f"- **页眉文件数量**: {len(structure['headers'])}\n")
    md_content.append(f"- **页脚文件数量**: {len(structure['footers'])}\n")
    return "".join(md_content)


def generate_headers_report(headers, header_consistency):
    """生成页眉检查报告部分。"""
    md_content = []
    md_content.append("\n## 2. 页眉检查\n")
    md_content.append("### 2.1 页眉内容详情\n")

    if headers:
        md_content.append(f"共发现 **{len(headers)}** 个有内容的页眉：\n")
        for i, header in enumerate(headers, 1):
            md_content.append(f"#### 页眉 {i}\n")
            md_content.append(f"- **文件**: `{header['file']}`\n")
            md_content.append(f"- **内容**: {header['text']}\n")
            if header.get("page_info"):
                page_ranges = []
                for info in header["page_info"]:
                    page_ranges.append(
                        f"约第 {info['estimated_start_page']} 页起（节 {info['section']}，段落 {info['start_para']}）"
                    )
                if page_ranges:
                    md_content.append(f"- **出现位置**: {', '.join(page_ranges)}\n")
            md_content.append("\n")
    else:
        md_content.append("未发现页眉内容。\n")

    md_content.append("\n### 2.2 页眉一致性检查\n")
    if header_consistency and "consistent" in header_consistency:
        if header_consistency["consistent"]:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {header_consistency['message']}\n")
        else:
            md_content.append("❌ **状态**: 失败\n")
            md_content.append(f"**结果**: {header_consistency['message']}\n")
            if "variations" in header_consistency:
                md_content.append("\n**页眉变化情况**:\n")
                for header_text, count in header_consistency["variations"].items():
                    md_content.append(f"- `{header_text}` (出现 {count} 次)\n")
    else:
        md_content.append("⚠️ **状态**: 未检查\n")
        md_content.append("**结果**: 本次检查未包含页眉一致性检查\n")

    return "".join(md_content)


def generate_footers_report(footers, footer_consistency):
    """生成页脚检查报告部分。"""
    md_content = []
    md_content.append("\n## 3. 页脚检查\n")
    md_content.append("### 3.1 页脚内容详情\n")

    if footers:
        md_content.append(f"共发现 **{len(footers)}** 个有内容的页脚：\n")
        for i, footer in enumerate(footers, 1):
            md_content.append(f"#### 页脚 {i}\n")
            md_content.append(f"- **文件**: `{footer['file']}`\n")
            md_content.append(f"- **内容**: {footer['text']}\n")
            if footer.get("page_info"):
                page_ranges = []
                for info in footer["page_info"]:
                    page_ranges.append(
                        f"约第 {info['estimated_start_page']} 页起（节 {info['section']}，段落 {info['start_para']}）"
                    )
                if page_ranges:
                    md_content.append(f"- **出现位置**: {', '.join(page_ranges)}\n")
            md_content.append("\n")
    else:
        md_content.append("未发现页脚内容。\n")

    md_content.append("\n### 3.2 页脚一致性检查\n")
    if footer_consistency and "consistent" in footer_consistency:
        if footer_consistency["consistent"]:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {footer_consistency['message']}\n")
        else:
            md_content.append("❌ **状态**: 失败\n")
            md_content.append(f"**结果**: {footer_consistency['message']}\n")
            if "variations" in footer_consistency:
                md_content.append("\n**页脚变化情况**:\n")
                for footer_text, count in footer_consistency["variations"].items():
                    md_content.append(f"- `{footer_text}` (出现 {count} 次)\n")
    else:
        md_content.append("⚠️ **状态**: 未检查\n")
        md_content.append("**结果**: 本次检查未包含页脚一致性检查\n")

    return "".join(md_content)


def generate_empty_lines_report(empty_lines_check):
    """生成连续空行检查报告部分。"""
    md_content = []
    md_content.append("\n## 4. 连续空行检查\n")

    if empty_lines_check and "found" in empty_lines_check:
        if empty_lines_check["found"]:
            md_content.append("❌ **状态**: 发现问题\n")
            md_content.append(f"**结果**: {empty_lines_check['message']}\n")
            if "total_paragraphs" in empty_lines_check:
                md_content.append(
                    f"**文档总段落数**: {empty_lines_check['total_paragraphs']}\n"
                )
            if empty_lines_check["details"]:
                md_content.append("\n**连续空行位置**:\n")
                md_content.append("| 序号 | 段落范围 | 空行数 | 页码 | 上下文 |\n")
                md_content.append("|------|----------|--------|------|--------|\n")

                for idx, detail in enumerate(empty_lines_check["details"], 1):
                    para_range = f"{detail['start']}-{detail['end']}"
                    count = detail["count"]

                    page_info = ""
                    if (
                        "estimated_start_page" in detail
                        and "estimated_end_page" in detail
                    ):
                        if (
                            detail["estimated_start_page"]
                            == detail["estimated_end_page"]
                        ):
                            page_info = f"第 {detail['estimated_start_page']} 页"
                        else:
                            page_info = f"第 {detail['estimated_start_page']}-{detail['estimated_end_page']} 页"
                    else:
                        page_info = "-"

                    context_parts = []
                    if detail.get("context_before"):
                        before_text = "; ".join(detail["context_before"])
                        if before_text:
                            before_short = (
                                before_text[:17] + "..."
                                if len(before_text) > 17
                                else before_text
                            )
                            context_parts.append(f"前: {before_short}")
                    if detail.get("context_after"):
                        after_text = "; ".join(detail["context_after"])
                        if after_text:
                            after_short = (
                                after_text[:17] + "..."
                                if len(after_text) > 17
                                else after_text
                            )
                            context_parts.append(f"后: {after_short}")

                    context_info = " | ".join(context_parts) if context_parts else "-"

                    md_content.append(
                        f"| {idx} | {para_range} | {count} | {page_info} | {context_info} |\n"
                    )
        else:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {empty_lines_check['message']}\n")
            if "total_paragraphs" in empty_lines_check:
                md_content.append(
                    f"**文档总段落数**: {empty_lines_check['total_paragraphs']}\n"
                )
    else:
        md_content.append("⚠️ **状态**: 未检查\n")
        md_content.append("**结果**: 本次检查未包含连续空行检查\n")

    return "".join(md_content)


def generate_figures_report(figure_check):
    """生成图表前后空行检查报告部分。"""
    md_content = []
    md_content.append("\n## 5. 图表前后空行检查\n")

    if figure_check and "found" in figure_check:
        if figure_check["found"]:
            md_content.append("❌ **状态**: 发现问题\n")
            md_content.append(f"**结果**: {figure_check['message']}\n")
            if figure_check["details"]:
                md_content.append("\n**图表前后空行位置**:\n")
                md_content.append("| 序号 | 图片索引 | 页码 | 前有空行 | 后有空行 |\n")
                md_content.append("|------|----------|------|----------|----------|\n")

                for idx, detail in enumerate(figure_check["details"], 1):
                    before_status = "是" if detail["before_empty"] else "否"
                    after_status = "是" if detail["after_empty"] else "否"
                    figure_idx = detail.get(
                        "figure_index", detail.get("paragraph", idx)
                    )  # 兼容旧格式
                    md_content.append(
                        f"| {idx} | 图片 {figure_idx} | 第 {detail['page']} 页 | {before_status} | {after_status} |\n"
                    )
        else:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {figure_check['message']}\n")
    else:
        md_content.append("⚠️ **状态**: 未检查\n")
        md_content.append("**结果**: 本次检查未包含图表前后空行检查\n")

    return "".join(md_content)


def generate_captions_report(caption_check):
    """生成题注对齐检查报告部分。"""
    md_content = []
    md_content.append("\n## 6. 题注对齐检查\n")

    if caption_check and "found" in caption_check:
        if caption_check["found"]:
            md_content.append("❌ **状态**: 发现问题\n")
            md_content.append(f"**结果**: {caption_check['message']}\n")
            if caption_check["details"]:
                md_content.append("\n**题注对齐问题位置**:\n")
                md_content.append(
                    "| 序号 | 段落 | 页码 | 类型 | 对齐方式 | 题注内容 |\n"
                )
                md_content.append(
                    "|------|------|------|------|----------|----------|\n"
                )

                for idx, detail in enumerate(caption_check["details"], 1):
                    alignment_map = {
                        "left": "左对齐",
                        "right": "右对齐",
                        "justify": "两端对齐",
                        "center": "居中",
                    }
                    alignment_text = alignment_map.get(
                        detail["alignment"], detail["alignment"]
                    )
                    md_content.append(
                        f"| {idx} | {detail['paragraph']} | 第 {detail['page']} 页 | {detail['type']} | {alignment_text} | {detail['text']} |\n"
                    )
        else:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {caption_check['message']}\n")
    else:
        md_content.append("⚠️ **状态**: 未检查\n")
        md_content.append("**结果**: 本次检查未包含题注对齐检查\n")

    return "".join(md_content)


def generate_references_report(references_check):
    """生成参考文献检查报告部分。"""
    md_content = []
    md_content.append("\n## 7. 参考文献检查\n")

    if references_check:
        details = references_check.get("details", {})
        if not details:
            details = references_check
        if references_check.get("found"):
            md_content.append("❌ **状态**: 发现问题\n")
            md_content.append(f"**结果**: {references_check['message']}\n")
            if details:
                md_content.append(
                    f"- **参考文献总数**: {references_check.get('total_references', len(details.get('references', [])))}\n"
                )
                md_content.append(
                    f"- **被引用的参考文献数量**: {references_check.get('cited_references', len(details.get('citations', [])))}\n"
                )

                unreferenced_count = references_check.get("unreferenced_count", 0)
                unreferenced = details.get("unreferenced", [])
                if not unreferenced:
                    unreferenced = []
                if isinstance(unreferenced, set):
                    unreferenced = sorted(list(unreferenced))
                elif not isinstance(unreferenced, list):
                    unreferenced = []
                md_content.append(
                    f"- **未被引用的参考文献数量**: {unreferenced_count}\n"
                )

                if unreferenced_count > 0:
                    md_content.append("\n### 未引用参考文献详情\n")
                    if unreferenced and len(unreferenced) > 0:
                        md_content.append(
                            f"共发现 **{len(unreferenced)}** 个未被引用的参考文献：\n\n"
                        )
                        md_content.append("| 参考文献编号 | 参考文献内容 |\n")
                        md_content.append("|-------------|-------------|\n")
                        references_list = details.get("references", [])
                        for ref_num in unreferenced:
                            ref = next(
                                (
                                    r
                                    for r in references_list
                                    if r.get("number") == ref_num
                                ),
                                None,
                            )
                            if ref:
                                ref_text = ref.get("full_text", ref.get("text", ""))
                                if len(ref_text) > 200:
                                    ref_text = ref_text[:200] + "..."
                                md_content.append(f"| {ref_num} | {ref_text} |\n")
                            else:
                                md_content.append(f"| {ref_num} | (未找到详细信息) |\n")
                        md_content.append("\n")
                    else:
                        md_content.append(
                            f"⚠️ 共发现 **{unreferenced_count}** 个未被引用的参考文献，但无法获取详细信息。\n\n"
                        )

                duplicates = details.get("duplicates", [])
                duplicates_count = references_check.get(
                    "duplicates_count", len(duplicates)
                )
                md_content.append(f"- **重复的参考文献组数**: {duplicates_count}\n")

                if duplicates:
                    md_content.append("\n### 重复参考文献详情\n")
                    md_content.append(
                        f"共发现 **{len(duplicates)}** 组完全相同的重复参考文献：\n\n"
                    )
                    md_content.append("| 重复组 | 参考文献编号 | 参考文献内容 |\n")
                    md_content.append("|--------|-------------|-------------|\n")
                    for idx, duplicate_pair in enumerate(duplicates, 1):
                        if (
                            isinstance(duplicate_pair, tuple)
                            and len(duplicate_pair) == 2
                        ):
                            ref1, ref2 = duplicate_pair
                            ref1_text = ref1.get("full_text", ref1.get("text", ""))
                            if len(ref1_text) > 200:
                                ref1_text = ref1_text[:200] + "..."
                            ref2_text = ref2.get("full_text", ref2.get("text", ""))
                            if len(ref2_text) > 200:
                                ref2_text = ref2_text[:200] + "..."
                            md_content.append(
                                f"| {idx} | {ref1.get('number', 'N/A')} | {ref1_text} |\n"
                            )
                            md_content.append(
                                f"| {idx} | {ref2.get('number', 'N/A')} | {ref2_text} |\n"
                            )
                    md_content.append("\n")

                heading_check = details.get("heading_check", {})
                if heading_check:
                    if heading_check.get("is_level1"):
                        md_content.append(
                            "- **参考文献标题级别**: ✅ 正确（一级标题）\n"
                        )
                    else:
                        actual_level = heading_check.get("actual_level", "未知")
                        md_content.append(
                            f"- **参考文献标题级别**: ❌ 不符合要求（当前级别: {actual_level}，应为一级标题）\n"
                        )
        else:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {references_check['message']}\n")
            if details:
                md_content.append(
                    f"- **参考文献总数**: {references_check.get('total_references', len(details.get('references', [])))}\n"
                )
                md_content.append(
                    f"- **被引用的参考文献数量**: {references_check.get('cited_references', len(details.get('citations', [])))}\n"
                )

                unreferenced = details.get("unreferenced", [])
                if isinstance(unreferenced, set):
                    unreferenced = sorted(list(unreferenced))
                elif not isinstance(unreferenced, list):
                    unreferenced = []
                if unreferenced:
                    unreferenced_count = references_check.get(
                        "unreferenced_count", len(unreferenced)
                    )
                    md_content.append(
                        f"- **未被引用的参考文献数量**: {unreferenced_count}\n"
                    )
                    md_content.append("\n### 未引用参考文献详情\n")
                    md_content.append(
                        f"共发现 **{len(unreferenced)}** 个未被引用的参考文献：\n\n"
                    )
                    md_content.append("| 参考文献编号 | 参考文献内容 |\n")
                    md_content.append("|-------------|-------------|\n")
                    references_list = details.get("references", [])
                    for ref_num in unreferenced:
                        ref = next(
                            (r for r in references_list if r.get("number") == ref_num),
                            None,
                        )
                        if ref:
                            ref_text = ref.get("full_text", ref.get("text", ""))
                            if len(ref_text) > 200:
                                ref_text = ref_text[:200] + "..."
                            md_content.append(f"| {ref_num} | {ref_text} |\n")
                    md_content.append("\n")

                duplicates = details.get("duplicates", [])
                if duplicates:
                    duplicates_count = references_check.get(
                        "duplicates_count", len(duplicates)
                    )
                    md_content.append(f"- **重复的参考文献组数**: {duplicates_count}\n")
                    md_content.append("\n### 重复参考文献详情\n")
                    md_content.append(
                        f"共发现 **{len(duplicates)}** 组完全相同的重复参考文献：\n\n"
                    )
                    md_content.append("| 重复组 | 参考文献编号 | 参考文献内容 |\n")
                    md_content.append("|--------|-------------|-------------|\n")
                    for idx, duplicate_pair in enumerate(duplicates, 1):
                        if (
                            isinstance(duplicate_pair, tuple)
                            and len(duplicate_pair) == 2
                        ):
                            ref1, ref2 = duplicate_pair
                            ref1_text = ref1.get("full_text", ref1.get("text", ""))
                            if len(ref1_text) > 200:
                                ref1_text = ref1_text[:200] + "..."
                            ref2_text = ref2.get("full_text", ref2.get("text", ""))
                            if len(ref2_text) > 200:
                                ref2_text = ref2_text[:200] + "..."
                            md_content.append(
                                f"| {idx} | {ref1.get('number', 'N/A')} | {ref1_text} |\n"
                            )
                            md_content.append(
                                f"| {idx} | {ref2.get('number', 'N/A')} | {ref2_text} |\n"
                            )
                    md_content.append("\n")
    else:
        md_content.append("⚠️ **状态**: 未检查\n")
        md_content.append("**结果**: 本次检查未包含参考文献检查\n")

    return "".join(md_content)


def generate_chinese_spacing_report(chinese_spacing_check):
    """生成中文间距检查报告部分。"""
    md_content = []
    md_content.append("\n## 9. 中文间距检查\n")

    if chinese_spacing_check and "found" in chinese_spacing_check:
        if chinese_spacing_check["found"]:
            md_content.append("❌ **状态**: 发现问题\n")
            md_content.append(f"**结果**: {chinese_spacing_check['message']}\n")
            if chinese_spacing_check["details"]:
                md_content.append("\n**中文间距问题位置**:\n")
                md_content.append("| 序号 | 段落 | 页码 | 问题文本 | 上下文 |\n")
                md_content.append("|------|------|------|----------|--------|\n")

                for idx, detail in enumerate(chinese_spacing_check["details"], 1):
                    context = detail.get("context", "")
                    if len(context) > 50:
                        context = context[:47] + "..."
                    md_content.append(
                        f"| {idx} | {detail['paragraph']} | 第 {detail['page']} 页 | {detail['text']} | {context} |\n"
                    )
        else:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {chinese_spacing_check['message']}\n")
    else:
        md_content.append("⚠️ **状态**: 未检查\n")
        md_content.append("**结果**: 本次检查未包含中文间距检查\n")

    return "".join(md_content)


def generate_chinese_quotes_report(chinese_quotes_check):
    """生成中文引号检查报告部分。"""
    md_content = []
    md_content.append("\n## 10. 中文引号检查\n")

    if chinese_quotes_check and "found" in chinese_quotes_check:
        if chinese_quotes_check["found"]:
            md_content.append("❌ **状态**: 发现问题\n")
            md_content.append(f"**结果**: {chinese_quotes_check['message']}\n")
            details = chinese_quotes_check.get("details", {})
            english_quotes = details.get("english_quotes", [])
            quote_matching = details.get("quote_matching", [])

            if english_quotes:
                md_content.append("\n### 英文引号问题\n")
                md_content.append(f"共发现 **{len(english_quotes)}** 处英文引号问题：\n\n")
                md_content.append("| 序号 | 段落 | 类型 | 问题文本 | 上下文 |\n")
                md_content.append("|------|------|------|----------|--------|\n")

                for idx, detail in enumerate(english_quotes, 1):
                    text = detail.get("text", "")
                    if len(text) > 50:
                        text = text[:47] + "..."
                    context = detail.get("context", "")
                    # 限制上下文为20个中文字符
                    # 找到问题文本在上下文中的位置
                    problem_text = detail.get("text", "")
                    if problem_text in context:
                        text_pos = context.find(problem_text)
                        # 在问题文本前后各取约10个中文字符
                        before_text = context[:text_pos]
                        after_text = context[text_pos + len(problem_text):]
                        
                        # 从后往前取，直到达到10个中文字符
                        chinese_count_before = 0
                        before_limited = ""
                        for char in reversed(before_text):
                            if '\u4e00' <= char <= '\u9fff':
                                chinese_count_before += 1
                            before_limited = char + before_limited
                            if chinese_count_before >= 10:
                                break
                        
                        # 从前往后取，直到达到10个中文字符
                        chinese_count_after = 0
                        after_limited = ""
                        for char in after_text:
                            if '\u4e00' <= char <= '\u9fff':
                                chinese_count_after += 1
                            after_limited += char
                            if chinese_count_after >= 10:
                                break
                        
                        context_limited = before_limited + problem_text + after_limited
                        if len(before_limited) < len(before_text):
                            context_limited = "..." + context_limited
                        if len(after_limited) < len(after_text):
                            context_limited = context_limited + "..."
                    else:
                        # 如果找不到问题文本，直接限制整个上下文
                        chinese_count = 0
                        context_limited = ""
                        for char in context:
                            if '\u4e00' <= char <= '\u9fff':
                                chinese_count += 1
                            context_limited += char
                            if chinese_count >= 20:
                                break
                        if len(context_limited) < len(context):
                            context_limited += "..."
                    
                    md_content.append(
                        f"| {idx} | {detail['paragraph']} | 中文使用了英文引号 | {text} | {context_limited} |\n"
                    )

            if quote_matching:
                md_content.append("\n### 引号匹配问题\n")
                md_content.append(f"共发现 **{len(quote_matching)}** 处引号匹配问题：\n\n")
                md_content.append("| 序号 | 段落 | 类型 | 问题文本 | 上下文 |\n")
                md_content.append("|------|------|------|----------|--------|\n")

                for idx, detail in enumerate(quote_matching, 1):
                    context = detail.get('context', detail.get('text', ''))
                    # 不要截断上下文，保留完整内容以便正确提取问题文本
                    # if len(context) > 50:
                    #     context = context[:47] + "..."
                    # 提取问题文本：只显示引号及其直接包含的内容
                    problem_text = ""
                    quote_type = detail.get('quote_type', '')
                    if quote_type:
                        left_quote = quote_type[0] if len(quote_type) > 0 else ''
                        right_quote = quote_type[1] if len(quote_type) > 1 else ''
                        
                        # 查找上下文中的所有引号位置（包括Unicode和ASCII引号）
                        # 支持多种引号字符
                        all_quotes = []
                        quote_chars = [left_quote, right_quote, '"', '"', '\u201c', '\u201d', '\u2018', '\u2019']
                        for i, char in enumerate(context):
                            if char in quote_chars:
                                all_quotes.append((i, char))
                        
                        if all_quotes:
                            # 找到所有引号对，选择包含中文且最短的那个
                            left_quote_chars = [left_quote, '\u201c', '\u2018', '"']
                            right_quote_chars = [right_quote, '\u201d', '\u2019', '"']
                            
                            # 找到所有可能的引号对
                            quote_pairs = []
                            for i, (left_pos, left_char) in enumerate(all_quotes):
                                if left_char in left_quote_chars:
                                    # 找到这个左引号后的第一个右引号
                                    for right_pos, right_char in all_quotes[i+1:]:
                                        if right_char in right_quote_chars:
                                            quote_pairs.append((left_pos, right_pos))
                                            break
                            
                            # 选择包含中文且最短的引号对
                            if quote_pairs:
                                # 先筛选出包含中文的引号对
                                chinese_pairs = []
                                for left_pos, right_pos in quote_pairs:
                                    text_between = context[left_pos:right_pos + 1]
                                    if any('\u4e00' <= c <= '\u9fff' for c in text_between):
                                        chinese_pairs.append((left_pos, right_pos))
                                
                                if chinese_pairs:
                                    # 从包含中文的引号对中选择最短的
                                    best_pair = min(chinese_pairs, key=lambda p: p[1] - p[0] + 1)
                                    left_pos, right_pos = best_pair
                                    problem_text = context[left_pos:right_pos + 1]
                                else:
                                    # 如果没有包含中文的引号对，选择最短的引号对
                                    shortest_pair = min(quote_pairs, key=lambda p: p[1] - p[0] + 1)
                                    left_pos, right_pos = shortest_pair
                                    problem_text = context[left_pos:right_pos + 1]
                            else:
                                # 没有找到匹配的引号对，只显示第一个引号
                                if all_quotes:
                                    first_pos, first_char = all_quotes[0]
                                    problem_text = context[first_pos:first_pos + 1]
                    
                    if not problem_text:
                        problem_text = context[:30] + "..." if len(context) > 30 else context
                    md_content.append(
                        f"| {idx} | {detail['paragraph']} | 左右引号不匹配 | {problem_text} | {context} |\n"
                    )
        else:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {chinese_quotes_check['message']}\n")
    else:
        md_content.append("⚠️ **状态**: 未检查\n")
        md_content.append("**结果**: 本次检查未包含中文引号检查\n")

    return "".join(md_content)


def generate_summary_report(
    checks_to_run,
    header_consistency,
    footer_consistency,
    empty_lines_check,
    figure_check,
    caption_check,
    references_check,
    chinese_spacing_check=None,
    chinese_quotes_check=None,
):
    """生成检查总结报告部分。"""
    md_content = []
    md_content.append("\n---\n")
    md_content.append("\n## 8. 检查总结\n")

    # Build summary table only for checks that were actually executed
    md_content.append("| 检查项 | 状态 |\n")
    md_content.append("|--------|------|\n")

    issues = []

    if checks_to_run is None or "headers" in checks_to_run or "all" in checks_to_run:
        header_status = (
            "✅ 通过"
            if (header_consistency and header_consistency.get("consistent"))
            else (
                "❌ 失败"
                if (header_consistency and "consistent" in header_consistency)
                else "⚠️ 未检查"
            )
        )
        md_content.append(f"| 页眉一致性 | {header_status} |\n")
        if (
            header_consistency
            and "consistent" in header_consistency
            and not header_consistency["consistent"]
        ):
            issues.append(f"**页眉**: {header_consistency['message']}")

    if checks_to_run is None or "footers" in checks_to_run or "all" in checks_to_run:
        footer_status = (
            "✅ 通过"
            if (footer_consistency and footer_consistency.get("consistent"))
            else (
                "❌ 失败"
                if (footer_consistency and "consistent" in footer_consistency)
                else "⚠️ 未检查"
            )
        )
        md_content.append(f"| 页脚一致性 | {footer_status} |\n")
        if (
            footer_consistency
            and "consistent" in footer_consistency
            and not footer_consistency["consistent"]
        ):
            issues.append(f"**页脚**: {footer_consistency['message']}")

    if (
        checks_to_run is None
        or "empty_lines" in checks_to_run
        or "all" in checks_to_run
    ):
        empty_lines_status = (
            "✅ 通过"
            if (empty_lines_check and not empty_lines_check.get("found", False))
            else (
                "❌ 失败"
                if (empty_lines_check and "found" in empty_lines_check)
                else "⚠️ 未检查"
            )
        )
        md_content.append(f"| 连续空行检查 | {empty_lines_status} |\n")
        if empty_lines_check and empty_lines_check.get("found"):
            issues.append(f"**连续空行**: {empty_lines_check['message']}")

    if checks_to_run is None or "figures" in checks_to_run or "all" in checks_to_run:
        figure_status = (
            "✅ 通过"
            if (figure_check and not figure_check.get("found", False))
            else (
                "❌ 失败" if (figure_check and "found" in figure_check) else "⚠️ 未检查"
            )
        )
        md_content.append(f"| 图表前后空行检查 | {figure_status} |\n")
        if figure_check and figure_check.get("found"):
            issues.append(f"**图表前后空行**: {figure_check['message']}")

    if checks_to_run is None or "captions" in checks_to_run or "all" in checks_to_run:
        caption_status = (
            "✅ 通过"
            if (caption_check and not caption_check.get("found", False))
            else (
                "❌ 失败"
                if (caption_check and "found" in caption_check)
                else "⚠️ 未检查"
            )
        )
        md_content.append(f"| 题注对齐检查 | {caption_status} |\n")
        if caption_check and caption_check.get("found"):
            issues.append(f"**题注对齐**: {caption_check['message']}")

    if checks_to_run is None or "references" in checks_to_run or "all" in checks_to_run:
        references_status = (
            "✅ 通过"
            if (references_check and not references_check.get("found", False))
            else (
                "❌ 失败"
                if (references_check and "found" in references_check)
                else "⚠️ 未检查"
            )
        )
        md_content.append(f"| 参考文献检查 | {references_status} |\n")
        if references_check and references_check.get("found"):
            issues.append(f"**参考文献**: {references_check['message']}")

    if checks_to_run is None or "chinese_spacing" in checks_to_run or "all" in checks_to_run:
        chinese_spacing_status = (
            "✅ 通过"
            if (chinese_spacing_check and not chinese_spacing_check.get("found", False))
            else (
                "❌ 失败"
                if (chinese_spacing_check and "found" in chinese_spacing_check)
                else "⚠️ 未检查"
            )
        )
        md_content.append(f"| 中文间距检查 | {chinese_spacing_status} |\n")
        if chinese_spacing_check and chinese_spacing_check.get("found"):
            issues.append(f"**中文间距**: {chinese_spacing_check['message']}")

    if checks_to_run is None or "chinese_quotes" in checks_to_run or "all" in checks_to_run:
        chinese_quotes_status = (
            "✅ 通过"
            if (chinese_quotes_check and not chinese_quotes_check.get("found", False))
            else (
                "❌ 失败"
                if (chinese_quotes_check and "found" in chinese_quotes_check)
                else "⚠️ 未检查"
            )
        )
        md_content.append(f"| 中文引号检查 | {chinese_quotes_status} |\n")
        if chinese_quotes_check and chinese_quotes_check.get("found"):
            issues.append(f"**中文引号**: {chinese_quotes_check['message']}")

    if issues:
        md_content.append("\n### 发现的问题\n")
        for issue in issues:
            md_content.append(f"- {issue}\n")
    else:
        md_content.append("\n✅ **所有格式检查通过！**\n")

    md_content.append("\n---\n")
    md_content.append("\n*报告由文档格式检查脚本自动生成*\n")

    return "".join(md_content)


def generate_markdown_report(
    docx_path,
    structure,
    headers,
    footers,
    header_consistency,
    footer_consistency,
    empty_lines_check,
    figure_check,
    caption_check,
    references_check=None,
    chinese_spacing_check=None,
    chinese_quotes_check=None,
    checks_to_run=None,
):
    """生成完整的文档格式检查报告。

    主函数只负责组合各个独立的报告部分，每个检查项的报告生成逻辑互不影响。

    Args:
        checks_to_run: List of check names that were actually executed. If None, includes all sections.
    """
    docx_name = docx_path.name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_content = []
    md_content.append("# 文档格式检查报告\n")
    md_content.append(f"**文档名称**: {docx_name}\n")
    md_content.append(f"**检查时间**: {timestamp}\n")
    md_content.append("\n---\n")

    # 根据实际执行的检查项，组合相应的报告部分
    # 每个检查项的报告生成函数都是独立的，互不影响

    # 文档结构分析（仅在检查页眉或页脚时包含）
    if checks_to_run is None or any(
        check in checks_to_run for check in ["headers", "footers", "all"]
    ):
        md_content.append(generate_structure_report(structure))

    # 页眉检查
    if checks_to_run is None or "headers" in checks_to_run or "all" in checks_to_run:
        md_content.append(generate_headers_report(headers, header_consistency))

    # 页脚检查
    if checks_to_run is None or "footers" in checks_to_run or "all" in checks_to_run:
        md_content.append(generate_footers_report(footers, footer_consistency))

    # 连续空行检查
    if (
        checks_to_run is None
        or "empty_lines" in checks_to_run
        or "all" in checks_to_run
    ):
        md_content.append(generate_empty_lines_report(empty_lines_check))

    # 图表前后空行检查
    if checks_to_run is None or "figures" in checks_to_run or "all" in checks_to_run:
        md_content.append(generate_figures_report(figure_check))

    # 题注对齐检查
    if checks_to_run is None or "captions" in checks_to_run or "all" in checks_to_run:
        md_content.append(generate_captions_report(caption_check))

    # 参考文献检查
    if checks_to_run is None or "references" in checks_to_run or "all" in checks_to_run:
        md_content.append(generate_references_report(references_check))

    # 中文间距检查
    if checks_to_run is None or "chinese_spacing" in checks_to_run or "all" in checks_to_run:
        md_content.append(generate_chinese_spacing_report(chinese_spacing_check))

    # 中文引号检查
    if checks_to_run is None or "chinese_quotes" in checks_to_run or "all" in checks_to_run:
        md_content.append(generate_chinese_quotes_report(chinese_quotes_check))

    # 检查总结（已移除）
    # md_content.append(
    #     generate_summary_report(
    #         checks_to_run,
    #         header_consistency,
    #         footer_consistency,
    #         empty_lines_check,
    #         figure_check,
    #         caption_check,
    #         references_check,
    #         chinese_spacing_check,
    #         chinese_quotes_check,
    #     )
    # )

    return "".join(md_content)
