#!/usr/bin/env python3
"""
Cover page checking functions.
"""

import zipfile
import xml.etree.ElementTree as ET


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


def get_paragraph_fonts(para, namespaces):
    """Get all fonts used in a paragraph."""
    fonts = []
    runs = para.findall(".//w:r", namespaces)

    for run in runs:
        font = get_font_from_run(run, namespaces)
        if font:
            fonts.append(font)

    return fonts


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


def find_first_page_end(paragraphs, namespaces, body):
    """
    Find the end of the first page by looking for section breaks or page breaks.

    Returns:
        Index of the last paragraph on the first page (0-based)
    """
    for para_idx, para in enumerate(paragraphs):
        if is_in_table_cell(para, body):
            continue

        pPr = para.find(".//w:pPr", namespaces)
        if pPr is not None:
            sectPr = pPr.find(".//w:sectPr", namespaces)
            if sectPr is not None:
                return para_idx

            pgNumType = pPr.find(".//w:pgNumType", namespaces)
            if pgNumType is not None:
                pgStart = pgNumType.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}start"
                )
                if pgStart and int(pgStart) > 1:
                    return para_idx

        runs = para.findall(".//w:r", namespaces)
        for run in runs:
            br = run.find(".//w:br", namespaces)
            if br is not None:
                br_type = br.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type"
                )
                if br_type == "page":
                    return para_idx

    return len(paragraphs)


def check_cover_font(docx_path, required_font=None):
    """
    Check if cover page (first page only) uses the required font.

    Args:
        docx_path: Path to the Word document
        required_font: Required font name (if None, will use default from config)

    Returns:
        Dictionary with check results
    """
    if required_font is None:
        from config_loader import ConfigLoader

        config_loader = ConfigLoader()
        config = config_loader.load()
        cover_config = config.get("cover", {})
        if not cover_config:
            raise ValueError("Cover configuration not found in config file")
        format_config = cover_config.get("format", {})
        if not format_config:
            raise ValueError("Cover format configuration not found in config file")
        required_font = format_config.get("font")
        if not required_font:
            raise ValueError("Cover font not specified in config file (cover.format.font)")
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

            paragraphs = body.findall(".//w:p", namespaces)

            first_page_end = find_first_page_end(paragraphs, namespaces, body)
            first_page_paragraphs = paragraphs[: first_page_end + 1]

            cover_paragraphs = []

            for para_idx, para in enumerate(first_page_paragraphs, 1):
                if is_in_table_cell(para, body):
                    continue

                para_text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join(
                    [t.text for t in para_text_elements if t.text]
                ).strip()

                if para_text:
                    fonts = get_paragraph_fonts(para, namespaces)
                    if fonts:
                        cover_paragraphs.append(
                            {
                                "paragraph": para_idx,
                                "text": para_text[:50],
                                "fonts": fonts,
                            }
                        )

            if not cover_paragraphs:
                return {
                    "found": False,
                    "message": "No cover paragraphs found on first page",
                    "details": [],
                }

            for para_info in cover_paragraphs:
                para_fonts = para_info["fonts"]
                if not para_fonts:
                    continue

                unique_fonts = list(set(para_fonts))

                all_use_required_font = all(
                    required_font in font for font in unique_fonts
                )

                if not all_use_required_font:
                    issues.append(
                        {
                            "paragraph": para_info["paragraph"],
                            "page": 1,
                            "text": para_info["text"],
                            "fonts": unique_fonts,
                            "required_font": required_font,
                        }
                    )

    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking cover font: {e}",
            "details": [],
        }

    if issues:
        return {
            "found": True,
            "message": f"Found {len(issues)} cover paragraph(s) on first page with incorrect font",
            "details": issues,
        }
    else:
        return {
            "found": False,
            "message": f"All cover paragraphs on first page use {required_font} font",
            "details": [],
        }
