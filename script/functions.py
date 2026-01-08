#!/usr/bin/env python3
"""
Individual check functions for document format checking.
"""

from pathlib import Path
from config_loader import ConfigLoader
from cover import check_cover_font
from toc import check_toc_order, check_toc_all, check_toc_complete
from header_footer import (
    analyze_header_footer_usage,
    extract_headers_from_docx,
    extract_footers_from_docx,
    check_header_consistency,
    check_footer_consistency,
)
from empty_lines import check_consecutive_empty_lines
from figure import check_figure_empty_lines, check_caption_alignment
from page_numbers import check_page_numbers
from chinese_text import check_chinese_spacing, check_chinese_quotes


def _is_check_enabled(config_loader, check_name, item_config):
    """
    Check if a check item is enabled with priority control.
    
    Priority:
    1. checks.<check_name> (top-level control) - if False, check is disabled
    2. <check_name>.enabled (item-level control) - if False, check is disabled
    
    Args:
        config_loader: ConfigLoader instance
        check_name: Name of the check (e.g., "cover", "page_numbers")
        item_config: Configuration dictionary for the check item
        
    Returns:
        True if check is enabled, False otherwise
    """
    # First check top-level checks section
    if not config_loader.get_check_enabled(check_name):
        return False
    
    # Then check item-level enabled flag
    if not item_config.get("enabled", True):
        return False
    
    return True


from references import check_unreferenced_references


def run_cover_check(docx_path):
    """Run cover page check."""
    print("Checking cover font...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        cover_config = config.get("cover", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "cover", cover_config):
            cover_check = {
                "found": False,
                "message": "Cover check is disabled",
                "details": [],
            }
            print(f"   Result: {cover_check['message']}")
            return cover_check
        
        if cover_config.get("enabled", True):
            format_config = cover_config.get("format", {})
            if not format_config:
                raise ValueError("Cover format configuration not found in config file")
            required_font = format_config.get("font")
            if not required_font:
                raise ValueError("Cover font not specified in config file (cover.format.font)")
            cover_check = check_cover_font(docx_path, required_font=required_font)
            print(f"   Result: {cover_check['message']}")

            if cover_check["found"]:
                print()
                print("   WARNING: Cover font is incorrect!")
                if cover_check["details"]:
                    details = cover_check["details"]
                    print(f"   Found {len(details)} paragraph(s) with incorrect font")
                    if len(details) > 20:
                        print("   First 10 locations:")
                        for detail in details[:10]:
                            fonts_str = ", ".join(detail["fonts"])
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): Fonts: {fonts_str}, Required: {detail['required_font']}"
                            )
                        print("   ...")
                    else:
                        print("   Locations:")
                        for detail in details:
                            fonts_str = ", ".join(detail["fonts"])
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): Fonts: {fonts_str}, Required: {detail['required_font']}"
                            )
            else:
                print("   ✓ Cover font is correct")
            return cover_check
        else:
            cover_check = {
                "found": False,
                "message": "Cover check is disabled",
                "details": [],
            }
            print(f"   Result: {cover_check['message']}")
            return cover_check
    except Exception as e:
        print(f"   Error loading cover config: {e}")
        return {"found": False, "message": f"Error: {e}", "details": []}


def run_page_numbers_check(docx_path, config_loader=None):
    """Run page numbers check."""
    print("Checking page numbers format and style...")
    try:
        if config_loader is None:
            raise ValueError("ConfigLoader instance is required. Please pass config_loader parameter.")
        config = config_loader.config
        page_numbers_config = config.get("page_numbers", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "page_numbers", page_numbers_config):
            page_numbers_result = {
                "format": {"found": False, "message": "Page numbers check is disabled", "details": []},
                "style": {"found": False, "message": "Page numbers check is disabled", "details": []},
            }
            print(f"   Result: Page numbers check is disabled")
            return page_numbers_result
        
        if page_numbers_config.get("enabled", True):
            page_numbers_result = check_page_numbers(docx_path, page_numbers_config)
            
            # Print format check results
            format_result = page_numbers_result.get("format", {})
            print(f"   Format: {format_result.get('message', 'N/A')}")
            
            if format_result.get("found"):
                print("   WARNING: Page number format issues found!")
                if format_result.get("details"):
                    details = format_result["details"]
                    print(f"   Found {len(details)} format issue(s)")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            print(f"      - {detail.get('footer_file', 'N/A')}: {detail.get('issue', 'N/A')}")
                        print("   ...")
                    else:
                        for detail in details:
                            print(f"      - {detail.get('footer_file', 'N/A')}: {detail.get('issue', 'N/A')}")
            else:
                print("   ✓ Page number format is correct")
            
            print()
            
            # Print style check results
            style_result = page_numbers_result.get("style", {})
            print(f"   Style: {style_result.get('message', 'N/A')}")
            
            if style_result.get("found"):
                print("   WARNING: Page number style issues found!")
                if style_result.get("details"):
                    details = style_result["details"]
                    print(f"   Found {len(details)} style issue(s)")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            print(f"      - {detail.get('footer_file', 'N/A')}: {detail.get('issue', 'N/A')}")
                        print("   ...")
                    else:
                        for detail in details:
                            print(f"      - {detail.get('footer_file', 'N/A')}: {detail.get('issue', 'N/A')}")
            else:
                print("   ✓ Page number style is correct")
            
            return page_numbers_result
        else:
            page_numbers_result = {
                "format": {"found": False, "message": "Page numbers check is disabled", "details": []},
                "style": {"found": False, "message": "Page numbers check is disabled", "details": []},
            }
            print(f"   Result: Page numbers check is disabled")
            return page_numbers_result
    except Exception as e:
        print(f"   Error loading page numbers config: {e}")
        return {
            "format": {"found": False, "message": f"Error: {e}", "details": []},
            "style": {"found": False, "message": f"Error: {e}", "details": []},
        }


def run_toc_check(docx_path):
    """Run table of contents check with parallel execution."""
    print("Checking table of contents (order, format, numbering, page accuracy)...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        toc_config = config.get("table_of_contents", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "table_of_contents", toc_config):
            toc_check = {
                "order": {"found": False, "message": "TOC check is disabled"},
                "format": {"found": False, "message": "TOC check is disabled"},
                "numbering": {"found": False, "message": "TOC check is disabled"},
                "page_accuracy": {"found": False, "message": "TOC check is disabled"},
            }
            print(f"   Result: TOC check is disabled")
            return toc_check

        if toc_config.get("enabled", True):
            # All TOC checks run in parallel: order, format, numbering, page accuracy
            toc_results = check_toc_complete(docx_path, toc_config)

            toc_order_check = toc_results.get("order", {})
            print(f"   Order: {toc_order_check.get('message', 'N/A')}")

            if toc_order_check.get("found"):
                print("   WARNING: TOC sections are not in correct order!")
                if toc_order_check.get("details"):
                    for detail in toc_order_check["details"]:
                        print(f"      - {detail}")
            else:
                print("   ✓ TOC sections are in correct order")

            print()
            toc_format_check = toc_results.get("format", {})
            print(f"   Format: {toc_format_check.get('message', 'N/A')}")

            if toc_format_check.get("found"):
                print("   WARNING: Table of contents format issues found!")
                if toc_format_check.get("details"):
                    details = toc_format_check["details"]
                    print(f"   Found {len(details)} paragraph(s) with format issues")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            issues_str = "; ".join(detail["issues"])
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}, Style {detail['style']}): {issues_str}"
                            )
                    else:
                        for detail in details:
                            issues_str = "; ".join(detail["issues"])
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}, Style {detail['style']}): {issues_str}"
                            )

            toc_numbering_check = toc_results.get("numbering", {})
            print(
                f"   Numbering continuity: {toc_numbering_check.get('message', 'N/A')}"
            )

            if toc_numbering_check.get("found"):
                print("   WARNING: Numbering continuity issues found!")
                if toc_numbering_check.get("details"):
                    details = toc_numbering_check["details"]
                    print(f"   Found {len(details)} numbering issue(s)")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['numbering']} - {detail['issue']}"
                            )
                    else:
                        for detail in details:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['numbering']} - {detail['issue']}"
                            )

            toc_page_check = toc_results.get("page_accuracy", {})
            print(f"   Page accuracy: {toc_page_check.get('message', 'N/A')}")

            if toc_page_check.get("found"):
                print("   WARNING: Page number accuracy issues found!")
                if toc_page_check.get("details"):
                    details = toc_page_check["details"]
                    print(f"   Found {len(details)} page number issue(s)")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            print(
                                f"      - Paragraph {detail['paragraph']}: {detail['issue']}"
                            )
                    else:
                        for detail in details:
                            print(
                                f"      - Paragraph {detail['paragraph']}: {detail['issue']}"
                            )
        else:
            print("   Table of contents check is disabled")
            toc_results = {
                "order": {"found": False, "message": "Disabled", "details": []},
                "format": {"found": False, "message": "Disabled", "details": []},
                "numbering": {"found": False, "message": "Disabled", "details": []},
                "page_accuracy": {"found": False, "message": "Disabled", "details": []},
            }
    except Exception as e:
        print(f"   Error checking table of contents: {e}")
        toc_results = {
            "order": {"found": False, "message": f"Error: {e}", "details": []},
            "format": {"found": False, "message": f"Error: {e}", "details": []},
            "numbering": {"found": False, "message": f"Error: {e}", "details": []},
            "page_accuracy": {"found": False, "message": f"Error: {e}", "details": []},
        }

    return toc_results


def run_figure_list_check(docx_path):
    """Run figure list check."""
    print("Checking figure list (format, numbering, page accuracy)...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        figure_list_config = config.get("figure_list", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "figure_list", figure_list_config):
            figure_list_results = {
                "format": {"found": False, "message": "Figure list check is disabled", "details": []},
                "numbering": {"found": False, "message": "Figure list check is disabled", "details": []},
                "page_accuracy": {"found": False, "message": "Figure list check is disabled", "details": []},
            }
            print(f"   Result: Figure list check is disabled")
            return figure_list_results

        if figure_list_config.get("enabled", True):
            figure_list_results = check_toc_all(
                docx_path, "figure_list", figure_list_config
            )

            figure_list_format_check = figure_list_results.get("format", {})
            print(f"   Format: {figure_list_format_check.get('message', 'N/A')}")

            if figure_list_format_check.get("found"):
                print("   WARNING: Figure list format issues found!")
                if figure_list_format_check.get("details"):
                    details = figure_list_format_check["details"]
                    print(f"   Found {len(details)} paragraph(s) with format issues")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            issues_str = "; ".join(detail["issues"])
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}, Style {detail['style']}): {issues_str}"
                            )
                    else:
                        for detail in details:
                            issues_str = "; ".join(detail["issues"])
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}, Style {detail['style']}): {issues_str}"
                            )

            figure_list_numbering_check = figure_list_results.get("numbering", {})
            print(
                f"   Numbering continuity: {figure_list_numbering_check.get('message', 'N/A')}"
            )

            if figure_list_numbering_check.get("found"):
                print("   WARNING: Numbering continuity issues found!")
                if figure_list_numbering_check.get("details"):
                    details = figure_list_numbering_check["details"]
                    print(f"   Found {len(details)} numbering issue(s)")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['numbering']} - {detail['issue']}"
                            )
                    else:
                        for detail in details:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['numbering']} - {detail['issue']}"
                            )

            figure_list_page_check = figure_list_results.get("page_accuracy", {})
            print(f"   Page accuracy: {figure_list_page_check.get('message', 'N/A')}")

            if figure_list_page_check.get("found"):
                print("   WARNING: Page number accuracy issues found!")
                if figure_list_page_check.get("details"):
                    details = figure_list_page_check["details"]
                    print(f"   Found {len(details)} page number issue(s)")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            print(
                                f"      - Paragraph {detail['paragraph']}: {detail['issue']}"
                            )
                    else:
                        for detail in details:
                            print(
                                f"      - Paragraph {detail['paragraph']}: {detail['issue']}"
                            )
        else:
            print("   Figure list check is disabled")
            figure_list_results = {
                "format": {"found": False, "message": "Disabled", "details": []},
                "numbering": {"found": False, "message": "Disabled", "details": []},
                "page_accuracy": {"found": False, "message": "Disabled", "details": []},
            }
    except Exception as e:
        print(f"   Error checking figure list: {e}")
        figure_list_results = {
            "format": {"found": False, "message": f"Error: {e}", "details": []},
            "numbering": {"found": False, "message": f"Error: {e}", "details": []},
            "page_accuracy": {"found": False, "message": f"Error: {e}", "details": []},
        }

    return figure_list_results


def run_table_list_check(docx_path):
    """Run table list check."""
    print("Checking table list (format, numbering, page accuracy)...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        table_list_config = config.get("table_list", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "table_list", table_list_config):
            table_list_results = {
                "format": {"found": False, "message": "Table list check is disabled", "details": []},
                "numbering": {"found": False, "message": "Table list check is disabled", "details": []},
                "page_accuracy": {"found": False, "message": "Table list check is disabled", "details": []},
            }
            print(f"   Result: Table list check is disabled")
            return table_list_results

        if table_list_config.get("enabled", True):
            table_list_results = check_toc_all(
                docx_path, "table_list", table_list_config
            )

            table_list_format_check = table_list_results.get("format", {})
            print(f"   Format: {table_list_format_check.get('message', 'N/A')}")

            if table_list_format_check.get("found"):
                print("   WARNING: Table list format issues found!")
                if table_list_format_check.get("details"):
                    details = table_list_format_check["details"]
                    print(f"   Found {len(details)} paragraph(s) with format issues")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            issues_str = "; ".join(detail["issues"])
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}, Style {detail['style']}): {issues_str}"
                            )
                    else:
                        for detail in details:
                            issues_str = "; ".join(detail["issues"])
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}, Style {detail['style']}): {issues_str}"
                            )

            table_list_numbering_check = table_list_results.get("numbering", {})
            print(
                f"   Numbering continuity: {table_list_numbering_check.get('message', 'N/A')}"
            )

            if table_list_numbering_check.get("found"):
                print("   WARNING: Numbering continuity issues found!")
                if table_list_numbering_check.get("details"):
                    details = table_list_numbering_check["details"]
                    print(f"   Found {len(details)} numbering issue(s)")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['numbering']} - {detail['issue']}"
                            )
                    else:
                        for detail in details:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['numbering']} - {detail['issue']}"
                            )

            table_list_page_check = table_list_results.get("page_accuracy", {})
            print(f"   Page accuracy: {table_list_page_check.get('message', 'N/A')}")

            if table_list_page_check.get("found"):
                print("   WARNING: Page number accuracy issues found!")
                if table_list_page_check.get("details"):
                    details = table_list_page_check["details"]
                    print(f"   Found {len(details)} page number issue(s)")
                    if len(details) > 10:
                        print("   First 5 locations:")
                        for detail in details[:5]:
                            print(
                                f"      - Paragraph {detail['paragraph']}: {detail['issue']}"
                            )
                    else:
                        for detail in details:
                            print(
                                f"      - Paragraph {detail['paragraph']}: {detail['issue']}"
                            )
        else:
            print("   Table list check is disabled")
            table_list_results = {
                "format": {"found": False, "message": "Disabled", "details": []},
                "numbering": {"found": False, "message": "Disabled", "details": []},
                "page_accuracy": {"found": False, "message": "Disabled", "details": []},
            }
    except Exception as e:
        print(f"   Error checking table list: {e}")
        table_list_results = {
            "format": {"found": False, "message": f"Error: {e}", "details": []},
            "numbering": {"found": False, "message": f"Error: {e}", "details": []},
            "page_accuracy": {"found": False, "message": f"Error: {e}", "details": []},
        }

    return table_list_results


def run_headers_check(docx_path):
    """Run headers check."""
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        headers_config = config.get("headers", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "headers", headers_config):
            return {
                "headers": [],
                "consistency": {"consistent": True, "message": "Headers check is disabled"},
                "usage_info": None,
            }
    except Exception as e:
        print(f"   Error loading headers config: {e}")
    
    print("Analyzing header/footer usage...")
    usage_info = analyze_header_footer_usage(docx_path)
    print()

    print("Extracting headers...")
    headers = extract_headers_from_docx(docx_path, usage_info)
    print(f"   Extracted {len(headers)} header(s) with content")
    print()

    if headers:
        print("   Header details:")
        for i, header in enumerate(headers, 1):
            print(f"   Header {i} ({header['file']}):")
            print(
                f"      Content: {header['text'][:100]}..."
                if len(header["text"]) > 100
                else f"      Content: {header['text']}"
            )
            if header.get("page_info"):
                page_ranges = []
                for info in header["page_info"]:
                    page_ranges.append(
                        f"Page ~{info['estimated_start_page']} (Section {info['section']}, Para {info['start_para']})"
                    )
                if page_ranges:
                    print(f"      Location: {', '.join(page_ranges)}")
            print()

    print("Checking header consistency...")
    consistency = check_header_consistency(headers)
    print(f"   Result: {consistency['message']}")

    if not consistency["consistent"]:
        print()
        print("   WARNING: Headers are not consistent!")
        if "variations" in consistency:
            print("   Header variations found:")
            for header_text, count in consistency["variations"].items():
                print(
                    f"      - '{header_text[:80]}...' (appears {count} time(s))"
                    if len(header_text) > 80
                    else f"      - '{header_text}' (appears {count} time(s))"
                )
    else:
        print("   ✓ Headers are consistent")

    return {"headers": headers, "consistency": consistency, "usage_info": usage_info}


def run_footers_check(docx_path, usage_info=None):
    """Run footers check."""
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        footers_config = config.get("footers", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "footers", footers_config):
            return {
                "footers": [],
                "consistency": {"consistent": True, "message": "Footers check is disabled"},
            }
    except Exception as e:
        print(f"   Error loading footers config: {e}")
    
    if usage_info is None:
        print("Analyzing header/footer usage...")
        usage_info = analyze_header_footer_usage(docx_path)
        print()

    print("Extracting footers...")
    footers = extract_footers_from_docx(docx_path, usage_info)
    print(f"   Extracted {len(footers)} footer(s) with content")
    print()

    if footers:
        print("   Footer details:")
        for i, footer in enumerate(footers, 1):
            print(f"   Footer {i} ({footer['file']}):")
            print(
                f"      Content: {footer['text'][:100]}..."
                if len(footer["text"]) > 100
                else f"      Content: {footer['text']}"
            )
            if footer.get("page_info"):
                page_ranges = []
                for info in footer["page_info"]:
                    page_ranges.append(
                        f"Page ~{info['estimated_start_page']} (Section {info['section']}, Para {info['start_para']})"
                    )
                if page_ranges:
                    print(f"      Location: {', '.join(page_ranges)}")
            print()

    print("Checking footer consistency...")
    footer_consistency = check_footer_consistency(footers)
    print(f"   Result: {footer_consistency['message']}")

    if not footer_consistency["consistent"]:
        print()
        print("   WARNING: Footers are not consistent!")
        if "variations" in footer_consistency:
            print("   Footer variations found:")
            for footer_text, count in footer_consistency["variations"].items():
                print(
                    f"      - '{footer_text[:80]}...' (appears {count} time(s))"
                    if len(footer_text) > 80
                    else f"      - '{footer_text}' (appears {count} time(s))"
                )
    else:
        print("   ✓ Footers are consistent")

    return {"footers": footers, "consistency": footer_consistency}


def run_empty_lines_check(docx_path, config_loader=None):
    """Run empty lines check."""
    print("Checking for consecutive empty lines...")
    try:
        if config_loader is None:
            import os
            config_path = os.environ.get('CUSTOM_CONFIG_PATH')
            if not config_path:
                raise ValueError("Configuration file path is required. Please specify a config file using --config option.")
            config_loader = ConfigLoader(config_path)
        config = config_loader.load()
        
        # 从 body_paragraphs.empty_lines 配置中获取空行检查设置
        body_paragraphs_config = config.get("body_paragraphs", {})
        empty_lines_config = body_paragraphs_config.get("empty_lines", {})
        
        # Check if check is enabled
        if not _is_check_enabled(config_loader, "body_paragraphs", body_paragraphs_config):
            empty_lines_check = {
                "found": False,
                "message": "Empty lines check is disabled",
                "details": [],
            }
            print(f"   Result: {empty_lines_check['message']}")
            return empty_lines_check
        
        # 检查是否启用了空行检查
        check_enabled = (
            body_paragraphs_config.get("enabled", True) and 
            empty_lines_config.get("consecutive", False)
        )
        
        if check_enabled:
            max_consecutive = empty_lines_config.get("max_consecutive")
            if max_consecutive is None:
                raise ValueError("max_consecutive not specified in config file (body_paragraphs.empty_lines.max_consecutive or empty_lines.max_consecutive)")
            empty_lines_check = check_consecutive_empty_lines(
                docx_path, max_consecutive=max_consecutive
            )
            print(f"   Result: {empty_lines_check['message']}")
        else:
            empty_lines_check = {
                "found": False,
                "message": "Empty lines check is disabled",
                "details": [],
            }
            print(f"   Result: {empty_lines_check['message']}")
    except Exception as e:
        print(f"   Error loading empty lines config: {e}")
        empty_lines_check = {"found": False, "message": f"Error: {e}", "details": []}

    if empty_lines_check["found"]:
        print()
        print("   警告：发现连续空行！")
        if empty_lines_check["details"]:
            details = empty_lines_check["details"]
            print(f"   发现 {len(details)} 组连续空行")
            if len(details) > 20:
                print("   前 10 个位置：")
                for detail in details[:10]:
                    page_info = ""
                    if (
                        "estimated_start_page" in detail
                        and "estimated_end_page" in detail
                    ):
                        if (
                            detail["estimated_start_page"]
                            == detail["estimated_end_page"]
                        ):
                            page_info = f" (第 ~{detail['estimated_start_page']} 页)"
                        else:
                            page_info = f" (第 ~{detail['estimated_start_page']}-{detail['estimated_end_page']} 页)"
                    print(
                        f"      - 段落 {detail['start']} 到 {detail['end']}：{detail['count']} 个连续空行{page_info}"
                    )
                print("   ...")
            else:
                print("   位置：")
                for detail in details:
                    page_info = ""
                    if (
                        "estimated_start_page" in detail
                        and "estimated_end_page" in detail
                    ):
                        if (
                            detail["estimated_start_page"]
                            == detail["estimated_end_page"]
                        ):
                            page_info = f" (第 ~{detail['estimated_start_page']} 页)"
                        else:
                            page_info = f" (第 ~{detail['estimated_start_page']}-{detail['estimated_end_page']} 页)"
                    print(
                        f"      - 段落 {detail['start']} 到 {detail['end']}：{detail['count']} 个连续空行{page_info}"
                    )
    else:
        print("   ✓ 未发现连续空行")

    if "total_paragraphs" in empty_lines_check:
        print(
            f"   Total paragraphs in document: {empty_lines_check['total_paragraphs']}"
        )

    return empty_lines_check


def run_figures_check(docx_path):
    """Run figures check."""
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        # Note: figures check doesn't have its own config section, 
        # it's part of captions, so we check captions
        captions_config = config.get("captions", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "captions", captions_config):
            figure_check = {
                "found": False,
                "message": "Figures check is disabled",
                "details": [],
            }
            print(f"   Result: {figure_check['message']}")
            return figure_check
    except Exception as e:
        print(f"   Error loading config: {e}")
    
    print("Checking figure empty lines...")
    figure_check = check_figure_empty_lines(docx_path)
    print(f"   Result: {figure_check['message']}")

    if figure_check["found"]:
        print()
        print("   WARNING: Figures with empty lines before or after found!")
        if figure_check["details"]:
            details = figure_check["details"]
            print(f"   Found {len(details)} figure(s) with empty lines")
            if len(details) > 20:
                print("   First 10 locations:")
                for detail in details[:10]:
                    before = "Yes" if detail["before_empty"] else "No"
                    after = "Yes" if detail["after_empty"] else "No"
                    print(
                        f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): Before={before}, After={after}"
                    )
                print("   ...")
            else:
                print("   Locations:")
                for detail in details:
                    before = "Yes" if detail["before_empty"] else "No"
                    after = "Yes" if detail["after_empty"] else "No"
                    print(
                        f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): Before={before}, After={after}"
                    )
    else:
        print("   ✓ No figures with empty lines before or after found")

    return figure_check


def run_captions_check(docx_path):
    """Run captions check."""
    print("Checking caption alignment...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        captions_config = config.get("captions", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "captions", captions_config):
            caption_check = {
                "found": False,
                "message": "Caption check is disabled",
                "details": [],
            }
            print(f"   Result: {caption_check['message']}")
            return caption_check
        
        if captions_config.get("enabled", True):
            figure_config = captions_config.get("figure", {})
            if not figure_config:
                raise ValueError("Figure caption configuration not found in config file")
            format_config = figure_config.get("format", {})
            if not format_config:
                raise ValueError("Figure caption format configuration not found in config file")
            required_alignment = format_config.get("alignment")
            if not required_alignment:
                raise ValueError("Figure caption alignment not specified in config file (captions.figure.format.alignment)")
            caption_check = check_caption_alignment(
                docx_path, required_alignment=required_alignment
            )
            print(f"   Result: {caption_check['message']}")
        else:
            caption_check = {
                "found": False,
                "message": "Caption check is disabled",
                "details": [],
            }
            print(f"   Result: {caption_check['message']}")
    except Exception as e:
        print(f"   Error loading caption config: {e}")
        caption_check = {"found": False, "message": f"Error: {e}", "details": []}

    if caption_check["found"]:
        print()
        required_alignment_text = (
            caption_check.get("details", [{}])[0].get("required_alignment", "center")
            if caption_check.get("details")
            else "center"
        )
        alignment_map = {
            "center": "居中",
            "left": "左对齐",
            "right": "右对齐",
            "justify": "两端对齐",
        }
        alignment_display = alignment_map.get(
            required_alignment_text, required_alignment_text
        )
        print(f"   WARNING: Captions not {alignment_display} found!")
        if caption_check["details"]:
            details = caption_check["details"]
            print(f"   Found {len(details)} caption(s) not {alignment_display}")
            if len(details) > 20:
                print("   First 10 locations:")
                for detail in details[:10]:
                    alignment_map = {
                        "left": "Left",
                        "right": "Right",
                        "justify": "Justify",
                        "center": "Center",
                    }
                    alignment_text = alignment_map.get(
                        detail["alignment"], detail["alignment"]
                    )
                    print(
                        f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['type']} - {alignment_text}"
                    )
                print("   ...")
            else:
                print("   Locations:")
                for detail in details:
                    alignment_map = {
                        "left": "Left",
                        "right": "Right",
                        "justify": "Justify",
                        "center": "Center",
                    }
                    alignment_text = alignment_map.get(
                        detail["alignment"], detail["alignment"]
                    )
                    print(
                        f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['type']} - {alignment_text}"
                    )
    else:
        print("   ✓ All captions are centered")

    return caption_check


def run_references_check(docx_path, config_loader=None):
    """Run references check."""
    print("Checking references format and citations...")
    try:
        if config_loader is None:
            raise ValueError("ConfigLoader instance is required. Please pass config_loader parameter.")
        config = config_loader.config
        references_config = config.get("references", {})
        
        # Check if check is enabled (with priority control)
        if not _is_check_enabled(config_loader, "references", references_config):
            references_check = {
                "found": False,
                "message": "References check is disabled",
                "details": [],
            }
            print(f"   Result: {references_check['message']}")
            return references_check
        
        if references_config.get("enabled", True):
            references_check = check_unreferenced_references(docx_path, config=config)

            if references_check.get("error"):
                print(f"   ✗ Error: {references_check['message']}")
                return references_check

            total_refs = len(references_check.get("references", []))
            cited_refs = len(references_check.get("citations", []))
            unreferenced = len(references_check.get("unreferenced", []))
            duplicates = len(references_check.get("duplicates", []))

            print(f"   Total references: {total_refs}")
            print(f"   Cited references: {cited_refs}")
            print(f"   Unreferenced references: {unreferenced}")
            print(f"   Duplicate references: {duplicates}")

            issues_found = unreferenced > 0 or duplicates > 0

            if issues_found:
                print()
                print("   WARNING: Reference issues found!")
                if unreferenced > 0:
                    print(f"   Found {unreferenced} unreferenced reference(s)")
                if duplicates > 0:
                    print(f"   Found {duplicates} duplicate reference(s)")
            else:
                print("   ✓ All references are properly cited and unique")

            # Convert to standard format
            if issues_found:
                if unreferenced > 0 and duplicates > 0:
                    message = f"发现 {unreferenced} 个未被引用的参考文献和 {duplicates} 组重复的参考文献"
                elif unreferenced > 0:
                    message = f"发现 {unreferenced} 个未被引用的参考文献"
                else:
                    message = f"发现 {duplicates} 组重复的参考文献"
            else:
                message = "所有参考文献均已被正确引用且唯一"
            
            return {
                "found": issues_found,
                "message": message,
                "details": references_check,
                "total_references": total_refs,
                "cited_references": cited_refs,
                "unreferenced_count": unreferenced,
                "duplicates_count": duplicates
            }
        else:
            print("   References check is disabled")
            return {"enabled": False, "message": "References check is disabled in configuration"}

    except Exception as e:
        error_msg = f"Error during references check: {str(e)}"
        print(f"   ✗ {error_msg}")
        return {
            "found": True,
            "message": error_msg,
            "details": {},
            "error": True
        }


# Body paragraphs check functions moved to body_paragraphs.py
