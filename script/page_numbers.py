#!/usr/bin/env python3
"""
Page number checking functions.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Any, Optional, Tuple
from header_footer import analyze_header_footer_usage, extract_footers_from_docx
from toc import find_toc_sections


def is_roman_numeral(text: str) -> bool:
    """
    Check if text is a Roman numeral.

    Args:
        text: Text to check

    Returns:
        True if text is a Roman numeral, False otherwise
    """
    if not text:
        return False

    text = text.strip().upper()
    # Roman numerals: I, II, III, IV, V, VI, VII, VIII, IX, X, etc.
    roman_pattern = r"^[IVXLCDM]+$"
    return bool(re.match(roman_pattern, text))


def is_arabic_numeral(text: str) -> bool:
    """
    Check if text is an Arabic numeral.

    Args:
        text: Text to check

    Returns:
        True if text is an Arabic numeral, False otherwise
    """
    if not text:
        return False

    text = text.strip()
    return text.isdigit()


def _get_font_from_runs_in_paragraph(para, namespaces: Dict[str, str]) -> Optional[str]:
    """
    Get font from any run in a paragraph (as fallback when page number run has no font).
    
    Args:
        para: Paragraph XML element
        namespaces: XML namespaces
        
    Returns:
        Font name if found, None otherwise
    """
    for run in para.findall('.//w:r', namespaces):
        rpr = run.find('.//w:rPr', namespaces)
        if rpr is not None:
            font_elem = rpr.find('.//w:rFonts', namespaces)
            if font_elem is not None:
                font = (font_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia') or
                       font_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii') or
                       font_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi') or
                       font_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs'))
                if font:
                    return font
    return None


def extract_page_number_from_footer_xml(footer_xml: bytes) -> List[Dict[str, Any]]:
    """
    Extract page number fields from footer XML.

    Args:
        footer_xml: Footer XML content as bytes

    Returns:
        List of page number information dictionaries
    """
    page_numbers = []

    try:
        root = ET.fromstring(footer_xml)
        namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

        # Find all page number fields
        # Method 1: Simple fields (w:fldSimple with w:instr="PAGE")
        for fld_simple in root.findall(".//w:fldSimple", namespaces):
            instr = fld_simple.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instr",
                "",
            )
            if "PAGE" in instr.upper():
                # Get the page number text
                text_elements = fld_simple.findall(".//w:t", namespaces)
                page_num_text = "".join(
                    [t.text for t in text_elements if t.text]
                ).strip()

                if page_num_text:
                    page_num_info = _extract_page_number_formatting(
                        fld_simple, namespaces, page_num_text
                    )
                    if page_num_info:
                        # If font is not found, try to get from paragraph
                        if page_num_info.get('font') is None:
                            para = fld_simple.find('..', namespaces)
                            while para is not None and not para.tag.endswith('}p'):
                                para = para.find('..', namespaces)
                            if para is not None:
                                fallback_font = _get_font_from_runs_in_paragraph(para, namespaces)
                                if fallback_font:
                                    page_num_info['font'] = fallback_font
                        page_numbers.append(page_num_info)

        # Method 2: Complex fields (w:fldChar with PAGE instruction)
        # Process each paragraph to find field sequences
        for para in root.findall(".//w:p", namespaces):
            field_runs = []
            in_field = False
            field_instruction = ""

            for run in para.findall(".//w:r", namespaces):
                fld_char = run.find(".//w:fldChar", namespaces)
                if fld_char is not None:
                    fld_type = fld_char.get(
                        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldCharType"
                    )
                    if fld_type == "begin":
                        in_field = True
                        field_runs = []
                        field_instruction = ""
                    elif fld_type == "end":
                        if in_field and "PAGE" in field_instruction.upper():
                            # Extract page number from field runs (after separator)
                            page_num_text = ""
                            found_separator = False
                            for r in field_runs:
                                # Skip instruction text
                                if r.find(".//w:instrText", namespaces) is not None:
                                    continue
                                if r.find(".//w:fldChar", namespaces) is not None:
                                    sep = r.find(".//w:fldChar", namespaces)
                                    if (
                                        sep is not None
                                        and sep.get(
                                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldCharType"
                                        )
                                        == "separate"
                                    ):
                                        found_separator = True
                                        continue
                                if found_separator:
                                    text_elems = r.findall(".//w:t", namespaces)
                                    page_num_text += "".join(
                                        [t.text for t in text_elems if t.text]
                                    )

                            page_num_text = page_num_text.strip()

                            if page_num_text:
                                page_num_info = _extract_page_number_formatting(
                                    para, namespaces, page_num_text
                                )
                                if page_num_info:
                                    # If font is not found, try to get from other runs in paragraph
                                    if page_num_info.get('font') is None:
                                        fallback_font = _get_font_from_runs_in_paragraph(para, namespaces)
                                        if fallback_font:
                                            page_num_info['font'] = fallback_font
                                    page_numbers.append(page_num_info)
                        in_field = False
                        field_runs = []
                        field_instruction = ""

                if in_field:
                    # Check for instruction text
                    instr_text = run.find(".//w:instrText", namespaces)
                    if instr_text is not None and instr_text.text:
                        field_instruction += instr_text.text

                    # Collect runs for page number extraction
                    field_runs.append(run)

    except Exception as e:
        # If XML parsing fails, return empty list
        pass

    return page_numbers


def _extract_page_number_formatting(
    element, namespaces: Dict[str, str], page_num_text: str
) -> Optional[Dict[str, Any]]:
    """
    Extract formatting information from a page number element.

    Args:
        element: XML element containing the page number
        namespaces: XML namespaces
        page_num_text: Page number text

    Returns:
        Dictionary with formatting information, or None if extraction fails
    """
    font_info = {}

    # Find paragraph containing the page number
    para = element if element.tag.endswith("}p") else element.find("..", namespaces)
    if para is None:
        # Try to find parent paragraph
        para = element.find("..", namespaces)
        while para is not None and not para.tag.endswith("}p"):
            para = para.find("..", namespaces)

    # Get formatting from run (most specific)
    run = element.find(".//w:r", namespaces)
    if run is not None:
        rpr = run.find(".//w:rPr", namespaces)
        if rpr is not None:
            # Get font (prefer eastAsia for Chinese fonts)
            font_elem = rpr.find(".//w:rFonts", namespaces)
            if font_elem is not None:
                font = (
                    font_elem.get(
                        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia"
                    )
                    or font_elem.get(
                        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii"
                    )
                    or font_elem.get(
                        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi"
                    )
                    or font_elem.get(
                        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs"
                    )
                )
                if font:
                    font_info["font"] = font

            # Get font size
            sz_elem = rpr.find(".//w:sz", namespaces)
            if sz_elem is not None:
                sz_val = sz_elem.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                )
                if sz_val:
                    # Convert half-points to points
                    font_info["size"] = int(sz_val) / 2

    # If font not found in run, try paragraph level
    if "font" not in font_info and para is not None:
        # Check all runs in paragraph for font information
        for run in para.findall(".//w:r", namespaces):
            rpr = run.find(".//w:rPr", namespaces)
            if rpr is not None:
                font_elem = rpr.find(".//w:rFonts", namespaces)
                if font_elem is not None:
                    font = (
                        font_elem.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia"
                        )
                        or font_elem.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii"
                        )
                        or font_elem.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi"
                        )
                        or font_elem.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs"
                        )
                    )
                    if font:
                        font_info["font"] = font
                        break

    # Get paragraph alignment
    alignment = None
    if para is not None:
        ppr = para.find(".//w:pPr", namespaces)
        if ppr is not None:
            jc = ppr.find(".//w:jc", namespaces)
            if jc is not None:
                alignment = jc.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                )

    return {
        "text": page_num_text,
        "font": font_info.get("font"),
        "size": font_info.get("size"),
        "alignment": alignment,
        "is_roman": is_roman_numeral(page_num_text),
        "is_arabic": is_arabic_numeral(page_num_text),
    }


def determine_page_section(
    estimated_page: int,
    toc_sections: Dict[str, Any],
    footer_page_info: List[Dict[str, Any]],
) -> str:
    """
    Determine if a page is in contents section or body section.

    Args:
        estimated_page: Estimated page number
        toc_sections: Dictionary with TOC section information
        footer_page_info: List of page info from footer

    Returns:
        'contents' if in contents section, 'body' otherwise
    """
    # Find the end of contents section (after table_list)
    # Contents section includes: cover, table_of_contents, figure_list, table_list
    # We need to find where table_list ends to determine the boundary
    
    table_list_info = toc_sections.get("table_list")
    if table_list_info:
        # Get the start paragraph of table_list
        start_para = table_list_info.get("start_para")
        if start_para:
            # Estimate the page number where table_list starts
            # We'll estimate that table_list typically takes 1-2 pages
            # So contents section ends approximately at table_list_start_page + 2
            from utils import estimate_page_from_paragraph
            # We need total_paras to estimate, but we don't have it here
            # Use a rough estimate: assume table_list starts around page 3-5 for typical documents
            # If estimated_page is <= 5, it's likely in contents section
            # This is a heuristic, but better than always returning "contents"
            if estimated_page <= 5:
                return "contents"
    
    # If we can't determine from TOC, check footer page_info
    # Look at section numbers - typically contents are in early sections
    if footer_page_info:
        # Get section numbers from page_info
        sections = [info.get("section", 999) for info in footer_page_info]
        min_section = min(sections) if sections else 999
        
        # If we're in section 0, 1, or 2, and page is early, likely contents
        if min_section <= 2 and estimated_page <= 5:
            return "contents"

    # If we can't determine, assume it's in body
    # This is safer than assuming contents, as most pages are body
    return "body"


def check_page_number_format(
    docx_path: str, format_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check page number format (font, size, position).

    Args:
        docx_path: Path to Word document
        format_config: Format configuration from config file

    Returns:
        Dictionary with check results
    """
    issues = []

    try:
        usage_info = analyze_header_footer_usage(docx_path)
        footers = extract_footers_from_docx(docx_path, usage_info)

        required_size = format_config.get("size")
        required_position = format_config.get("position")

        for footer in footers:
            footer_xml = footer["raw_xml"].encode("utf-8")
            page_numbers = extract_page_number_from_footer_xml(footer_xml)

            for page_num in page_numbers:
                # Check size
                if required_size and page_num.get("size"):
                    # Allow small tolerance for size (0.5 points)
                    if abs(page_num.get("size") - required_size) > 0.5:
                        issues.append(
                            {
                                "footer_file": footer["file"],
                                "issue": f"Page number size is {page_num.get('size')}, should be {required_size}",
                                "page_num_text": page_num.get("text"),
                            }
                        )

                # Check position (alignment)
                if required_position:
                    # Map position to alignment
                    position_map = {
                        "bottom_center": "center",
                        "bottom_left": "left",
                        "bottom_right": "right",
                    }
                    required_alignment = position_map.get(required_position, "center")

                    if page_num.get("alignment") != required_alignment:
                        issues.append(
                            {
                                "footer_file": footer["file"],
                                "issue": f"Page number alignment is '{page_num.get('alignment')}', should be '{required_alignment}'",
                                "page_num_text": page_num.get("text"),
                            }
                        )

        if issues:
            return {
                "found": True,
                "message": f"Found {len(issues)} page number format issue(s)",
                "details": issues,
            }
        else:
            return {
                "found": False,
                "message": "Page number format is correct",
                "details": [],
            }

    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking page number format: {e}",
            "details": [],
        }


def check_page_number_style(
    docx_path: str, format_config: Dict[str, Any], toc_sections: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check page number style (Roman vs Arabic) for different sections.

    Args:
        docx_path: Path to Word document
        format_config: Format configuration from config file
        toc_sections: Dictionary with TOC section information

    Returns:
        Dictionary with check results
    """
    issues = []

    try:
        usage_info = analyze_header_footer_usage(docx_path)
        footers = extract_footers_from_docx(docx_path, usage_info)

        # Get sections configuration
        sections_config = format_config.get("sections")
        if not sections_config:
            # If no sections config, use single style
            style = format_config.get("style", "arabic")
            # Simple check - all pages should use the same style
            for footer in footers:
                footer_xml = footer["raw_xml"].encode("utf-8")
                page_numbers = extract_page_number_from_footer_xml(footer_xml)

                for page_num in page_numbers:
                    page_num_text = page_num.get("text", "")
                    if style == "roman" and not page_num.get("is_roman"):
                        issues.append(
                            {
                                "footer_file": footer["file"],
                                "issue": f"Page number '{page_num_text}' should be Roman numeral",
                                "page_num_text": page_num_text,
                            }
                        )
                    elif style == "arabic" and not page_num.get("is_arabic"):
                        issues.append(
                            {
                                "footer_file": footer["file"],
                                "issue": f"Page number '{page_num_text}' should be Arabic numeral",
                                "page_num_text": page_num_text,
                            }
                        )
        else:
            # Check segmented page numbers
            contents_style = sections_config.get("contents", {}).get("style", "roman")
            body_style = sections_config.get("body", {}).get("style", "arabic")

            for footer in footers:
                footer_xml = footer["raw_xml"].encode("utf-8")
                page_numbers = extract_page_number_from_footer_xml(footer_xml)

                # Determine which section this footer belongs to
                page_info = footer.get("page_info", [])
                for page_num in page_numbers:
                    page_num_text = page_num.get("text", "")

                    # Determine section based on actual page number style
                    # If page number is Roman, it's in contents section
                    # If page number is Arabic, it's in body section
                    # This is more reliable than trying to estimate from paragraph positions
                    if page_num.get("is_roman"):
                        # Page number is Roman, so it should be in contents section
                        section = "contents"
                        expected_style = contents_style
                    elif page_num.get("is_arabic"):
                        # Page number is Arabic, so it should be in body section
                        section = "body"
                        expected_style = body_style
                    else:
                        # Can't determine from page number style, fall back to estimation
                        section = "body"  # Default to body
                        if page_info:
                            estimated_page = page_info[0].get("estimated_start_page", 0)
                            section = determine_page_section(
                                estimated_page, toc_sections, page_info
                            )
                        expected_style = contents_style if section == "contents" else body_style

                    # Check style based on determined section
                    if section == "contents":
                        if expected_style == "roman" and not page_num.get("is_roman"):
                            issues.append(
                                {
                                    "footer_file": footer["file"],
                                    "issue": f"Contents section page number '{page_num_text}' should be Roman numeral",
                                    "page_num_text": page_num_text,
                                    "section": section,
                                }
                            )
                        elif expected_style == "arabic" and not page_num.get("is_arabic"):
                            issues.append(
                                {
                                    "footer_file": footer["file"],
                                    "issue": f"Contents section page number '{page_num_text}' should be Arabic numeral",
                                    "page_num_text": page_num_text,
                                    "section": section,
                                }
                            )
                    else:  # body section
                        if expected_style == "roman" and not page_num.get("is_roman"):
                            issues.append(
                                {
                                    "footer_file": footer["file"],
                                    "issue": f"Body section page number '{page_num_text}' should be Roman numeral",
                                    "page_num_text": page_num_text,
                                    "section": section,
                                }
                            )
                        elif expected_style == "arabic" and not page_num.get("is_arabic"):
                            issues.append(
                                {
                                    "footer_file": footer["file"],
                                    "issue": f"Body section page number '{page_num_text}' should be Arabic numeral",
                                    "page_num_text": page_num_text,
                                    "section": section,
                                }
                            )

        if issues:
            return {
                "found": True,
                "message": f"Found {len(issues)} page number style issue(s)",
                "details": issues,
            }
        else:
            return {
                "found": False,
                "message": "Page number style is correct",
                "details": [],
            }

    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking page number style: {e}",
            "details": [],
        }


def check_page_numbers(
    docx_path: str, page_numbers_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check page numbers format and style.

    Args:
        docx_path: Path to Word document
        page_numbers_config: Page numbers configuration from config file

    Returns:
        Dictionary with all check results
    """
    results = {
        "format": {"found": False, "message": "Not checked", "details": []},
        "style": {"found": False, "message": "Not checked", "details": []},
    }

    format_config = page_numbers_config.get("format", {})
    if not format_config:
        return results

    # Check format
    format_result = check_page_number_format(docx_path, format_config)
    results["format"] = format_result

    # Check style
    toc_sections = find_toc_sections(docx_path)
    style_result = check_page_number_style(docx_path, format_config, toc_sections)
    results["style"] = style_result

    return results
