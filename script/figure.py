#!/usr/bin/env python3
"""
Figure and caption checking functions.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
from collections import defaultdict
from utils import estimate_page_from_paragraph


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


def check_caption_alignment(docx_path, required_alignment=None):
    """
    Check if figure and table captions have the required alignment.
    
    Args:
        docx_path: Path to the Word document
        required_alignment: Required alignment (if None, will use default from config)
    
    Returns:
        Dictionary with check results
    """
    if required_alignment is None:
        from config_loader import ConfigLoader
        try:
            config_loader = ConfigLoader()
            config = config_loader.load()
            captions_config = config.get("captions", {})
            figure_config = captions_config.get("figure", {})
            format_config = figure_config.get("format", {})
            required_alignment = format_config.get("alignment", "center")
        except Exception:
            required_alignment = "center"
    
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

                    if alignment != required_alignment:
                        caption_issues.append({
                            'paragraph': para_idx,
                            'page': page,
                            'type': caption_type,
                            'alignment': alignment,
                            'required_alignment': required_alignment,
                            'text': text[:50]
                        })

    except Exception as e:
        return {
            'found': False,
            'message': f'Error checking caption alignment: {e}',
            'details': []
        }

    alignment_map = {
        'center': '居中',
        'left': '左对齐',
        'right': '右对齐',
        'justify': '两端对齐'
    }
    alignment_text = alignment_map.get(required_alignment, required_alignment)
    
    if caption_issues:
        return {
            'found': True,
            'message': f'Found {len(caption_issues)} caption(s) not {alignment_text}',
            'details': caption_issues
        }
    else:
        return {
            'found': False,
            'message': f'All captions are {alignment_text}',
            'details': []
        }


def check_figure_caption_format(docx_path):
    """Check if figure captions have consistent format."""
    figure_captions = []
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            if 'word/document.xml' not in docx.namelist():
                return {
                    'found': False,
                    'message': 'Document body not found',
                    'details': [],
                    'format_patterns': {}
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
                    'details': [],
                    'format_patterns': {}
                }
            
            paragraphs = body.findall('.//w:p', namespaces)
            
            def get_paragraph_text(para):
                text_elements = para.findall('.//w:t', namespaces)
                return ''.join([t.text for t in text_elements if t.text]).strip()
            
            def is_figure_caption(para):
                """Check if paragraph is a figure caption."""
                text = get_paragraph_text(para)
                if not text:
                    return False
                text_stripped = text.strip()
                if text_stripped.startswith('图') or '图' in text_stripped:
                    pattern = re.match(r'^图\s*[0-9]+', text_stripped)
                    if pattern:
                        return True
                return False
            
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
            
            def extract_caption_pattern(text):
                """Extract the format pattern from caption text."""
                text_stripped = text.strip()
                match = re.match(r'^(图\s*)([0-9]+)([-.]?)([0-9]*)(.*)$', text_stripped)
                if match:
                    prefix = match.group(1)
                    num1 = match.group(2)
                    separator = match.group(3)
                    num2 = match.group(4)
                    suffix = match.group(5)
                    
                    has_space = ' ' in prefix or prefix.endswith(' ')
                    has_separator = bool(separator)
                    has_second_num = bool(num2)
                    
                    if has_second_num:
                        if separator == '-':
                            pattern = f"图{' ' if has_space else ''}{num1}-{num2}"
                        elif separator == '.':
                            pattern = f"图{' ' if has_space else ''}{num1}.{num2}"
                        else:
                            pattern = f"图{' ' if has_space else ''}{num1}{num2}"
                    else:
                        pattern = f"图{' ' if has_space else ''}{num1}"
                    
                    return pattern, text_stripped
                return None, text_stripped
            
            for para_idx, para in enumerate(paragraphs, 1):
                if is_in_table_cell(para):
                    continue
                
                if is_figure_caption(para):
                    text = get_paragraph_text(para)
                    pattern, full_text = extract_caption_pattern(text)
                    total_paras = len(paragraphs)
                    page = estimate_page_from_paragraph(para_idx, total_paras)
                    
                    figure_captions.append({
                        'paragraph': para_idx,
                        'page': page,
                        'text': full_text,
                        'pattern': pattern
                    })
    
    except Exception as e:
        return {
            'found': False,
            'message': f'Error checking figure caption format: {e}',
            'details': [],
            'format_patterns': {}
        }
    
    if not figure_captions:
        return {
            'found': False,
            'message': 'No figure captions found',
            'details': [],
            'format_patterns': {}
        }
    
    pattern_counts = defaultdict(list)
    for caption in figure_captions:
        pattern_counts[caption['pattern']].append(caption)
    
    if len(pattern_counts) == 1:
        return {
            'found': False,
            'message': f'All {len(figure_captions)} figure caption(s) have consistent format',
            'details': [],
            'format_patterns': dict(pattern_counts)
        }
    
    most_common_pattern = max(pattern_counts.items(), key=lambda x: len(x[1]))[0]
    inconsistent_captions = []
    
    for pattern, captions in pattern_counts.items():
        if pattern != most_common_pattern:
            inconsistent_captions.extend(captions)
    
    return {
        'found': True,
        'message': f'Found {len(inconsistent_captions)} figure caption(s) with inconsistent format (out of {len(figure_captions)} total)',
        'details': inconsistent_captions,
        'format_patterns': dict(pattern_counts),
        'most_common_pattern': most_common_pattern
    }

