#!/usr/bin/env python3
"""
Figure and caption checking functions.
"""

import zipfile
import xml.etree.ElementTree as ET
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

