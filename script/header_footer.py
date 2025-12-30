#!/usr/bin/env python3
"""
Header and footer checking functions.
"""

import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from utils import extract_text_from_xml, estimate_page_from_paragraph


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

