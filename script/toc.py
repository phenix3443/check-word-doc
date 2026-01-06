#!/usr/bin/env python3
"""
Table of contents checking functions.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import estimate_page_from_paragraph


def get_paragraph_style(para, namespaces):
    """Get paragraph style ID."""
    pPr = para.find(".//w:pPr", namespaces)
    if pPr is not None:
        pStyle = pPr.find(".//w:pStyle", namespaces)
        if pStyle is not None:
            return pStyle.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
            )
    return None


def get_font_from_run(run, namespaces):
    """Extract font name from a run element."""
    rPr = run.find(".//w:rPr", namespaces)
    if rPr is not None:
        rFonts = rPr.find(".//w:rFonts", namespaces)
        if rFonts is not None:
            font_east_asia = rFonts.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia"
            )
            font_ascii = rFonts.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii"
            )
            font_cs = rFonts.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs"
            )
            font_hAnsi = rFonts.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi"
            )

            font = font_east_asia or font_ascii or font_cs or font_hAnsi
            if font:
                return font
    return None


def get_font_size_from_run(run, namespaces):
    """Extract font size from a run element."""
    rPr = run.find(".//w:rPr", namespaces)
    if rPr is not None:
        sz = rPr.find(".//w:sz", namespaces)
        if sz is not None:
            sz_val = sz.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
            )
            if sz_val:
                return int(sz_val) / 2
    return None


def get_alignment(para, namespaces):
    """Get paragraph alignment."""
    pPr = para.find(".//w:pPr", namespaces)
    if pPr is not None:
        jc = pPr.find(".//w:jc", namespaces)
        if jc is not None:
            val = jc.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
            )
            if val:
                return val
    return "left"


def get_indent(para, namespaces):
    """Get paragraph indent information."""
    pPr = para.find(".//w:pPr", namespaces)
    indent_info = {}
    if pPr is not None:
        ind = pPr.find(".//w:ind", namespaces)
        if ind is not None:
            left = ind.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left"
            )
            first_line = ind.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLine"
            )
            hanging = ind.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hanging"
            )
            if left:
                indent_info["left"] = int(left) / 20
            if first_line:
                indent_info["first_line"] = int(first_line) / 20
            if hanging:
                indent_info["hanging"] = int(hanging) / 20
    return indent_info


def is_in_table_cell(para, body):
    """Check if paragraph is inside a table cell."""
    current = para
    for _ in range(20):
        found_parent = False
        for elem in body.iter():
            if current in list(elem):
                if elem.tag.endswith("}tc"):
                    return True
                current = elem
                found_parent = True
                break
        if not found_parent:
            break
    return False


def find_toc_sections(docx_path):
    """
    Find table of contents, figure list, and table list sections.

    Returns:
        Dictionary with section information
    """
    sections = {
        "table_of_contents": None,
        "figure_list": None,
        "table_list": None,
    }

    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            if "word/document.xml" not in docx.namelist():
                return sections

            document_xml = docx.read("word/document.xml")
            root = ET.fromstring(document_xml)

            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }

            body = root.find(".//w:body", namespaces)
            if body is None:
                return sections

            paragraphs = body.findall(".//w:p", namespaces)

            toc_keywords = ["目录", "目  录", "目   录"]
            figure_keywords = ["图目录", "插图目录", "图  目录", "图   目录"]
            table_keywords = ["表目录", "附表目录", "表  目录", "表   目录"]

            for para_idx, para in enumerate(paragraphs, 1):
                if is_in_table_cell(para, body):
                    continue

                para_text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join(
                    [t.text for t in para_text_elements if t.text]
                ).strip()

                if not para_text:
                    continue

                if sections["table_of_contents"] is None:
                    for keyword in toc_keywords:
                        if keyword in para_text and len(para_text) < 20:
                            sections["table_of_contents"] = {
                                "start_para": para_idx,
                                "title": para_text,
                            }
                            break

                if sections["figure_list"] is None:
                    for keyword in figure_keywords:
                        if keyword in para_text and len(para_text) < 20:
                            sections["figure_list"] = {
                                "start_para": para_idx,
                                "title": para_text,
                            }
                            break

                if sections["table_list"] is None:
                    for keyword in table_keywords:
                        if keyword in para_text and len(para_text) < 20:
                            sections["table_list"] = {
                                "start_para": para_idx,
                                "title": para_text,
                            }
                            break

    except Exception as e:
        print(f"Error finding TOC sections: {e}")

    return sections


def check_toc_format(docx_path, section_type, style_config):
    """
    Check table of contents format.

    Args:
        docx_path: Path to the Word document
        section_type: 'table_of_contents', 'figure_list', or 'table_list'
        style_config: Configuration for TOC1, TOC2, TOC3 styles

    Returns:
        Dictionary with check results
    """
    issues = []

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

            sections = find_toc_sections(docx_path)
            section_info = sections.get(section_type)

            if not section_info:
                return {
                    "found": False,
                    "message": f"{section_type} section not found",
                    "details": [],
                }

            paragraphs = body.findall(".//w:p", namespaces)
            start_para = section_info["start_para"]

            toc_paragraphs = []
            max_check_paras = 500  # 增加检查范围，但优化并行处理

            for para_idx in range(
                start_para, min(start_para + max_check_paras, len(paragraphs))
            ):
                para = paragraphs[para_idx - 1]
                if is_in_table_cell(para, body):
                    continue

                para_text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join(
                    [t.text for t in para_text_elements if t.text]
                ).strip()

                if not para_text:
                    continue

                style_id = get_paragraph_style(para, namespaces)
                if style_id and style_id.upper() in ["TOC1", "TOC2", "TOC3"]:
                    toc_paragraphs.append(
                        {
                            "paragraph": para_idx,
                            "text": para_text[:100],
                            "style": style_id.upper(),
                        }
                    )
                elif para_text and not any(
                    keyword in para_text
                    for keyword in ["目录", "图目录", "表目录", "参考文献", "正文"]
                ):
                    break

            if not toc_paragraphs:
                return {
                    "found": False,
                    "message": f"No TOC paragraphs found in {section_type}",
                    "details": [],
                }

            def check_paragraph_format(para_info_item):
                """Check format for a single paragraph."""
                para_idx = para_info_item["paragraph"]
                para = paragraphs[para_idx - 1]
                style_id = para_info_item["style"]
                expected_style = style_config.get(style_id, {})
                issues_found = []

                runs = para.findall(".//w:r", namespaces)
                if runs:
                    first_run = runs[0]
                    font = get_font_from_run(first_run, namespaces)
                    font_size = get_font_size_from_run(first_run, namespaces)

                    if expected_style.get("font"):
                        if not font or expected_style["font"] not in font:
                            issues_found.append(
                                f"Font should be {expected_style['font']}, found: {font}"
                            )

                    if expected_style.get("size"):
                        if (
                            not font_size
                            or abs(font_size - expected_style["size"]) > 0.5
                        ):
                            issues_found.append(
                                f"Font size should be {expected_style['size']}, found: {font_size}"
                            )

                alignment = get_alignment(para, namespaces)
                if expected_style.get("alignment"):
                    if alignment != expected_style["alignment"]:
                        issues_found.append(
                            f"Alignment should be {expected_style['alignment']}, found: {alignment}"
                        )

                indent_info = get_indent(para, namespaces)
                if expected_style.get("indent_first_line") is not None:
                    actual_first_line = indent_info.get("first_line", 0)
                    expected_first_line = expected_style["indent_first_line"]
                    if abs(actual_first_line - expected_first_line) > 1:
                        issues_found.append(
                            f"First line indent should be {expected_first_line}pt, found: {actual_first_line}pt"
                        )

                if expected_style.get("indent_left") is not None:
                    actual_left = indent_info.get("left", 0)
                    expected_left = expected_style["indent_left"]
                    if abs(actual_left - expected_left) > 1:
                        issues_found.append(
                            f"Left indent should be {expected_left}pt, found: {actual_left}pt"
                        )

                if expected_style.get("indent_hanging") is not None:
                    actual_hanging = indent_info.get("hanging", 0)
                    expected_hanging = expected_style["indent_hanging"]
                    if abs(actual_hanging - expected_hanging) > 1:
                        issues_found.append(
                            f"Hanging indent should be {expected_hanging}pt, found: {actual_hanging}pt"
                        )

                if issues_found:
                    page = estimate_page_from_paragraph(para_idx, len(paragraphs))
                    return {
                        "paragraph": para_idx,
                        "page": page,
                        "text": para_info_item["text"],
                        "style": style_id,
                        "issues": issues_found,
                    }
                return None

            if len(toc_paragraphs) > 5:  # 降低并行阈值，提高响应速度
                with ThreadPoolExecutor(max_workers=8) as executor:  # 增加工作线程数
                    future_to_para = {
                        executor.submit(check_paragraph_format, para_info): para_info
                        for para_info in toc_paragraphs
                    }
                    for future in as_completed(future_to_para):
                        result = future.result()
                        if result:
                            issues.append(result)
            else:
                for para_info in toc_paragraphs:
                    result = check_paragraph_format(para_info)
                    if result:
                        issues.append(result)

    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking TOC format: {e}",
            "details": [],
        }

    if issues:
        return {
            "found": True,
            "message": f"Found {len(issues)} paragraph(s) with incorrect format in {section_type}",
            "details": issues,
        }
    else:
        return {
            "found": False,
            "message": f"All paragraphs in {section_type} have correct format",
            "details": [],
        }


def check_toc_order(docx_path):
    """
    Check if TOC sections are in correct order: cover -> table_of_contents -> figure_list -> table_list.

    Returns:
        Dictionary with check results
    """
    sections = find_toc_sections(docx_path)

    expected_order = ["table_of_contents", "figure_list", "table_list"]
    found_sections = [
        (name, info["start_para"])
        for name, info in sections.items()
        if info is not None
    ]
    found_sections.sort(key=lambda x: x[1])

    order_issues = []

    for i, (section_name, para_num) in enumerate(found_sections):
        if i < len(expected_order):
            expected_section = expected_order[i]
            if section_name != expected_section:
                order_issues.append(
                    f"Expected {expected_section} at position {i + 1}, found {section_name} at paragraph {para_num}"
                )

    if order_issues:
        return {
            "found": True,
            "message": "TOC sections are not in correct order",
            "details": order_issues,
            "sections": sections,
        }
    else:
        return {
            "found": False,
            "message": "TOC sections are in correct order",
            "details": [],
            "sections": sections,
        }


def extract_toc_entry_info(para_text):
    """Extract numbering and page number from TOC entry text."""
    text = para_text.strip()

    page_match = re.search(r"(\d+)\s*$", text)
    page_num = int(page_match.group(1)) if page_match else None

    text_without_page = re.sub(r"\s*\d+\s*$", "", text).strip()

    numbering_match = re.match(r"^(\d+(?:\.\d+)*)", text_without_page)
    numbering = numbering_match.group(1) if numbering_match else None

    title = re.sub(r"^\d+(?:\.\d+)*\s+", "", text_without_page).strip()

    return {"numbering": numbering, "page": page_num, "title": title, "full_text": text}


def check_toc_numbering_continuity(docx_path, section_type, numbering_config):
    """
    Check if TOC numbering is continuous.

    Args:
        docx_path: Path to the Word document
        section_type: 'table_of_contents', 'figure_list', or 'table_list'
        numbering_config: Configuration for numbering check

    Returns:
        Dictionary with check results
    """
    if not numbering_config.get("check_continuity", False):
        return {
            "found": False,
            "message": "Numbering continuity check is disabled",
            "details": [],
        }

    issues = []

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

            sections = find_toc_sections(docx_path)
            section_info = sections.get(section_type)

            if not section_info:
                return {
                    "found": False,
                    "message": f"{section_type} section not found",
                    "details": [],
                }

            paragraphs = body.findall(".//w:p", namespaces)
            start_para = section_info["start_para"]

            toc_entries = []
            max_check_paras = 500  # 增加检查范围

            for para_idx in range(
                start_para, min(start_para + max_check_paras, len(paragraphs))
            ):
                para = paragraphs[para_idx - 1]
                if is_in_table_cell(para, body):
                    continue

                para_text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join(
                    [t.text for t in para_text_elements if t.text]
                ).strip()

                if not para_text:
                    continue

                style_id = get_paragraph_style(para, namespaces)
                if style_id and style_id.upper() in ["TOC1", "TOC2", "TOC3"]:
                    entry_info = extract_toc_entry_info(para_text)
                    if entry_info["numbering"]:
                        toc_entries.append(
                            {
                                "paragraph": para_idx,
                                "numbering": entry_info["numbering"],
                                "page": entry_info["page"],
                                "title": entry_info["title"],
                                "full_text": entry_info["full_text"],
                            }
                        )
                elif para_text and not any(
                    keyword in para_text
                    for keyword in ["目录", "图目录", "表目录", "参考文献", "正文"]
                ):
                    break

            if len(toc_entries) < 2:
                return {
                    "found": False,
                    "message": f"Not enough TOC entries to check continuity in {section_type}",
                    "details": [],
                }

            def parse_numbering(num_str):
                """Parse numbering string to list of integers."""
                try:
                    return [int(x) for x in num_str.split(".")]
                except (ValueError, AttributeError):
                    return None

            prev_numbering = None
            for i, entry in enumerate(toc_entries):
                current_num = parse_numbering(entry["numbering"])
                if current_num is None:
                    continue

                if prev_numbering is not None:
                    level = min(len(current_num), len(prev_numbering))

                    for level_idx in range(level):
                        if level_idx < level - 1:
                            if current_num[level_idx] != prev_numbering[level_idx]:
                                issues.append(
                                    {
                                        "paragraph": entry["paragraph"],
                                        "page": estimate_page_from_paragraph(
                                            entry["paragraph"], len(paragraphs)
                                        ),
                                        "numbering": entry["numbering"],
                                        "prev_numbering": ".".join(
                                            map(str, prev_numbering)
                                        ),
                                        "issue": f"Numbering discontinuity at level {level_idx + 1}",
                                    }
                                )
                                break
                        else:
                            if current_num[level_idx] != prev_numbering[level_idx] + 1:
                                if current_num[level_idx] != prev_numbering[level_idx]:
                                    issues.append(
                                        {
                                            "paragraph": entry["paragraph"],
                                            "page": estimate_page_from_paragraph(
                                                entry["paragraph"], len(paragraphs)
                                            ),
                                            "numbering": entry["numbering"],
                                            "prev_numbering": ".".join(
                                                map(str, prev_numbering)
                                            ),
                                            "issue": f"Expected {prev_numbering[level_idx] + 1}, found {current_num[level_idx]}",
                                        }
                                    )

                prev_numbering = current_num

    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking TOC numbering continuity: {e}",
            "details": [],
        }

    if issues:
        return {
            "found": True,
            "message": f"Found {len(issues)} numbering continuity issue(s) in {section_type}",
            "details": issues,
        }
    else:
        return {
            "found": False,
            "message": f"All numbering is continuous in {section_type}",
            "details": [],
        }


def check_toc_page_accuracy(docx_path, section_type, validation_config):
    """
    Check if TOC page numbers match actual page numbers in document.

    Args:
        docx_path: Path to the Word document
        section_type: 'table_of_contents', 'figure_list', or 'table_list'
        validation_config: Configuration for validation check

    Returns:
        Dictionary with check results
    """
    if not validation_config.get("check_page_numbers", False):
        return {
            "found": False,
            "message": "Page number accuracy check is disabled",
            "details": [],
        }

    issues = []

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

            sections = find_toc_sections(docx_path)
            section_info = sections.get(section_type)

            if not section_info:
                return {
                    "found": False,
                    "message": f"{section_type} section not found",
                    "details": [],
                }

            paragraphs = body.findall(".//w:p", namespaces)
            start_para = section_info["start_para"]

            toc_entries = []
            max_check_paras = 500  # 增加检查范围

            for para_idx in range(
                start_para, min(start_para + max_check_paras, len(paragraphs))
            ):
                para = paragraphs[para_idx - 1]
                if is_in_table_cell(para, body):
                    continue

                para_text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join(
                    [t.text for t in para_text_elements if t.text]
                ).strip()

                if not para_text:
                    continue

                style_id = get_paragraph_style(para, namespaces)
                if style_id and style_id.upper() in ["TOC1", "TOC2", "TOC3"]:
                    entry_info = extract_toc_entry_info(para_text)
                    if entry_info["numbering"] and entry_info["page"]:
                        toc_entries.append(
                            {
                                "paragraph": para_idx,
                                "numbering": entry_info["numbering"],
                                "toc_page": entry_info["page"],
                                "title": entry_info["title"],
                                "full_text": entry_info["full_text"],
                            }
                        )
                elif para_text and not any(
                    keyword in para_text
                    for keyword in ["目录", "图目录", "表目录", "参考文献", "正文"]
                ):
                    break

            if not toc_entries:
                return {
                    "found": False,
                    "message": f"No TOC entries with page numbers found in {section_type}",
                    "details": [],
                }

            for entry in toc_entries:
                estimated_page = estimate_page_from_paragraph(
                    entry["paragraph"], len(paragraphs)
                )
                toc_page = entry["toc_page"]

                # 页码必须完全匹配，不允许有误差
                if estimated_page != toc_page:
                    issues.append(
                        {
                            "paragraph": entry["paragraph"],
                            "toc_page": toc_page,
                            "estimated_page": estimated_page,
                            "numbering": entry["numbering"],
                            "title": entry["title"],
                            "issue": f"TOC shows page {toc_page}, but estimated page is {estimated_page}",
                        }
                    )

    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking TOC page accuracy: {e}",
            "details": [],
        }

    if issues:
        return {
            "found": True,
            "message": f"Found {len(issues)} page number accuracy issue(s) in {section_type}",
            "details": issues,
        }
    else:
        return {
            "found": False,
            "message": f"All page numbers are accurate in {section_type}",
            "details": [],
        }


def check_toc_all(docx_path, section_type, config):
    """
    Perform all TOC checks in parallel: format, numbering continuity, and page accuracy.

    Args:
        docx_path: Path to the Word document
        section_type: 'table_of_contents', 'figure_list', or 'table_list'
        config: Full configuration for the section

    Returns:
        Dictionary with all check results
    """
    results = {}

    def run_format_check():
        style_config = config.get("styles", {})
        return check_toc_format(docx_path, section_type, style_config)

    def run_numbering_check():
        numbering_config = config.get("numbering", {})
        return check_toc_numbering_continuity(docx_path, section_type, numbering_config)

    def run_page_check():
        validation_config = config.get("validation", {})
        return check_toc_page_accuracy(docx_path, section_type, validation_config)

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_format = executor.submit(run_format_check)
        future_numbering = executor.submit(run_numbering_check)
        future_page = executor.submit(run_page_check)

        results["format"] = future_format.result()
        results["numbering"] = future_numbering.result()
        results["page_accuracy"] = future_page.result()

    return results


def check_toc_complete(docx_path, config):
    """
    Perform all table of contents checks in parallel: order, format, numbering continuity, and page accuracy.

    Args:
        docx_path: Path to the Word document
        config: Full configuration for table_of_contents section

    Returns:
        Dictionary with all check results including order, format, numbering, and page_accuracy
    """
    results = {}

    def run_order_check():
        return check_toc_order(docx_path)

    def run_format_check():
        style_config = config.get("styles", {})
        return check_toc_format(docx_path, "table_of_contents", style_config)

    def run_numbering_check():
        numbering_config = config.get("numbering", {})
        return check_toc_numbering_continuity(docx_path, "table_of_contents", numbering_config)

    def run_page_check():
        validation_config = config.get("validation", {})
        return check_toc_page_accuracy(docx_path, "table_of_contents", validation_config)

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_order = executor.submit(run_order_check)
        future_format = executor.submit(run_format_check)
        future_numbering = executor.submit(run_numbering_check)
        future_page = executor.submit(run_page_check)

        results["order"] = future_order.result()
        results["format"] = future_format.result()
        results["numbering"] = future_numbering.result()
        results["page_accuracy"] = future_page.result()

    return results
