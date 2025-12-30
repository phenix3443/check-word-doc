#!/usr/bin/env python3
"""
Main entry point for document format checking.
"""

from pathlib import Path
import sys

from structure import analyze_document_structure
from header_footer import (
    analyze_header_footer_usage,
    extract_headers_from_docx,
    extract_footers_from_docx,
    check_header_consistency,
    check_footer_consistency
)
from empty_lines import check_consecutive_empty_lines
from figure import check_figure_empty_lines, check_caption_alignment
from report import generate_markdown_report


def main():
    if len(sys.argv) < 2:
        print("Error: Please provide the document path as a command line argument")
        print("Usage: python3 check.py <docx_path>")
        sys.exit(1)

    docx_path = Path(sys.argv[1])

    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        sys.exit(1)

    print("=" * 80)
    print(f"Checking document format: {docx_path.name}")
    print("=" * 80)
    print()

    print("1. Analyzing document structure...")
    structure = analyze_document_structure(docx_path)
    print(f"   Found {len(structure['headers'])} header file(s)")
    print(f"   Found {len(structure['footers'])} footer file(s)")
    print()

    print("2. Analyzing header/footer usage...")
    usage_info = analyze_header_footer_usage(docx_path)
    print()

    print("3. Extracting headers...")
    headers = extract_headers_from_docx(docx_path, usage_info)
    print(f"   Extracted {len(headers)} header(s) with content")
    print()

    if headers:
        print("   Header details:")
        for i, header in enumerate(headers, 1):
            print(f"   Header {i} ({header['file']}):")
            print(f"      Content: {header['text'][:100]}..." if len(header['text']) > 100 else f"      Content: {header['text']}")
            if header.get('page_info'):
                page_ranges = []
                for info in header['page_info']:
                    page_ranges.append(f"Page ~{info['estimated_start_page']} (Section {info['section']}, Para {info['start_para']})")
                if page_ranges:
                    print(f"      Location: {', '.join(page_ranges)}")
            print()

    print("4. Checking header consistency...")
    consistency = check_header_consistency(headers)
    print(f"   Result: {consistency['message']}")

    if not consistency['consistent']:
        print()
        print("   WARNING: Headers are not consistent!")
        if 'variations' in consistency:
            print("   Header variations found:")
            for header_text, count in consistency['variations'].items():
                print(f"      - '{header_text[:80]}...' (appears {count} time(s))" if len(header_text) > 80 else f"      - '{header_text}' (appears {count} time(s))")
    else:
        print("   ✓ Headers are consistent")

    print()
    print("5. Extracting footers...")
    footers = extract_footers_from_docx(docx_path, usage_info)
    print(f"   Extracted {len(footers)} footer(s) with content")
    print()

    if footers:
        print("   Footer details:")
        for i, footer in enumerate(footers, 1):
            print(f"   Footer {i} ({footer['file']}):")
            print(f"      Content: {footer['text'][:100]}..." if len(footer['text']) > 100 else f"      Content: {footer['text']}")
            if footer.get('page_info'):
                page_ranges = []
                for info in footer['page_info']:
                    page_ranges.append(f"Page ~{info['estimated_start_page']} (Section {info['section']}, Para {info['start_para']})")
                if page_ranges:
                    print(f"      Location: {', '.join(page_ranges)}")
            print()

    print("6. Checking footer consistency...")
    footer_consistency = check_footer_consistency(footers)
    print(f"   Result: {footer_consistency['message']}")

    if not footer_consistency['consistent']:
        print()
        print("   WARNING: Footers are not consistent!")
        if 'variations' in footer_consistency:
            print("   Footer variations found:")
            for footer_text, count in footer_consistency['variations'].items():
                print(f"      - '{footer_text[:80]}...' (appears {count} time(s))" if len(footer_text) > 80 else f"      - '{footer_text}' (appears {count} time(s))")
    else:
        print("   ✓ Footers are consistent")

    print()
    print("7. Checking for consecutive empty lines...")
    empty_lines_check = check_consecutive_empty_lines(docx_path)
    print(f"   Result: {empty_lines_check['message']}")

    if empty_lines_check['found']:
        print()
        print("   WARNING: Consecutive empty lines found!")
        if empty_lines_check['details']:
            details = empty_lines_check['details']
            print(f"   Found {len(details)} group(s) of consecutive empty lines")
            if len(details) > 20:
                print("   First 10 locations:")
                for detail in details[:10]:
                    page_info = ""
                    if 'estimated_start_page' in detail and 'estimated_end_page' in detail:
                        if detail['estimated_start_page'] == detail['estimated_end_page']:
                            page_info = f" (Page ~{detail['estimated_start_page']})"
                        else:
                            page_info = f" (Pages ~{detail['estimated_start_page']}-{detail['estimated_end_page']})"
                    print(f"      - Paragraphs {detail['start']} to {detail['end']}: {detail['count']} consecutive empty lines{page_info}")
                print("   ...")
                print("   Last 10 locations:")
                for detail in details[-10:]:
                    page_info = ""
                    if 'estimated_start_page' in detail and 'estimated_end_page' in detail:
                        if detail['estimated_start_page'] == detail['estimated_end_page']:
                            page_info = f" (Page ~{detail['estimated_start_page']})"
                        else:
                            page_info = f" (Pages ~{detail['estimated_start_page']}-{detail['estimated_end_page']})"
                    print(f"      - Paragraphs {detail['start']} to {detail['end']}: {detail['count']} consecutive empty lines{page_info}")
            else:
                print("   Locations:")
                for detail in details:
                    page_info = ""
                    if 'estimated_start_page' in detail and 'estimated_end_page' in detail:
                        if detail['estimated_start_page'] == detail['estimated_end_page']:
                            page_info = f" (Page ~{detail['estimated_start_page']})"
                        else:
                            page_info = f" (Pages ~{detail['estimated_start_page']}-{detail['estimated_end_page']})"
                    print(f"      - Paragraphs {detail['start']} to {detail['end']}: {detail['count']} consecutive empty lines{page_info}")
    else:
        print("   ✓ No consecutive empty lines found")

    if 'total_paragraphs' in empty_lines_check:
        print(f"   Total paragraphs in document: {empty_lines_check['total_paragraphs']}")

    print()
    print("8. Checking figure empty lines...")
    figure_check = check_figure_empty_lines(docx_path)
    print(f"   Result: {figure_check['message']}")

    if figure_check['found']:
        print()
        print("   WARNING: Figures with empty lines before or after found!")
        if figure_check['details']:
            details = figure_check['details']
            print(f"   Found {len(details)} figure(s) with empty lines")
            if len(details) > 20:
                print("   First 10 locations:")
                for detail in details[:10]:
                    before = "Yes" if detail['before_empty'] else "No"
                    after = "Yes" if detail['after_empty'] else "No"
                    print(f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): Before={before}, After={after}")
                print("   ...")
            else:
                print("   Locations:")
                for detail in details:
                    before = "Yes" if detail['before_empty'] else "No"
                    after = "Yes" if detail['after_empty'] else "No"
                    print(f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): Before={before}, After={after}")
    else:
        print("   ✓ No figures with empty lines before or after found")

    print()
    print("9. Checking caption alignment...")
    caption_check = check_caption_alignment(docx_path)
    print(f"   Result: {caption_check['message']}")

    if caption_check['found']:
        print()
        print("   WARNING: Captions not centered found!")
        if caption_check['details']:
            details = caption_check['details']
            print(f"   Found {len(details)} caption(s) not centered")
            if len(details) > 20:
                print("   First 10 locations:")
                for detail in details[:10]:
                    alignment_map = {
                        'left': 'Left',
                        'right': 'Right',
                        'justify': 'Justify',
                        'center': 'Center'
                    }
                    alignment_text = alignment_map.get(detail['alignment'], detail['alignment'])
                    print(f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['type']} - {alignment_text}")
                print("   ...")
            else:
                print("   Locations:")
                for detail in details:
                    alignment_map = {
                        'left': 'Left',
                        'right': 'Right',
                        'justify': 'Justify',
                        'center': 'Center'
                    }
                    alignment_text = alignment_map.get(detail['alignment'], detail['alignment'])
                    print(f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['type']} - {alignment_text}")
    else:
        print("   ✓ All captions are centered")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Header consistency: {'✓ PASS' if consistency['consistent'] else '✗ FAIL'}")
    print(f"Footer consistency: {'✓ PASS' if footer_consistency['consistent'] else '✗ FAIL'}")
    print(f"Consecutive empty lines: {'✓ PASS' if not empty_lines_check['found'] else '✗ FAIL'}")
    print(f"Figure empty lines: {'✓ PASS' if not figure_check['found'] else '✗ FAIL'}")
    print(f"Caption alignment: {'✓ PASS' if not caption_check['found'] else '✗ FAIL'}")

    issues = []
    if not consistency['consistent']:
        issues.append(f"Headers: {consistency['message']}")
    if not footer_consistency['consistent']:
        issues.append(f"Footers: {footer_consistency['message']}")
    if empty_lines_check['found']:
        issues.append(f"Consecutive empty lines: {empty_lines_check['message']}")
    if figure_check['found']:
        issues.append(f"Figure empty lines: {figure_check['message']}")
    if caption_check['found']:
        issues.append(f"Caption alignment: {caption_check['message']}")

    if issues:
        print()
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print()
        print("✓ All format checks passed!")

    print("=" * 80)

    print()
    print("Generating markdown report...")
    md_report = generate_markdown_report(docx_path, structure, headers, footers, consistency, footer_consistency, empty_lines_check, figure_check, caption_check)

    report_path = docx_path.parent / f"{docx_path.stem}_格式检查报告.md"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        print(f"✓ Markdown report saved to: {report_path}")
    except Exception as e:
        print(f"✗ Error saving markdown report: {e}")


if __name__ == '__main__':
    main()

