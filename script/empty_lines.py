#!/usr/bin/env python3
"""
Empty lines checking functions.
"""

import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
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
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
                "o": "urn:schemas-microsoft-com:office:office"
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

            # Pre-build a set of all paragraphs that are inside table cells for fast lookup
            # This is much more efficient than checking each paragraph individually
            tc_elements = body.findall(".//w:tc", namespaces)
            table_cell_paragraphs = set()
            for tc in tc_elements:
                # Get all paragraphs inside this table cell
                tc_paras = tc.findall(".//w:p", namespaces)
                table_cell_paragraphs.update(tc_paras)

            def is_in_table_cell(para):
                """Check if paragraph is inside a table cell - optimized version using pre-built set."""
                return para in table_cell_paragraphs

            def has_non_text_content(para):
                """Check if paragraph contains images, formulas, or other non-text content - optimized version."""
                # Check for images/drawings (most common case, check first)
                if para.find(".//w:drawing", namespaces) is not None:
                    return True
                if para.find(".//w:pict", namespaces) is not None:
                    return True
                # Check for formulas (Office Math) - check both oMath and oMathPara
                if para.find(".//m:oMath", namespaces) is not None:
                    return True
                if para.find(".//m:oMathPara", namespaces) is not None:
                    return True
                # Check for embedded objects
                if para.find(".//o:OLEObject", namespaces) is not None:
                    return True
                # Check for section properties (sectPr) - these are not empty lines
                if para.find(".//w:sectPr", namespaces) is not None:
                    return True
                # Check for math namespace in any element tag (only if other checks failed)
                # This is a fallback check for edge cases
                math_ns = "http://schemas.openxmlformats.org/officeDocument/2006/math"
                # Only iterate if we haven't found anything yet (optimization)
                for elem in para.iter():
                    if math_ns in elem.tag:
                        return True
                return False

            def get_paragraph_text(para):
                text_elements = para.findall(".//w:t", namespaces)
                return "".join([t.text for t in text_elements if t.text]).strip()

            def analyze_paragraph(para_info):
                """Analyze a single paragraph to determine its state."""
                para_idx, para = para_info
                para_idx_0based = para_idx - 1

                # Check if in first page (skip)
                if para_idx_0based <= first_page_end:
                    return {
                        "idx": para_idx,
                        "skip": True,
                        "is_empty": False,
                        "in_table": False,
                    }

                # Check if in table cell
                in_table = is_in_table_cell(para)
                if in_table:
                    return {
                        "idx": para_idx,
                        "skip": True,
                        "is_empty": False,
                        "in_table": True,
                    }

                # Check if paragraph is empty
                has_non_text = has_non_text_content(para)
                if has_non_text:
                    return {
                        "idx": para_idx,
                        "skip": False,
                        "is_empty": False,
                        "in_table": False,
                    }

                para_text = get_paragraph_text(para)
                is_empty = not para_text

                return {
                    "idx": para_idx,
                    "skip": False,
                    "is_empty": is_empty,
                    "in_table": False,
                    "text": para_text,
                }

            # Parallel preprocessing: analyze all paragraphs
            para_info_list = list(enumerate(paragraphs, 1))
            para_states = {}

            # Use parallel processing for large documents
            if len(paragraphs) > 100:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    future_to_para = {
                        executor.submit(analyze_paragraph, para_info): para_info[0]
                        for para_info in para_info_list
                    }
                    for future in as_completed(future_to_para):
                        result = future.result()
                        para_states[result["idx"]] = result
            else:
                # For small documents, sequential processing is faster
                for para_info in para_info_list:
                    result = analyze_paragraph(para_info)
                    para_states[result["idx"]] = result

            def get_context_text(para_idx, paragraphs, para_states, before_count=3, after_count=3):
                context_before = []
                context_after = []

                for i in range(max(0, para_idx - before_count - 1), para_idx - 1):
                    if i >= 0 and i < len(paragraphs):
                        state = para_states.get(i + 1, {})
                        text = state.get("text", "")
                        if text and len(text) > 5:
                            context_before.append(text[:150])

                for i in range(para_idx, min(len(paragraphs), para_idx + after_count)):
                    if i < len(paragraphs):
                        state = para_states.get(i + 1, {})
                        text = state.get("text", "")
                        if text and len(text) > 5:
                            context_after.append(text[:150])

                return context_before[-2:], context_after[:2]

            # Sequential processing of consecutive empty lines detection
            empty_count = 0
            start_paragraph = None

            for para_idx in range(1, len(paragraphs) + 1):
                state = para_states.get(para_idx, {})

                if state.get("skip", False):
                    if empty_count > max_consecutive:
                        empty_count = 0
                        start_paragraph = None
                    continue

                if state.get("is_empty", False):
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
                            start_paragraph, paragraphs, para_states
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
                    start_paragraph, paragraphs, para_states
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
            "message": f"发现 {len(consecutive_empty)} 组连续空行（最大允许：{max_consecutive}）",
            "details": consecutive_empty,
            "total_paragraphs": len(paragraphs) if "paragraphs" in locals() else 0,
        }
    else:
        return {
            "found": False,
            "message": f"未发现连续空行（最大允许：{max_consecutive}）",
            "details": [],
            "total_paragraphs": len(paragraphs) if "paragraphs" in locals() else 0,
        }
