#!/usr/bin/env python3
"""
Check figure caption format consistency in Word document.
"""

import sys
from pathlib import Path
from figure import check_figure_caption_format


def main():
    if len(sys.argv) < 2:
        print("Error: Please provide the document path as a command line argument")
        print("Usage: python3 figure_format.py <docx_path>")
        sys.exit(1)

    docx_path = Path(sys.argv[1])

    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        sys.exit(1)

    print("=" * 80)
    print(f"Checking figure caption format: {docx_path.name}")
    print("=" * 80)
    print()

    result = check_figure_caption_format(docx_path)

    print(f"Result: {result['message']}")
    print()

    if result["format_patterns"]:
        print("Format patterns found:")
        for pattern, captions in sorted(
            result["format_patterns"].items(), key=lambda x: -len(x[1])
        ):
            print(f"  - '{pattern}': {len(captions)} caption(s)")
        print()

    if result["found"]:
        print("WARNING: Inconsistent figure caption formats found!")
        print()
        if "most_common_pattern" in result:
            print(f"Most common format: '{result['most_common_pattern']}'")
            print()

        print("Inconsistent captions:")
        details = result["details"]
        if len(details) > 50:
            print(
                f"Showing first 25 and last 25 of {len(details)} inconsistent captions:"
            )
            print()
            print("First 25:")
            for detail in details[:25]:
                print(
                    f"  - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['text']}"
                )
            print()
            print("Last 25:")
            for detail in details[-25:]:
                print(
                    f"  - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['text']}"
                )
        else:
            for detail in details:
                print(
                    f"  - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['text']}"
                )
    else:
        print("All figure captions have consistent format!")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
