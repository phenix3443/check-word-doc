#!/usr/bin/env python3
"""
Main entry point for document format checking.
"""

from pathlib import Path
import sys
import argparse

from structure import analyze_document_structure
from functions import (
    run_cover_check,
    run_toc_check,
    run_figure_list_check,
    run_table_list_check,
    run_headers_check,
    run_footers_check,
    run_empty_lines_check,
    run_figures_check,
    run_captions_check,
    run_references_check,
    run_page_numbers_check,
    run_chinese_spacing_check,
    run_chinese_quotes_check,
)
from report import generate_markdown_report
from config_loader import ConfigLoader
import os


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Check Word document format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all items
  python3 check.py document.docx

  # Check only table of contents
  python3 check.py document.docx --check toc

  # Check multiple items
  python3 check.py document.docx --check toc --check cover

  # List available check items
  python3 check.py --list-checks
        """,
    )

    parser.add_argument(
        "docx_path",
        nargs="?",
        type=str,
        help="Path to the Word document (.docx file)",
    )

    parser.add_argument(
        "--check",
        "-c",
        action="append",
        dest="checks",
        choices=[
            "all",
            "cover",
            "toc",
            "figure_list",
            "table_list",
            "headers",
            "footers",
            "empty_lines",
            "figures",
            "captions",
            "references",
            "page_numbers",
            "chinese_spacing",
            "chinese_quotes",
        ],
        help="Specific check item to run (can be specified multiple times)",
    )

    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="List all available check items and exit",
    )

    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip generating markdown report",
    )

    parser.add_argument(
        "--config",
        "-C",
        type=str,
        required=True,
        help="Path to configuration file (YAML format, required)",
    )

    return parser.parse_args()


def list_available_checks():
    """List all available check items."""
    checks = {
        "all": "Run all checks (default)",
        "cover": "Check cover page font",
        "toc": "Check table of contents (format, numbering, page accuracy)",
        "figure_list": "Check figure list (format, numbering, page accuracy)",
        "table_list": "Check table list (format, numbering, page accuracy)",
        "headers": "Check header consistency",
        "footers": "Check footer consistency",
        "page_numbers": "Check page numbers format and style",
        "empty_lines": "Check consecutive empty lines",
        "figures": "Check figure empty lines",
        "captions": "Check caption alignment",
        "references": "Check references format and citations",
        "chinese_spacing": "Check Chinese spacing (no spaces between Chinese characters)",
        "chinese_quotes": "Check Chinese quotes format",
    }

    print("Available check items:")
    print("=" * 60)
    for check_id, description in checks.items():
        print(f"  {check_id:15} - {description}")
    print()


def main():
    args = parse_arguments()

    if args.list_checks:
        list_available_checks()
        sys.exit(0)

    if not args.docx_path:
        print("Error: Please provide the document path")
        print("Usage: python3 check.py <docx_path> [--check <item>]")
        print("Use --help for more information")
        sys.exit(1)

    # Set custom config path if provided
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Configuration file not found: {config_path}")
            sys.exit(1)
        # Set environment variable for config path
        os.environ['CUSTOM_CONFIG_PATH'] = str(config_path.absolute())
        print(f"Using custom configuration: {config_path}")
        print()

    docx_path = Path(args.docx_path)

    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        sys.exit(1)

    checks_to_run = args.checks if args.checks else ["all"]
    if "all" in checks_to_run:
        checks_to_run = [
            "cover",
            "toc",
            "figure_list",
            "table_list",
            "headers",
            "footers",
            "empty_lines",
            "figures",
            "captions",
            "references",
            "page_numbers",
            "chinese_spacing",
            "chinese_quotes",
        ]

    print("=" * 80)
    print(f"Checking document format: {docx_path.name}")
    if checks_to_run != ["all"]:
        print(f"Selected checks: {', '.join(checks_to_run)}")
    print("=" * 80)
    print()

    # Load configuration
    config_loader = ConfigLoader(str(config_path))
    config_loader.load()

    structure = None
    if any(check in checks_to_run for check in ["headers", "footers", "all"]):
        print("Analyzing document structure...")
        structure = analyze_document_structure(docx_path)
        print(f"   Found {len(structure['headers'])} header file(s)")
        print(f"   Found {len(structure['footers'])} footer file(s)")
        print()

    results = {}
    step = 1

    if "cover" in checks_to_run:
        print(f"{step}. ", end="")
        results["cover"] = run_cover_check(docx_path)
        step += 1
        print()

    if "toc" in checks_to_run:
        print(f"{step}. ", end="")
        results["toc"] = run_toc_check(docx_path)
        step += 1
        print()

    if "figure_list" in checks_to_run:
        print(f"{step}. ", end="")
        results["figure_list"] = run_figure_list_check(docx_path)
        step += 1
        print()

    if "table_list" in checks_to_run:
        print(f"{step}. ", end="")
        results["table_list"] = run_table_list_check(docx_path)
        step += 1
        print()

    usage_info = None
    if "headers" in checks_to_run:
        print(f"{step}. ", end="")
        headers_result = run_headers_check(docx_path)
        results["headers"] = headers_result
        usage_info = headers_result.get("usage_info")
        step += 1
        print()

    if "footers" in checks_to_run:
        print(f"{step}. ", end="")
        results["footers"] = run_footers_check(docx_path, usage_info)
        step += 1
        print()

    if "empty_lines" in checks_to_run:
        print(f"{step}. ", end="")
        results["empty_lines"] = run_empty_lines_check(docx_path, config_loader)
        step += 1
        print()

    if "figures" in checks_to_run:
        print(f"{step}. ", end="")
        results["figures"] = run_figures_check(docx_path)
        step += 1
        print()

    if "captions" in checks_to_run:
        print(f"{step}. ", end="")
        results["captions"] = run_captions_check(docx_path)
        step += 1
        print()

    if "references" in checks_to_run:
        print(f"{step}. ", end="")
        results["references"] = run_references_check(docx_path, config_loader)
        step += 1
        print()

    if "page_numbers" in checks_to_run:
        print(f"{step}. ", end="")
        results["page_numbers"] = run_page_numbers_check(docx_path, config_loader)
        step += 1
        print()

    if "chinese_spacing" in checks_to_run:
        print(f"{step}. ", end="")
        results["chinese_spacing"] = run_chinese_spacing_check(docx_path, config_loader)
        step += 1
        print()

    if "chinese_quotes" in checks_to_run:
        print(f"{step}. ", end="")
        results["chinese_quotes"] = run_chinese_quotes_check(docx_path, config_loader)
        step += 1
        print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    for check_name in checks_to_run:
        check_result = results.get(check_name)
        if check_result is None:
            continue

        if check_name == "cover":
            print(f"Cover font: {'✓ PASS' if not check_result.get('found') else '✗ FAIL'}")
        elif check_name == "toc":
            toc_order = check_result.get("order", {})
            toc_format = check_result.get("format", {})
            toc_numbering = check_result.get("numbering", {})
            toc_page = check_result.get("page_accuracy", {})
            print(f"TOC order: {'✓ PASS' if not toc_order.get('found') else '✗ FAIL'}")
            print(f"TOC format: {'✓ PASS' if not toc_format.get('found') else '✗ FAIL'}")
            print(f"TOC numbering: {'✓ PASS' if not toc_numbering.get('found') else '✗ FAIL'}")
            print(f"TOC page accuracy: {'✓ PASS' if not toc_page.get('found') else '✗ FAIL'}")
        elif check_name == "figure_list":
            fig_format = check_result.get("format", {})
            fig_numbering = check_result.get("numbering", {})
            fig_page = check_result.get("page_accuracy", {})
            print(f"Figure list format: {'✓ PASS' if not fig_format.get('found') else '✗ FAIL'}")
            print(f"Figure list numbering: {'✓ PASS' if not fig_numbering.get('found') else '✗ FAIL'}")
            print(f"Figure list page accuracy: {'✓ PASS' if not fig_page.get('found') else '✗ FAIL'}")
        elif check_name == "table_list":
            tbl_format = check_result.get("format", {})
            tbl_numbering = check_result.get("numbering", {})
            tbl_page = check_result.get("page_accuracy", {})
            print(f"Table list format: {'✓ PASS' if not tbl_format.get('found') else '✗ FAIL'}")
            print(f"Table list numbering: {'✓ PASS' if not tbl_numbering.get('found') else '✗ FAIL'}")
            print(f"Table list page accuracy: {'✓ PASS' if not tbl_page.get('found') else '✗ FAIL'}")
        elif check_name == "headers":
            headers_consistency = check_result.get("consistency", {})
            print(f"Header consistency: {'✓ PASS' if headers_consistency.get('consistent') else '✗ FAIL'}")
        elif check_name == "footers":
            footers_consistency = check_result.get("consistency", {})
            print(f"Footer consistency: {'✓ PASS' if footers_consistency.get('consistent') else '✗ FAIL'}")
        elif check_name == "empty_lines":
            print(f"Consecutive empty lines: {'✓ PASS' if not check_result.get('found') else '✗ FAIL'}")
        elif check_name == "figures":
            print(f"Figure empty lines: {'✓ PASS' if not check_result.get('found') else '✗ FAIL'}")
        elif check_name == "captions":
            print(f"Caption alignment: {'✓ PASS' if not check_result.get('found') else '✗ FAIL'}")
        elif check_name == "references":
            print(f"References check: {'✓ PASS' if not check_result.get('found') else '✗ FAIL'}")
        elif check_name == "chinese_spacing":
            print(f"Chinese spacing: {'✓ PASS' if not check_result.get('found') else '✗ FAIL'}")
        elif check_name == "chinese_quotes":
            print(f"Chinese quotes: {'✓ PASS' if not check_result.get('found') else '✗ FAIL'}")

    issues = []
    for check_name in checks_to_run:
        check_result = results.get(check_name)
        if check_result is None:
            continue

        if check_name == "cover" and check_result.get("found"):
            issues.append(f"Cover font: {check_result.get('message', 'N/A')}")
        elif check_name == "toc":
            toc_order = check_result.get("order", {})
            toc_format = check_result.get("format", {})
            toc_numbering = check_result.get("numbering", {})
            toc_page = check_result.get("page_accuracy", {})
            if toc_order.get("found"):
                issues.append(f"TOC order: {toc_order.get('message', 'N/A')}")
            if toc_format.get("found"):
                issues.append(f"TOC format: {toc_format.get('message', 'N/A')}")
            if toc_numbering.get("found"):
                issues.append(f"TOC numbering: {toc_numbering.get('message', 'N/A')}")
            if toc_page.get("found"):
                issues.append(f"TOC page accuracy: {toc_page.get('message', 'N/A')}")
        elif check_name == "figure_list":
            fig_format = check_result.get("format", {})
            fig_numbering = check_result.get("numbering", {})
            fig_page = check_result.get("page_accuracy", {})
            if fig_format.get("found"):
                issues.append(f"Figure list format: {fig_format.get('message', 'N/A')}")
            if fig_numbering.get("found"):
                issues.append(f"Figure list numbering: {fig_numbering.get('message', 'N/A')}")
            if fig_page.get("found"):
                issues.append(f"Figure list page accuracy: {fig_page.get('message', 'N/A')}")
        elif check_name == "table_list":
            tbl_format = check_result.get("format", {})
            tbl_numbering = check_result.get("numbering", {})
            tbl_page = check_result.get("page_accuracy", {})
            if tbl_format.get("found"):
                issues.append(f"Table list format: {tbl_format.get('message', 'N/A')}")
            if tbl_numbering.get("found"):
                issues.append(f"Table list numbering: {tbl_numbering.get('message', 'N/A')}")
            if tbl_page.get("found"):
                issues.append(f"Table list page accuracy: {tbl_page.get('message', 'N/A')}")
        elif check_name == "headers":
            headers_consistency = check_result.get("consistency", {})
            if not headers_consistency.get("consistent"):
                issues.append(f"Headers: {headers_consistency.get('message', 'N/A')}")
        elif check_name == "footers":
            footers_consistency = check_result.get("consistency", {})
            if not footers_consistency.get("consistent"):
                issues.append(f"Footers: {footers_consistency.get('message', 'N/A')}")
        elif check_name == "empty_lines" and check_result.get("found"):
            issues.append(f"Consecutive empty lines: {check_result.get('message', 'N/A')}")
        elif check_name == "figures" and check_result.get("found"):
            issues.append(f"Figure empty lines: {check_result.get('message', 'N/A')}")
        elif check_name == "captions" and check_result.get("found"):
            issues.append(f"Caption alignment: {check_result.get('message', 'N/A')}")
        elif check_name == "references" and check_result.get("found"):
            issues.append(f"References: {check_result.get('message', 'N/A')}")
        elif check_name == "chinese_spacing" and check_result.get("found"):
            issues.append(f"Chinese spacing: {check_result.get('message', 'N/A')}")
        elif check_name == "chinese_quotes" and check_result.get("found"):
            issues.append(f"Chinese quotes: {check_result.get('message', 'N/A')}")

    if issues:
        print()
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print()
        print("✓ All format checks passed!")

    print("=" * 80)

    if not args.no_report:
        print()
        print("Generating markdown report...")
        try:
            headers_result = results.get("headers", {})
            footers_result = results.get("footers", {})
            headers = headers_result.get("headers", []) if headers_result else []
            footers = footers_result.get("footers", []) if footers_result else []
            consistency = headers_result.get("consistency", {}) if headers_result else {}
            footer_consistency = footers_result.get("consistency", {}) if footers_result else {}

            # Ensure structure has required keys
            if structure is None:
                structure = {'headers': [], 'footers': []}
            elif 'headers' not in structure:
                structure['headers'] = []
            elif 'footers' not in structure:
                structure['footers'] = []

            md_report = generate_markdown_report(
                docx_path,
                structure,
                headers,
                footers,
                consistency,
                footer_consistency,
                results.get("empty_lines", {}),
                results.get("figures", {}),
                results.get("captions", {}),
                results.get("references", {}),
                results.get("chinese_spacing", {}),
                results.get("chinese_quotes", {}),
                checks_to_run=checks_to_run,
            )

            report_path = docx_path.parent / f"{docx_path.stem}_格式检查报告.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(md_report)
            print(f"✓ Markdown report saved to: {report_path}")
        except Exception as e:
            print(f"✗ Error saving markdown report: {e}")


if __name__ == "__main__":
    main()
