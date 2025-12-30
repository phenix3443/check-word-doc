#!/usr/bin/env python3
"""
Script to check Word document format consistency, especially headers.
"""

import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import sys
from datetime import datetime

def extract_text_from_xml(xml_content):
    """Extract text content from Word XML, handling namespaces."""
    try:
        root = ET.fromstring(xml_content)

        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        text_elements = []

        for t in root.findall('.//w:t', namespaces):
            if t.text:
                text_elements.append(t.text)

        if not text_elements:
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    text_elements.append(elem.text.strip())

        return ' '.join(text_elements)
    except Exception:
        return None

def analyze_header_footer_usage(docx_path):
    """Analyze which sections use which headers/footers and estimate page ranges."""
    usage_info = {
        'headers': {},
        'footers': {},
        'sections': []
    }

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            if 'word/document.xml' not in docx.namelist():
                return usage_info

            document_xml = docx.read('word/document.xml')
            root = ET.fromstring(document_xml)

            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            }

            rels_map = {}
            if 'word/_rels/document.xml.rels' in docx.namelist():
                try:
                    rels_xml = docx.read('word/_rels/document.xml.rels')
                    rels_root = ET.fromstring(rels_xml)
                    for rel in rels_root:
                        rel_id = rel.get('Id')
                        target = rel.get('Target')
                        if target and rel_id:
                            normalized_target = target
                            if not normalized_target.startswith('word/'):
                                normalized_target = 'word/' + normalized_target
                            if 'header' in normalized_target.lower():
                                rels_map[rel_id] = ('header', normalized_target)
                            elif 'footer' in normalized_target.lower():
                                rels_map[rel_id] = ('footer', normalized_target)
                except Exception as e:
                    print(f"Warning: Could not parse relationships: {e}")

            paragraphs = root.findall('.//w:p', namespaces)
            body = root.find('.//w:body', namespaces)

            section_idx = 0
            para_idx = 0
            current_section_start = 1

            all_sect_prs = []

            for para in paragraphs:
                para_idx += 1
                sect_pr = para.find('.//w:sectPr', namespaces)
                if sect_pr is not None:
                    all_sect_prs.append((para_idx, sect_pr))

            if body is not None:
                body_sect_pr = body.find('.//w:sectPr', namespaces)
                if body_sect_pr is not None and len(paragraphs) > 0:
                    all_sect_prs.append((len(paragraphs), body_sect_pr))

            if not all_sect_prs:
                body_sect_pr = root.find('.//w:sectPr', namespaces)
                if body_sect_pr is not None:
                    all_sect_prs.append((len(paragraphs) if paragraphs else 1, body_sect_pr))

            for para_idx, sect_pr in all_sect_prs:
                section_idx += 1
                start_para = current_section_start

                header_refs = sect_pr.findall('.//w:headerReference', namespaces)
                footer_refs = sect_pr.findall('.//w:footerReference', namespaces)

                for header_ref in header_refs:
                    rel_id = None
                    for attr_name, attr_value in header_ref.attrib.items():
                        if 'id' in attr_name.lower() or attr_name.endswith(':id') or attr_name.endswith(':Id'):
                            rel_id = attr_value
                            break
                    if rel_id and rel_id in rels_map:
                        header_type, header_file = rels_map[rel_id]
                        if header_file not in usage_info['headers']:
                            usage_info['headers'][header_file] = []
                        usage_info['headers'][header_file].append({
                            'section': section_idx,
                            'start_para': start_para,
                            'type': header_ref.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type', 'default')
                        })

                for footer_ref in footer_refs:
                    rel_id = None
                    for attr_name, attr_value in footer_ref.attrib.items():
                        if 'id' in attr_name.lower() or attr_name.endswith(':id') or attr_name.endswith(':Id'):
                            rel_id = attr_value
                            break
                    if rel_id and rel_id in rels_map:
                        footer_type, footer_file = rels_map[rel_id]
                        if footer_file not in usage_info['footers']:
                            usage_info['footers'][footer_file] = []
                        usage_info['footers'][footer_file].append({
                            'section': section_idx,
                            'start_para': start_para,
                            'type': footer_ref.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type', 'default')
                        })

                current_section_start = para_idx + 1

            usage_info['total_paragraphs'] = len(paragraphs)

    except Exception as e:
        print(f"Error analyzing header/footer usage: {e}")

    return usage_info

def estimate_page_from_paragraph(para_num, total_paras):
    """Roughly estimate page number from paragraph number."""
    avg_paras_per_page = 25
    estimated_page = max(1, int(para_num / avg_paras_per_page) + 1)
    return estimated_page

def extract_headers_from_docx(docx_path, usage_info=None):
    """Extract all headers from a .docx file."""
    headers = []
    if usage_info is None:
        usage_info = analyze_header_footer_usage(docx_path)

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            header_files = [f for f in docx.namelist() if 'header' in f.lower() and f.endswith('.xml')]

            for header_file in header_files:
                try:
                    header_xml = docx.read(header_file)
                    header_text = extract_text_from_xml(header_xml)

                    if header_text and header_text.strip():
                        page_info = []
                        if header_file in usage_info['headers']:
                            for usage in usage_info['headers'][header_file]:
                                start_page = estimate_page_from_paragraph(usage['start_para'], usage_info.get('total_paragraphs', 0))
                                page_info.append({
                                    'section': usage['section'],
                                    'start_para': usage['start_para'],
                                    'estimated_start_page': start_page,
                                    'type': usage['type']
                                })

                        headers.append({
                            'file': header_file,
                            'text': header_text.strip(),
                            'raw_xml': header_xml.decode('utf-8', errors='ignore'),
                            'page_info': page_info
                        })
                except Exception as e:
                    print(f"Error reading {header_file}: {e}")
                    continue

    except Exception as e:
        print(f"Error opening docx file: {e}")
        return []

    return headers

def extract_footers_from_docx(docx_path, usage_info=None):
    """Extract all footers from a .docx file."""
    footers = []
    if usage_info is None:
        usage_info = analyze_header_footer_usage(docx_path)

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            footer_files = [f for f in docx.namelist() if 'footer' in f.lower() and f.endswith('.xml')]

            for footer_file in footer_files:
                try:
                    footer_xml = docx.read(footer_file)
                    footer_text = extract_text_from_xml(footer_xml)

                    if footer_text and footer_text.strip():
                        page_info = []
                        if footer_file in usage_info['footers']:
                            for usage in usage_info['footers'][footer_file]:
                                start_page = estimate_page_from_paragraph(usage['start_para'], usage_info.get('total_paragraphs', 0))
                                page_info.append({
                                    'section': usage['section'],
                                    'start_para': usage['start_para'],
                                    'estimated_start_page': start_page,
                                    'type': usage['type']
                                })

                        footers.append({
                            'file': footer_file,
                            'text': footer_text.strip(),
                            'raw_xml': footer_xml.decode('utf-8', errors='ignore'),
                            'page_info': page_info
                        })
                except Exception as e:
                    print(f"Error reading {footer_file}: {e}")
                    continue

    except Exception as e:
        print(f"Error opening docx file: {e}")
        return []

    return footers

def check_consistency(items, item_type='items'):
    """Check if items (headers/footers) are consistent."""
    if not items:
        return {
            'consistent': False,
            'message': f'No {item_type} found in document',
            'details': []
        }

    if len(items) == 1:
        return {
            'consistent': True,
            'message': f'Only one {item_type[:-1]} found',
            'details': items
        }

    item_texts = [item['text'] for item in items]
    unique_items = set(item_texts)

    if len(unique_items) == 1:
        return {
            'consistent': True,
            'message': f'All {item_type} are identical',
            'details': items
        }
    else:
        item_counts = Counter(item_texts)
        return {
            'consistent': False,
            'message': f'Found {len(unique_items)} different {item_type} variations',
            'details': items,
            'variations': dict(item_counts)
        }

def check_header_consistency(headers):
    """Check if headers are consistent."""
    return check_consistency(headers, 'headers')

def check_footer_consistency(footers):
    """Check if footers are consistent."""
    return check_consistency(footers, 'footers')

def check_consecutive_empty_lines(docx_path):
    """Check for consecutive empty lines in document body."""
    consecutive_empty = []

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            if 'word/document.xml' not in docx.namelist():
                return {
                    'found': False,
                    'message': 'Document body not found',
                    'details': []
                }

            document_xml = docx.read('word/document.xml')
            root = ET.fromstring(document_xml)

            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }

            body = root.find('.//w:body', namespaces)
            if body is None:
                return {
                    'found': False,
                    'message': 'Document body not found',
                    'details': []
                }

            paragraphs = body.findall('.//w:p', namespaces)

            def is_in_table_cell(para):
                """Check if paragraph is inside a table cell."""
                path_parts = []
                current = para
                for _ in range(20):
                    found_parent = False
                    for elem in body.iter():
                        if current in list(elem):
                            path_parts.append(elem.tag)
                            if elem.tag.endswith('}tc'):
                                return True
                            current = elem
                            found_parent = True
                            break
                    if not found_parent:
                        break
                return False

            def get_paragraph_text(para):
                text_elements = para.findall('.//w:t', namespaces)
                return ''.join([t.text for t in text_elements if t.text]).strip()

            def get_context_text(para_idx, paragraphs, before_count=3, after_count=3):
                context_before = []
                context_after = []

                for i in range(max(0, para_idx - before_count - 1), para_idx - 1):
                    if i >= 0 and i < len(paragraphs):
                        text = get_paragraph_text(paragraphs[i])
                        if text and len(text) > 5:
                            context_before.append(text[:150])

                for i in range(para_idx, min(len(paragraphs), para_idx + after_count)):
                    if i < len(paragraphs):
                        text = get_paragraph_text(paragraphs[i])
                        if text and len(text) > 5:
                            context_after.append(text[:150])

                return context_before[-2:], context_after[:2]

            empty_count = 0
            start_paragraph = None

            for para_idx, para in enumerate(paragraphs, 1):
                if is_in_table_cell(para):
                    if empty_count >= 2:
                        empty_count = 0
                        start_paragraph = None
                    continue
                
                para_text = get_paragraph_text(para)

                if not para_text:
                    if empty_count == 0:
                        start_paragraph = para_idx
                    empty_count += 1
                else:
                    if empty_count >= 2:
                        total_paras = len(paragraphs)
                        start_page = estimate_page_from_paragraph(start_paragraph, total_paras)
                        end_page = estimate_page_from_paragraph(para_idx - 1, total_paras)

                        context_before, context_after = get_context_text(start_paragraph, paragraphs)

                        consecutive_empty.append({
                            'start': start_paragraph,
                            'end': para_idx - 1,
                            'count': empty_count,
                            'estimated_start_page': start_page,
                            'estimated_end_page': end_page,
                            'context_before': context_before,
                            'context_after': context_after
                        })
                    empty_count = 0
                    start_paragraph = None

            if empty_count >= 2:
                total_paras = len(paragraphs)
                start_page = estimate_page_from_paragraph(start_paragraph, total_paras)
                end_page = estimate_page_from_paragraph(len(paragraphs), total_paras)

                context_before, context_after = get_context_text(start_paragraph, paragraphs)

                consecutive_empty.append({
                    'start': start_paragraph,
                    'end': len(paragraphs),
                    'count': empty_count,
                    'estimated_start_page': start_page,
                    'estimated_end_page': end_page,
                    'context_before': context_before,
                    'context_after': context_after
                })

    except Exception as e:
        return {
            'found': False,
            'message': f'Error checking empty lines: {e}',
            'details': []
        }

    if consecutive_empty:
        return {
            'found': True,
            'message': f'Found {len(consecutive_empty)} group(s) of consecutive empty lines',
            'details': consecutive_empty,
            'total_paragraphs': len(paragraphs) if 'paragraphs' in locals() else 0
        }
    else:
        return {
            'found': False,
            'message': 'No consecutive empty lines found',
            'details': [],
            'total_paragraphs': len(paragraphs) if 'paragraphs' in locals() else 0
        }

def check_figure_empty_lines(docx_path):
    """Check for empty lines before and after figures/images."""
    figure_issues = []

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            if 'word/document.xml' not in docx.namelist():
                return {
                    'found': False,
                    'message': 'Document body not found',
                    'details': []
                }

            document_xml = docx.read('word/document.xml')
            root = ET.fromstring(document_xml)

            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }

            body = root.find('.//w:body', namespaces)
            if body is None:
                return {
                    'found': False,
                    'message': 'Document body not found',
                    'details': []
                }

            paragraphs = body.findall('.//w:p', namespaces)

            def has_figure(para):
                """Check if paragraph contains a figure/image."""
                if para.find('.//w:drawing', namespaces) is not None:
                    return True
                if para.find('.//w:pict', namespaces) is not None:
                    return True
                return False

            def get_paragraph_text(para):
                text_elements = para.findall('.//w:t', namespaces)
                return ''.join([t.text for t in text_elements if t.text]).strip()

            def is_in_table_cell(para):
                """Check if paragraph is inside a table cell."""
                current = para
                for _ in range(20):
                    found_parent = False
                    for elem in body.iter():
                        if current in list(elem):
                            if elem.tag.endswith('}tc'):
                                return True
                            current = elem
                            found_parent = True
                            break
                    if not found_parent:
                        break
                return False

            for para_idx, para in enumerate(paragraphs, 1):
                if is_in_table_cell(para):
                    continue

                if has_figure(para):
                    total_paras = len(paragraphs)
                    page = estimate_page_from_paragraph(para_idx, total_paras)

                    before_empty = False
                    after_empty = False

                    if para_idx > 1:
                        prev_para = paragraphs[para_idx - 2]
                        if not is_in_table_cell(prev_para):
                            prev_text = get_paragraph_text(prev_para)
                            if not prev_text:
                                before_empty = True

                    if para_idx < len(paragraphs):
                        next_para = paragraphs[para_idx]
                        if not is_in_table_cell(next_para):
                            next_text = get_paragraph_text(next_para)
                            if not next_text:
                                after_empty = True

                    if before_empty or after_empty:
                        figure_issues.append({
                            'paragraph': para_idx,
                            'page': page,
                            'before_empty': before_empty,
                            'after_empty': after_empty
                        })

    except Exception as e:
        return {
            'found': False,
            'message': f'Error checking figure empty lines: {e}',
            'details': []
        }

    if figure_issues:
        return {
            'found': True,
            'message': f'Found {len(figure_issues)} figure(s) with empty lines before or after',
            'details': figure_issues
        }
    else:
        return {
            'found': False,
            'message': 'No figures with empty lines before or after found',
            'details': []
        }

def check_caption_alignment(docx_path):
    """Check if figure and table captions are centered."""
    caption_issues = []

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            if 'word/document.xml' not in docx.namelist():
                return {
                    'found': False,
                    'message': 'Document body not found',
                    'details': []
                }

            document_xml = docx.read('word/document.xml')
            root = ET.fromstring(document_xml)

            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }

            body = root.find('.//w:body', namespaces)
            if body is None:
                return {
                    'found': False,
                    'message': 'Document body not found',
                    'details': []
                }

            paragraphs = body.findall('.//w:p', namespaces)

            def get_paragraph_text(para):
                text_elements = para.findall('.//w:t', namespaces)
                return ''.join([t.text for t in text_elements if t.text]).strip()

            def is_caption(para):
                """Check if paragraph is a caption (contains 图 or 表)."""
                text = get_paragraph_text(para)
                if not text:
                    return False, None
                if '图' in text and ('图 ' in text or text.startswith('图')):
                    return True, '图'
                if '表' in text and ('表 ' in text or text.startswith('表')):
                    return True, '表'
                return False, None

            def get_alignment(para):
                """Get paragraph alignment."""
                pPr = para.find('.//w:pPr', namespaces)
                if pPr is not None:
                    jc = pPr.find('.//w:jc', namespaces)
                    if jc is not None:
                        val = jc.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                        if val == 'center':
                            return 'center'
                        elif val == 'left':
                            return 'left'
                        elif val == 'right':
                            return 'right'
                        elif val == 'both':
                            return 'justify'
                return 'left'

            def is_in_table_cell(para):
                """Check if paragraph is inside a table cell."""
                current = para
                for _ in range(20):
                    found_parent = False
                    for elem in body.iter():
                        if current in list(elem):
                            if elem.tag.endswith('}tc'):
                                return True
                            current = elem
                            found_parent = True
                            break
                    if not found_parent:
                        break
                return False

            for para_idx, para in enumerate(paragraphs, 1):
                if is_in_table_cell(para):
                    continue

                is_cap, caption_type = is_caption(para)
                if is_cap:
                    alignment = get_alignment(para)
                    total_paras = len(paragraphs)
                    page = estimate_page_from_paragraph(para_idx, total_paras)
                    text = get_paragraph_text(para)

                    if alignment != 'center':
                        caption_issues.append({
                            'paragraph': para_idx,
                            'page': page,
                            'type': caption_type,
                            'alignment': alignment,
                            'text': text[:50]
                        })

    except Exception as e:
        return {
            'found': False,
            'message': f'Error checking caption alignment: {e}',
            'details': []
        }

    if caption_issues:
        return {
            'found': True,
            'message': f'Found {len(caption_issues)} caption(s) not centered',
            'details': caption_issues
        }
    else:
        return {
            'found': False,
            'message': 'All captions are centered',
            'details': []
        }

def analyze_document_structure(docx_path):
    """Analyze the overall structure of the document."""
    structure = {
        'headers': [],
        'footers': [],
        'sections': []
    }

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            file_list = docx.namelist()

            structure['headers'] = [f for f in file_list if 'header' in f.lower() and f.endswith('.xml')]
            structure['footers'] = [f for f in file_list if 'footer' in f.lower() and f.endswith('.xml')]
            structure['sections'] = [f for f in file_list if 'word/section' in f.lower() or 'document.xml' in f]

    except Exception as e:
        print(f"Error analyzing document structure: {e}")

    return structure

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

def main():
    docx_path = Path('/Users/liushangliang/nuts/我的坚果云/idea/yanshou/项目验收-22年项目-科技报告-20251229-v2.docx')

    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        sys.exit(1)

    print("=" * 80)
    print(f"Checking document format: {docx_path.name}")
    print("=" * 80)
    print()

    print("1. Analyzing document structure...")
    structure = analyze_document_structure(docx_path)
    print(f"   Found {len(structure['headers'])} header file(s)")
    print(f"   Found {len(structure['footers'])} footer file(s)")
    print()

    print("2. Analyzing header/footer usage...")
    usage_info = analyze_header_footer_usage(docx_path)
    print()

    print("3. Extracting headers...")
    headers = extract_headers_from_docx(docx_path, usage_info)
    print(f"   Extracted {len(headers)} header(s) with content")
    print()

    if headers:
        print("   Header details:")
        for i, header in enumerate(headers, 1):
            print(f"   Header {i} ({header['file']}):")
            print(f"      Content: {header['text'][:100]}..." if len(header['text']) > 100 else f"      Content: {header['text']}")
            if header.get('page_info'):
                page_ranges = []
                for info in header['page_info']:
                    page_ranges.append(f"Page ~{info['estimated_start_page']} (Section {info['section']}, Para {info['start_para']})")
                if page_ranges:
                    print(f"      Location: {', '.join(page_ranges)}")
            print()

    print("4. Checking header consistency...")
    consistency = check_header_consistency(headers)
    print(f"   Result: {consistency['message']}")

    if not consistency['consistent']:
        print()
        print("   WARNING: Headers are not consistent!")
        if 'variations' in consistency:
            print("   Header variations found:")
            for header_text, count in consistency['variations'].items():
                print(f"      - '{header_text[:80]}...' (appears {count} time(s))" if len(header_text) > 80 else f"      - '{header_text}' (appears {count} time(s))")
    else:
        print("   ✓ Headers are consistent")

    print()
    print("5. Extracting footers...")
    footers = extract_footers_from_docx(docx_path, usage_info)
    print(f"   Extracted {len(footers)} footer(s) with content")
    print()

    if footers:
        print("   Footer details:")
        for i, footer in enumerate(footers, 1):
            print(f"   Footer {i} ({footer['file']}):")
            print(f"      Content: {footer['text'][:100]}..." if len(footer['text']) > 100 else f"      Content: {footer['text']}")
            if footer.get('page_info'):
                page_ranges = []
                for info in footer['page_info']:
                    page_ranges.append(f"Page ~{info['estimated_start_page']} (Section {info['section']}, Para {info['start_para']})")
                if page_ranges:
                    print(f"      Location: {', '.join(page_ranges)}")
            print()

    print("6. Checking footer consistency...")
    footer_consistency = check_footer_consistency(footers)
    print(f"   Result: {footer_consistency['message']}")

    if not footer_consistency['consistent']:
        print()
        print("   WARNING: Footers are not consistent!")
        if 'variations' in footer_consistency:
            print("   Footer variations found:")
            for footer_text, count in footer_consistency['variations'].items():
                print(f"      - '{footer_text[:80]}...' (appears {count} time(s))" if len(footer_text) > 80 else f"      - '{footer_text}' (appears {count} time(s))")
    else:
        print("   ✓ Footers are consistent")

    print()
    print("7. Checking for consecutive empty lines...")
    empty_lines_check = check_consecutive_empty_lines(docx_path)
    print(f"   Result: {empty_lines_check['message']}")

    if empty_lines_check['found']:
        print()
        print("   WARNING: Consecutive empty lines found!")
        if empty_lines_check['details']:
            details = empty_lines_check['details']
            print(f"   Found {len(details)} group(s) of consecutive empty lines")
            if len(details) > 20:
                print("   First 10 locations:")
                for detail in details[:10]:
                    page_info = ""
                    if 'estimated_start_page' in detail and 'estimated_end_page' in detail:
                        if detail['estimated_start_page'] == detail['estimated_end_page']:
                            page_info = f" (Page ~{detail['estimated_start_page']})"
                        else:
                            page_info = f" (Pages ~{detail['estimated_start_page']}-{detail['estimated_end_page']})"
                    print(f"      - Paragraphs {detail['start']} to {detail['end']}: {detail['count']} consecutive empty lines{page_info}")
                print("   ...")
                print("   Last 10 locations:")
                for detail in details[-10:]:
                    page_info = ""
                    if 'estimated_start_page' in detail and 'estimated_end_page' in detail:
                        if detail['estimated_start_page'] == detail['estimated_end_page']:
                            page_info = f" (Page ~{detail['estimated_start_page']})"
                        else:
                            page_info = f" (Pages ~{detail['estimated_start_page']}-{detail['estimated_end_page']})"
                    print(f"      - Paragraphs {detail['start']} to {detail['end']}: {detail['count']} consecutive empty lines{page_info}")
            else:
                print("   Locations:")
                for detail in details:
                    page_info = ""
                    if 'estimated_start_page' in detail and 'estimated_end_page' in detail:
                        if detail['estimated_start_page'] == detail['estimated_end_page']:
                            page_info = f" (Page ~{detail['estimated_start_page']})"
                        else:
                            page_info = f" (Pages ~{detail['estimated_start_page']}-{detail['estimated_end_page']})"
                    print(f"      - Paragraphs {detail['start']} to {detail['end']}: {detail['count']} consecutive empty lines{page_info}")
    else:
        print("   ✓ No consecutive empty lines found")

    if 'total_paragraphs' in empty_lines_check:
        print(f"   Total paragraphs in document: {empty_lines_check['total_paragraphs']}")

    print()
    print("8. Checking figure empty lines...")
    figure_check = check_figure_empty_lines(docx_path)
    print(f"   Result: {figure_check['message']}")

    if figure_check['found']:
        print()
        print("   WARNING: Figures with empty lines before or after found!")
        if figure_check['details']:
            details = figure_check['details']
            print(f"   Found {len(details)} figure(s) with empty lines")
            if len(details) > 20:
                print("   First 10 locations:")
                for detail in details[:10]:
                    before = "Yes" if detail['before_empty'] else "No"
                    after = "Yes" if detail['after_empty'] else "No"
                    print(f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): Before={before}, After={after}")
                print("   ...")
            else:
                print("   Locations:")
                for detail in details:
                    before = "Yes" if detail['before_empty'] else "No"
                    after = "Yes" if detail['after_empty'] else "No"
                    print(f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): Before={before}, After={after}")
    else:
        print("   ✓ No figures with empty lines before or after found")

    print()
    print("9. Checking caption alignment...")
    caption_check = check_caption_alignment(docx_path)
    print(f"   Result: {caption_check['message']}")

    if caption_check['found']:
        print()
        print("   WARNING: Captions not centered found!")
        if caption_check['details']:
            details = caption_check['details']
            print(f"   Found {len(details)} caption(s) not centered")
            if len(details) > 20:
                print("   First 10 locations:")
                for detail in details[:10]:
                    alignment_map = {
                        'left': 'Left',
                        'right': 'Right',
                        'justify': 'Justify',
                        'center': 'Center'
                    }
                    alignment_text = alignment_map.get(detail['alignment'], detail['alignment'])
                    print(f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['type']} - {alignment_text}")
                print("   ...")
            else:
                print("   Locations:")
                for detail in details:
                    alignment_map = {
                        'left': 'Left',
                        'right': 'Right',
                        'justify': 'Justify',
                        'center': 'Center'
                    }
                    alignment_text = alignment_map.get(detail['alignment'], detail['alignment'])
                    print(f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['type']} - {alignment_text}")
    else:
        print("   ✓ All captions are centered")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Header consistency: {'✓ PASS' if consistency['consistent'] else '✗ FAIL'}")
    print(f"Footer consistency: {'✓ PASS' if footer_consistency['consistent'] else '✗ FAIL'}")
    print(f"Consecutive empty lines: {'✓ PASS' if not empty_lines_check['found'] else '✗ FAIL'}")
    print(f"Figure empty lines: {'✓ PASS' if not figure_check['found'] else '✗ FAIL'}")
    print(f"Caption alignment: {'✓ PASS' if not caption_check['found'] else '✗ FAIL'}")

    issues = []
    if not consistency['consistent']:
        issues.append(f"Headers: {consistency['message']}")
    if not footer_consistency['consistent']:
        issues.append(f"Footers: {footer_consistency['message']}")
    if empty_lines_check['found']:
        issues.append(f"Consecutive empty lines: {empty_lines_check['message']}")
    if figure_check['found']:
        issues.append(f"Figure empty lines: {figure_check['message']}")
    if caption_check['found']:
        issues.append(f"Caption alignment: {caption_check['message']}")

    if issues:
        print()
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print()
        print("✓ All format checks passed!")

    print("=" * 80)

    print()
    print("Generating markdown report...")
    md_report = generate_markdown_report(docx_path, structure, headers, footers, consistency, footer_consistency, empty_lines_check, figure_check, caption_check)

    report_path = docx_path.parent / f"{docx_path.stem}_格式检查报告.md"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        print(f"✓ Markdown report saved to: {report_path}")
    except Exception as e:
        print(f"✗ Error saving markdown report: {e}")

if __name__ == '__main__':
    main()

