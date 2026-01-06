#!/usr/bin/env python3
"""
Empty lines checking functions.
"""

import zipfile
import xml.etree.ElementTree as ET
from utils import estimate_page_from_paragraph
from cover import find_first_page_end


def check_consecutive_empty_lines(docx_path, max_consecutive=None):
    """
    Check for consecutive empty lines.

    Args:
        docx_path: Path to the Word document
        max_consecutive: Maximum allowed consecutive empty lines (if None, will use default from config)

    Returns:
        Dictionary with check results
    """
    if max_consecutive is None:
        from config_loader import ConfigLoader

        config_loader = ConfigLoader()
        config = config_loader.load()
        empty_lines_config = config.get("empty_lines", {})
        if not empty_lines_config:
            raise ValueError("Empty lines configuration not found in config file")
        max_consecutive = empty_lines_config.get("max_consecutive")
        if max_consecutive is None:
            raise ValueError("max_consecutive not specified in config file (empty_lines.max_consecutive)")
    """Check for consecutive empty lines in document body."""
    consecutive_empty = []

    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            if "word/document.xml" not in docx.namelist():
                return {
                    "found": False,
                    "message": "Document body not found",
                    "details": [],
                }

            document_xml = docx.read("word/document.xml")
            root = ET.fromstring(document_xml)

            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }

            body = root.find(".//w:body", namespaces)
            if body is None:
                return {
                    "found": False,
                    "message": "Document body not found",
                    "details": [],
                }

            paragraphs = body.findall(".//w:p", namespaces)

            first_page_end = find_first_page_end(paragraphs, namespaces, body)

            def is_in_table_cell(para):
                """Check if paragraph is inside a table cell."""
                path_parts = []
                current = para
                for _ in range(20):
                    found_parent = False
                    for elem in body.iter():
                        if current in list(elem):
                            path_parts.append(elem.tag)
                            if elem.tag.endswith("}tc"):
                                return True
                            current = elem
                            found_parent = True
                            break
                    if not found_parent:
                        break
                return False

            def get_paragraph_text(para):
                text_elements = para.findall(".//w:t", namespaces)
                return "".join([t.text for t in text_elements if t.text]).strip()

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
                para_idx_0based = para_idx - 1

                if para_idx_0based <= first_page_end:
                    if empty_count > max_consecutive:
                        empty_count = 0
                        start_paragraph = None
                    continue

                if is_in_table_cell(para):
                    if empty_count > max_consecutive:
                        empty_count = 0
                        start_paragraph = None
                    continue

                para_text = get_paragraph_text(para)

                if not para_text:
                    if empty_count == 0:
                        start_paragraph = para_idx
                    empty_count += 1
                else:
                    if empty_count > max_consecutive:
                        total_paras = len(paragraphs)
                        start_page = estimate_page_from_paragraph(
                            start_paragraph, total_paras
                        )
                        end_page = estimate_page_from_paragraph(
                            para_idx - 1, total_paras
                        )

                        context_before, context_after = get_context_text(
                            start_paragraph, paragraphs
                        )

                        consecutive_empty.append(
                            {
                                "start": start_paragraph,
                                "end": para_idx - 1,
                                "count": empty_count,
                                "estimated_start_page": start_page,
                                "estimated_end_page": end_page,
                                "context_before": context_before,
                                "context_after": context_after,
                            }
                        )
                    empty_count = 0
                    start_paragraph = None

            if empty_count > max_consecutive:
                total_paras = len(paragraphs)
                start_page = estimate_page_from_paragraph(start_paragraph, total_paras)
                end_page = estimate_page_from_paragraph(len(paragraphs), total_paras)

                context_before, context_after = get_context_text(
                    start_paragraph, paragraphs
                )

                consecutive_empty.append(
                    {
                        "start": start_paragraph,
                        "end": len(paragraphs),
                        "count": empty_count,
                        "estimated_start_page": start_page,
                        "estimated_end_page": end_page,
                        "context_before": context_before,
                        "context_after": context_after,
                    }
                )

    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking empty lines: {e}",
            "details": [],
        }

    if consecutive_empty:
        return {
            "found": True,
            "message": f"Found {len(consecutive_empty)} group(s) of consecutive empty lines (max allowed: {max_consecutive})",
            "details": consecutive_empty,
            "total_paragraphs": len(paragraphs) if "paragraphs" in locals() else 0,
        }
    else:
        return {
            "found": False,
            "message": f"No consecutive empty lines found (max allowed: {max_consecutive})",
            "details": [],
            "total_paragraphs": len(paragraphs) if "paragraphs" in locals() else 0,
        }
